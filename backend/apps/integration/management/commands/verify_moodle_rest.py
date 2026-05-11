from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

import requests


class Command(BaseCommand):
    help = "Verify Moodle REST connectivity with a narrow core_user_get_users call."

    def add_arguments(self, parser):
        parser.add_argument(
            "--username",
            default=settings.MOODLE_DEFAULT_USERNAME,
            help="Username criterion used for the core_user_get_users verification call.",
        )

    def handle(self, *args, **options):
        base_url = settings.MOODLE_BASE_URL
        token = settings.MOODLE_WS_TOKEN
        username = options["username"].strip() or settings.MOODLE_DEFAULT_USERNAME

        if not base_url:
            raise CommandError("MOODLE_BASE_URL is not configured.")
        if not token:
            raise CommandError("MOODLE_WS_TOKEN is not configured.")

        endpoint = f"{base_url}/webservice/rest/server.php"
        payload = {
            "wstoken": token,
            "wsfunction": "core_user_get_users",
            "moodlewsrestformat": "json",
            "criteria[0][key]": "username",
            "criteria[0][value]": username,
        }

        try:
            response = requests.post(endpoint, data=payload, timeout=10)
            response.raise_for_status()
        except requests.RequestException as exc:
            raise CommandError(f"Could not reach Moodle REST endpoint at {endpoint}: {exc}") from exc

        try:
            response_payload = response.json()
        except ValueError as exc:
            raise CommandError("Moodle REST endpoint returned invalid JSON.") from exc

        if not isinstance(response_payload, dict):
            raise CommandError("Moodle REST endpoint returned an unexpected payload shape.")

        if "exception" in response_payload:
            exception_name = response_payload.get("exception", "unknown_exception")
            error_code = response_payload.get("errorcode", "unknown_error")
            message = response_payload.get("message", "No Moodle error message was provided.")
            raise CommandError(f"Moodle REST returned {exception_name} ({error_code}): {message}")

        users = response_payload.get("users")
        if not isinstance(users, list):
            raise CommandError("Moodle REST response did not include a users list.")

        self.stdout.write(self.style.SUCCESS("Moodle REST connectivity verified."))
        self.stdout.write(f"Matched {len(users)} user(s).")
        if users:
            first_user = users[0]
            self.stdout.write(
                f"First match: {first_user.get('username', 'unknown')} (#{first_user.get('id', '?')})"
            )
