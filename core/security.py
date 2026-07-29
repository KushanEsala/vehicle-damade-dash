from __future__ import annotations

import re
import secrets
import string
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError, InvalidHashError

from core.exceptions import ValidationError

ph = PasswordHasher()


def hash_password(password: str) -> str:
    """Hashes a password using Argon2id."""
    return ph.hash(password)


def verify_password(hash_str: str, password: str) -> bool:
    """Verifies a plain password against an Argon2id hash."""
    if not hash_str or not password:
        return False
    try:
        return ph.verify(hash_str, password)
    except (VerifyMismatchError, InvalidHashError):
        return False


def validate_password_strength(password: str) -> None:
    """
    Validates password strength according to security policy:
    - Min 10 chars
    - Uppercase char
    - Lowercase char
    - Digit
    - Special symbol
    """
    if len(password) < 10:
        raise ValidationError("Password must be at least 10 characters long.")
    if not re.search(r"[A-Z]", password):
        raise ValidationError("Password must contain at least one uppercase letter.")
    if not re.search(r"[a-z]", password):
        raise ValidationError("Password must contain at least one lowercase letter.")
    if not re.search(r"[0-9]", password):
        raise ValidationError("Password must contain at least one number.")
    if not re.search(r"[^A-Za-z0-9]", password):
        raise ValidationError("Password must contain at least one symbol (e.g. !@#$%^&*).")


def generate_temporary_password(length: int = 12) -> str:
    """Generates a secure temporary password complying with complexity rules."""
    uppercase = secrets.choice(string.ascii_uppercase)
    lowercase = secrets.choice(string.ascii_lowercase)
    digit = secrets.choice(string.digits)
    symbol = secrets.choice("!@#$%^&*")
    all_chars = string.ascii_letters + string.digits + "!@#$%^&*"
    remainder = [secrets.choice(all_chars) for _ in range(length - 4)]
    combined = list(uppercase + lowercase + digit + symbol + "".join(remainder))
    secrets.SystemRandom().shuffle(combined)
    return "".join(combined)
