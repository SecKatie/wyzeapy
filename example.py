#!/usr/bin/env uv run --script
"""Example script demonstrating Wyzeapy usage."""
import asyncio
import os

from wyzeapy import Wyzeapy, WyzeCamera, WyzeLock, WyzeLight, WyzePlug


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

        for device in devices:
            print(f"\n{'-'*60}")
            print(f"Device: {device.nickname}")
            print(f"{'-'*60}")
            print(f"  MAC: {device.mac}")
            print(f"  Type: {device.type.value}")
            print(f"  Product Model: {device.product_model}")
            print(f"  Available: {device.available}")

            # Device-specific info
            if isinstance(device, WyzeCamera):
                print(f"  Motion Detection: {device.motion_detection_enabled}")
                print(f"  Has Floodlight: {device.has_floodlight}")
                # For camera streaming, use docker-wyze-bridge:
                # https://github.com/mrlt8/docker-wyze-bridge

            elif isinstance(device, WyzeLock):
                print(f"  Is Locked: {device.is_locked}")

            elif isinstance(device, WyzeLight):
                print(f"  Is On: {device.is_on}")
                print(f"  Brightness: {device.brightness}")

            elif isinstance(device, WyzePlug):
                print(f"  Is On: {device.is_on}")


if __name__ == "__main__":
    asyncio.run(main())
