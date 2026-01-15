<!--
SPDX-FileCopyrightText: 2021 Mulliken, LLC <katie@mulliken.net>

SPDX-License-Identifier: GPL-3.0-only
-->

# Wyzeapy

A Python library for the (unofficial) Wyze Labs web APIs.

## Used By

This project is used by the [ha-wyzeapi](https://github.com/SecKatie/ha-wyzeapi) project.  Let me know if you are utilizing it so that I can feature your project here!

## Usage/Examples

### Basic Usage

```python
import asyncio
from wyzeapy import Wyzeapy

async def main():
    async with Wyzeapy("email@example.com", "password", "key_id", "api_key") as wyze:
        devices = await wyze.list_devices()
        for device in devices:
            print(f"{device.nickname}: {device.product_model}")

asyncio.run(main())
```

### With Two-Factor Authentication

```python
import asyncio
from wyzeapy import Wyzeapy

def get_2fa_code(auth_type: str) -> str:
    return input(f"Enter {auth_type} code: ")

async def main():
    async with Wyzeapy("email@example.com", "password", "key_id", "api_key", tfa_callback=get_2fa_code) as wyze:
        devices = await wyze.list_devices()
        for device in devices:
            print(f"{device.nickname}: {device.product_model}")

asyncio.run(main())
```

Note: Visit the [Wyze developer console](https://developer-api-console.wyze.com/#/apikey/view) to generate a Key ID and API Key.

## Thanks to:

 - [@shauntarves](https://github.com/shauntarves): for contributing the App ID and Signing Secret
 - [@yoinx](https://github.com/yoinx): for considerable contributions to the project

## TODO (High Priority Improvements)

- [x] Add type filtering to `list_devices()` - eliminate common boilerplate for getting specific device types
- [ ] Improve error messages with recovery guidance - provide actionable hints for authentication and device control failures
- [ ] Create comprehensive quick start examples - add examples for device control, thermostat, camera events, HMS, and irrigation
- [x] Add device discovery convenience methods (`wyze.get_lights()`, `wyze.get_locks()`, etc.) - matches mental models from other automation libraries
- [x] Create `docs/DEVELOPING.md` - documentation on how to add new device types, when to use MainApiMixin vs custom API calls, how to regenerate API client
- [ ] Add device test utilities/fixtures - create mock Device factories and mock context fixture for testing without real devices
- [x] Add runtime validation for device type mapping - warn when unknown product types are encountered instead of silently falling back to base `WyzeDevice`
- [x] Create abstraction for Unset checks - add utility function to reduce repetitive `isinstance(value, Unset)` checks across 12 files
- [ ] Improve test coverage for device control methods - add unit tests that mock the generated client instead of requiring real devices and credentials

## License

[GNU GPLv3](https://choosealicense.com/licenses/gpl-3.0/)

## Author

Developed by Katie Mulliken ([SecKatie](https://github.com/SecKatie))

## Appendix

### Testing

This project uses `pytest` for testing.

```bash
# Run all tests
just test

# Run unit tests only
just test-unit

# Run integration tests (requires credentials)
just test-integration
```

For integration tests, set these environment variables:

```bash
export WYZE_EMAIL="your_email"
export WYZE_PASSWORD="your_password"
export WYZE_KEY_ID="your_key_id"
export WYZE_API_KEY="your_api_key"
```

### Regenerating the API Client

The API client is generated from `wyze-api-openapi.yaml`:

```bash
just generate
```

### Documentation

Docs are generated using [pdoc](https://pdoc.dev/). To generate docs for this project, run:

```bash
# Install development dependencies
uv sync --group dev

# Generate docs
uv run pdoc --output-dir=docs src/wyzeapy
```
