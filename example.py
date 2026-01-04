#!/usr/bin/env uv run --script
"""Example script demonstrating Wyzeapy usage and dumping raw API data."""
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

        for device in devices:
            print(f"\n{'-'*60}")
            print(f"Device: {device.nickname}")
            print(f"{'-'*60}")
            print(f"  MAC: {device.mac}")
            print(f"  Type: {device.type.value}")
            print(f"  Product Model: {device.product_model}")
            print(f"  Available: {device.available}")

            # Get detailed device info
            info = await device.get_info()
            if info:
                print("\n  Device Info:")
                for key, value in info.items():
                    print(f"    {key}: {value}")

            # Get device properties
            properties = await device.get_properties()
            if properties:
                print("\n  Properties:")
                for pid, value in properties.items():
                    print(f"    {pid}: {value}")


if __name__ == "__main__":
    asyncio.run(main())
