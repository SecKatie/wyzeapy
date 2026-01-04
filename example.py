"""Example script demonstrating Wyzeapy usage and dumping raw API data."""

import asyncio
import json
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

        # Group devices by type
        by_type: dict[str, list] = {}
        for device in devices:
            type_name = device.product_type or "Unknown"
            by_type.setdefault(type_name, []).append(device)

        for product_type, type_devices in sorted(by_type.items()):
            print(f"\n{'='*60}")
            print(f"Product Type: {product_type} ({len(type_devices)} devices)")
            print(f"{'='*60}")

            for device in type_devices:
                print(f"\n--- {device.nickname} ({device.mac}) ---")
                print(f"  Class: {device.__class__.__name__}")
                print(f"  Model: {device.product_model}")
                print(f"  Firmware: {device.firmware_ver}")
                print(f"  Hardware: {device.hardware_ver}")
                print(f"  Available: {device.available}")
                print(f"  Parent MAC: {device.parent_device_mac}")

                # Dump raw device data
                raw = device.raw_device.to_dict()
                print(f"\n  Raw device fields:")
                for key, value in sorted(raw.items()):
                    if key != "device_params":
                        print(f"    {key}: {value!r}")

                # Dump device_params separately for readability
                if device.device_params:
                    print(f"\n  Device params:")
                    for key, value in sorted(device.device_params.items()):
                        print(f"    {key}: {value!r}")

                # Show any additional properties from the raw model
                if device.raw_device.additional_properties:
                    print(f"\n  Additional properties:")
                    for key, value in sorted(device.raw_device.additional_properties.items()):
                        # Truncate long values
                        val_str = repr(value)
                        if len(val_str) > 100:
                            val_str = val_str[:100] + "..."
                        print(f"    {key}: {val_str}")


if __name__ == "__main__":
    asyncio.run(main())
