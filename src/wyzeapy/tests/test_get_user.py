"""
Integration test for get_user to inspect API response.

Run with credentials to see what data the API returns:
    python -m wyzeapy.tests.test_get_user

Set environment variables:
    WYZE_EMAIL - Your Wyze account email
    WYZE_PASSWORD - Your Wyze account password
    WYZE_KEY_ID - API key ID
    WYZE_API_KEY - API key

Note: This file uses 'run_' prefix instead of 'test_' to avoid
pytest auto-discovery. Run it manually as a script.
"""

import asyncio
import json
import os
import sys


async def run_get_user_test():
    """Test get_user and print raw response data."""
    from wyzeapy import Wyzeapy

    email = os.environ.get("WYZE_EMAIL")
    password = os.environ.get("WYZE_PASSWORD")
    key_id = os.environ.get("WYZE_KEY_ID")
    api_key = os.environ.get("WYZE_API_KEY")

    if not all([email, password, key_id, api_key]):
        print("Missing required environment variables:")
        print("  WYZE_EMAIL, WYZE_PASSWORD, WYZE_KEY_ID, WYZE_API_KEY")
        sys.exit(1)

    # Assert for type narrowing
    assert email is not None
    assert password is not None
    assert key_id is not None
    assert api_key is not None

    def get_2fa_code(auth_type: str) -> str:
        return input(f"Enter {auth_type} code: ")

    async with Wyzeapy(
        email, password, key_id, api_key, tfa_callback=get_2fa_code
    ) as wyze:
        print("Logged in successfully!")
        print()

        user = await wyze.get_user()

        print("=== WyzeUser (modeled fields) ===")
        print(f"  user_id: {user.user_id}")
        print(f"  notifications_enabled: {user.notifications_enabled}")
        print(f"  nickname: {user.nickname}")
        print(f"  logo_url: {user.logo_url}")
        print(f"  gender: {user.gender}")
        print(f"  birthdate: {user.birthdate}")
        print(f"  occupation: {user.occupation}")
        print(f"  height: {user.height} {user.height_unit}")
        print(f"  weight: {user.weight} {user.weight_unit}")
        print(f"  body_type: {user.body_type}")
        print(f"  create_time: {user.create_time}")
        print(f"  update_time: {user.update_time}")
        print(f"  subscription: {user.subscription}")
        print(f"  metadata: {user.metadata}")
        print(f"  is_voip_on: {user.is_voip_on}")
        print()

        # Show any additional properties not in our model
        known_fields = {
            "notification",
            "user_id",
            "nickname",
            "logo_url",
            "gender",
            "birthdate",
            "occupation",
            "height",
            "height_unit",
            "weight",
            "weight_unit",
            "body_type",
            "create_time",
            "update_time",
            "subscription",
            "metadata",
            "is_voip_on",
        }
        additional = {k: v for k, v in user.raw_data.items() if k not in known_fields}
        if additional:
            print("=== Additional Properties (not yet modeled) ===")
            print(json.dumps(additional, indent=2, default=str))
        else:
            print("=== All API fields are now modeled! ===")


if __name__ == "__main__":
    asyncio.run(run_get_user_test())
