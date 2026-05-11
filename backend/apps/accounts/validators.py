from django.core.exceptions import ValidationError


class ComplexityPasswordValidator:
    def validate(self, password, user=None):
        messages: list[str] = []

        if not any(character.isupper() for character in password):
            messages.append("Password must contain at least one uppercase letter.")
        if not any(character.islower() for character in password):
            messages.append("Password must contain at least one lowercase letter.")
        if not any(character.isdigit() for character in password):
            messages.append("Password must contain at least one digit.")
        if password.isalnum():
            messages.append("Password must contain at least one special character.")

        if messages:
            raise ValidationError(messages)

    def get_help_text(self):
        return (
            "Your password must contain at least one uppercase letter, one lowercase "
            "letter, one digit, and one special character."
        )
