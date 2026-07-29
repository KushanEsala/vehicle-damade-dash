from __future__ import annotations

import pytest
from core.security import hash_password, verify_password, validate_password_strength, generate_temporary_password
from core.exceptions import ValidationError


def test_password_hashing_and_verification():
    raw_pass = "SecurePass#123"
    h = hash_password(raw_pass)
    assert h.startswith("$argon2")
    assert verify_password(h, raw_pass) is True
    assert verify_password(h, "WrongPassword#123") is False


def test_password_strength_validation():
    with pytest.raises(ValidationError):
        validate_password_strength("short")

    with pytest.raises(ValidationError):
        validate_password_strength("lowercaseonly123!")

    with pytest.raises(ValidationError):
        validate_password_strength("UPPERCASEONLY123!")

    with pytest.raises(ValidationError):
        validate_password_strength("NoSymbols12345")

    # Valid password should not raise exception
    validate_password_strength("ValidPassword#123")


def test_temporary_password_generation():
    temp_p = generate_temporary_password(14)
    assert len(temp_p) == 14
    validate_password_strength(temp_p)
