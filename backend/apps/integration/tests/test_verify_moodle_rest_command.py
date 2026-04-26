from io import StringIO
from json import JSONDecodeError
from unittest.mock import Mock

import pytest
import requests
from django.core.management import call_command
from django.core.management.base import CommandError


def build_response(*, payload=None, text="", status_code=200, json_error=None):
    response = Mock()
    response.status_code = status_code
    response.text = text
    response.raise_for_status.side_effect = None
    if status_code >= 400:
        response.raise_for_status.side_effect = requests.HTTPError(f"{status_code} error")

    if json_error is not None:
        response.json.side_effect = json_error
    else:
        response.json.return_value = payload
    return response


def test_verify_moodle_rest_requires_base_url(settings):
    settings.MOODLE_BASE_URL = ""
    settings.MOODLE_WS_TOKEN = "token"

    with pytest.raises(CommandError, match="MOODLE_BASE_URL"):
        call_command("verify_moodle_rest")


def test_verify_moodle_rest_requires_token(settings):
    settings.MOODLE_BASE_URL = "http://127.0.0.1:8090"
    settings.MOODLE_WS_TOKEN = ""

    with pytest.raises(CommandError, match="MOODLE_WS_TOKEN"):
        call_command("verify_moodle_rest")


def test_verify_moodle_rest_reports_connection_errors(settings, monkeypatch):
    settings.MOODLE_BASE_URL = "http://127.0.0.1:8090"
    settings.MOODLE_WS_TOKEN = "token"

    def fake_post(*args, **kwargs):
        raise requests.ConnectionError("refused")

    monkeypatch.setattr("requests.post", fake_post)

    with pytest.raises(CommandError, match="Could not reach Moodle REST endpoint"):
        call_command("verify_moodle_rest")


def test_verify_moodle_rest_reports_invalid_json(settings, monkeypatch):
    settings.MOODLE_BASE_URL = "http://127.0.0.1:8090"
    settings.MOODLE_WS_TOKEN = "token"

    response = build_response(
        text="<html>not json</html>",
        json_error=JSONDecodeError("Expecting value", "<html>not json</html>", 0),
    )
    monkeypatch.setattr("requests.post", lambda *args, **kwargs: response)

    with pytest.raises(CommandError, match="invalid JSON"):
        call_command("verify_moodle_rest")


def test_verify_moodle_rest_reports_moodle_exception_payload(settings, monkeypatch):
    settings.MOODLE_BASE_URL = "http://127.0.0.1:8090"
    settings.MOODLE_WS_TOKEN = "token"

    response = build_response(
        payload={
            "exception": "webservice_access_exception",
            "errorcode": "accessexception",
            "message": "Access control exception",
        }
    )
    monkeypatch.setattr("requests.post", lambda *args, **kwargs: response)

    with pytest.raises(CommandError, match="webservice_access_exception"):
        call_command("verify_moodle_rest")


def test_verify_moodle_rest_prints_success_summary(settings, monkeypatch):
    settings.MOODLE_BASE_URL = "http://127.0.0.1:8090"
    settings.MOODLE_WS_TOKEN = "token"
    stdout = StringIO()

    response = build_response(
        payload={
            "users": [
                {
                    "id": 2,
                    "username": "admin",
                    "firstname": "Site",
                    "lastname": "Administrator",
                }
            ],
            "warnings": [],
        }
    )
    post_mock = Mock(return_value=response)
    monkeypatch.setattr("requests.post", post_mock)

    call_command("verify_moodle_rest", stdout=stdout)

    post_mock.assert_called_once()
    _, kwargs = post_mock.call_args
    assert kwargs["timeout"] == 10
    assert kwargs["data"]["wsfunction"] == "core_user_get_users"
    assert kwargs["data"]["moodlewsrestformat"] == "json"
    assert kwargs["data"]["criteria[0][key]"] == "username"
    assert kwargs["data"]["criteria[0][value]"] == "admin"

    output = stdout.getvalue()
    assert "Moodle REST connectivity verified." in output
    assert "Matched 1 user(s)." in output
    assert "First match: admin (#2)" in output
