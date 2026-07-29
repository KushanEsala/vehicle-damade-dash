from __future__ import annotations

from typing import Final


VISION_CREDENTIAL_SERVICE: Final = "ApexAssurance"
VISION_CREDENTIAL_ACCOUNT: Final = "server-vision-validator"


def get_vision_api_key() -> str | None:
    """Read the server-only vision credential from the operating-system vault."""
    try:
        import keyring

        value = keyring.get_password(VISION_CREDENTIAL_SERVICE, VISION_CREDENTIAL_ACCOUNT)
    except Exception:
        return None
    value = value.strip() if value else ""
    return value or None
