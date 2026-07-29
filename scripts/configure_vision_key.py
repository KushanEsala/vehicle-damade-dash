from __future__ import annotations

import argparse
from getpass import getpass
from pathlib import Path
import sys

import httpx
import keyring

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from core.secret_store import VISION_CREDENTIAL_ACCOUNT, VISION_CREDENTIAL_SERVICE


def credential_is_valid(value: str) -> bool:
    try:
        response = httpx.get(
            "https://generativelanguage.googleapis.com/v1beta/models",
            headers={"x-goog-api-key": value},
            params={"pageSize": 1},
            timeout=15.0,
        )
        return response.status_code == 200
    except Exception:
        return False


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Manage the server-only visual validation credential.",
    )
    action = parser.add_mutually_exclusive_group()
    action.add_argument("--status", action="store_true", help="Report whether a credential is configured.")
    action.add_argument("--remove", action="store_true", help="Delete the saved credential.")
    args = parser.parse_args()

    if args.status:
        configured = bool(
            keyring.get_password(VISION_CREDENTIAL_SERVICE, VISION_CREDENTIAL_ACCOUNT)
        )
        print("Visual validation credential: configured" if configured else "Visual validation credential: not configured")
        return 0

    if args.remove:
        try:
            keyring.delete_password(VISION_CREDENTIAL_SERVICE, VISION_CREDENTIAL_ACCOUNT)
        except keyring.errors.PasswordDeleteError:
            pass
        print("Visual validation credential removed.")
        return 0

    first = getpass("Enter the Gemini API key (input is hidden): ").strip()
    if not first:
        print("No credential was entered. Nothing was changed.")
        return 1
    second = getpass("Enter the key again: ").strip()
    if first != second:
        print("The two entries did not match. Nothing was saved.")
        return 1
    print("Checking the credential without displaying or logging it...")
    if not credential_is_valid(first):
        print("The credential could not be verified. Nothing was saved.")
        print("Check the key, internet connection and Gemini API project access, then try again.")
        return 1

    keyring.set_password(VISION_CREDENTIAL_SERVICE, VISION_CREDENTIAL_ACCOUNT, first)
    print("Credential saved in the operating-system credential vault.")
    print("The next assessment will use the visual cross-check.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
