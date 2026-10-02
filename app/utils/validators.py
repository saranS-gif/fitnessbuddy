import re
from typing import Tuple


def validate_email(email: str) -> bool:
    """Validate format of an email address."""
    pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
    return bool(re.match(pattern, email.strip()))


def validate_password_strength(password: str) -> Tuple[bool, str]:
    """Ensure password meets minimum length requirements."""
    if len(password) < 6:
        return False, "Password must be at least 6 characters long."
    return True, ""
