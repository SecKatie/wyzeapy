#!/usr/bin/env uv run --script
"""Example script demonstrating Wyzeapy usage and dumping raw API data."""
from typing import cast
from src.wyzeapy_v2 import DeviceType, WyzeCamera

import asyncio
import os

from src.wyzeapy_v2 import Wyzeapy


def get_2fa_code(auth_type: str) -> str:
    """Prompt user for 2FA code if needed."""
    return input(f"Enter {auth_type} verification code: ")


async def main():
    email = os.environ["WYZE_EMAIL"]
    password = os.environ["WYZE_PASSWORD"]
    key_id = os.environ["WYZE_KEY_ID"]
    api_key = os.environ["WYZE_API_KEY"]

    async with Wyzeapy(email, password, key_id, api_key, tfa_callback=get_2fa_code) as wyze:
        devices = await wyze.list_devices()

        print(f"\n{'='*60}")
        print(f"Found {len(devices)} devices")
        print(f"{'='*60}\n")

        # Let's get the cameras and print out their details
        cameras = [cast(WyzeCamera, device) for device in devices if device.type == DeviceType.CAMERA]
        for camera in cameras:
            print(f"Camera: {camera.nickname} ({camera.mac})")
            print(f"  Type: {camera.type}")
            print(f"  Is Available: {camera.available}")
            print(f"  Is On: {camera.is_on}")
            print(f"  Product Model: {camera.product_model}")
            print(f"  Product Type: {camera.product_type}")

            await camera.turn_on()

if __name__ == "__main__":
    asyncio.run(main())
