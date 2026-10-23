<!--
SPDX-FileCopyrightText: 2021 Mulliken, LLC <katie@mulliken.net>

SPDX-License-Identifier: GPL-3.0-only
-->

# Wyzeapy

A Python library for the (unofficial) Wyze Labs web APIs.

## Used By

This project is used by the [ha-wyzeapi](https://github.com/SecKatie/ha-wyzeapi) project.  Let me know if you are utilizing it so that I can feature your project here!

## Usage/Examples

Getting logged in:

```python
import asyncio
from wyzeapy import Wyzeapy


async def async_main():
    client = await Wyzeapy.create()
    await client.login(email="EMAIL", password="PASSWORD", key_id="KEY_ID", api_key="API_KEY")


if __name__ == "__main__":
    asyncio.run(async_main())
```
Note: Visit the [Wyze developer console](https://developer-api-console.wyze.com/#/apikey/view) to generate an Key Id and Api Key.

### Account ownership (staged for 0.9.0)

Use one client per exact username and event loop. Obtain services from that
client so they share authentication, inventory, the parameter cache and legacy
update coordination. Separate clients have separate state, even when devices
have the same identifiers. Standalone service constructors remain usable but
create independent contexts; use the client properties to share state.

Same-username `login(...)` retries keep existing services connected to one auth
owner. Failed or cancelled attempts preserve the last successful token. Finish
MFA with `await client.login_with_2fa(code)` on the client that started it. A new
login invalidates its previous challenge. Service operations raise `RuntimeError`
until login/MFA finishes; changing username requires a new client.

For existing automatic updates, register devices and start the owning manager:

```python
service = await client.bulb_service
service.register_updater(device, 30)
await service.start_update_manager()
```

Ownerless `await BaseService.start_update_manager()` raises `RuntimeError`.
These restrictions are intended for the breaking 0.9.0 release, not 0.8.x.
This slice retains per-request sessions and existing polling intervals. It does
not yet provide client shutdown or complete HA account isolation. Consumer-owned
polling remains the eventual direction.

## Thanks to:

- [@shauntarves](https://github.com/shauntarves): for contributing the App ID and Signing Secret
- [@yoinx](https://github.com/yoinx): for considerable contributions to the project


## License

[GNU GPLv3](https://choosealicense.com/licenses/gpl-3.0/)

## Author

Developed by Katie Mulliken ([SecKatie](https://github.com/SecKatie))

## Appendix

### Testing

Run the complete pytest suite, including unittest cases, with `coverage` for
coverage reporting. Its HTTP guard permits only controlled loopback endpoints.

#### Prerequisites

First, install the development dependencies:

```bash
uv sync --group dev
```

#### Running Tests

**Run all tests:**
```bash
.venv/bin/python -m pytest tests
```

**Run tests with verbose output:**
```bash
.venv/bin/python -m pytest tests -v
```

**Run a specific test file:**
```bash
.venv/bin/python -m unittest tests.test_camera_service
```

**Run a specific test method:**
```bash
.venv/bin/python -m unittest tests.test_camera_service.TestCameraService.test_get_cameras
```

#### Code Coverage

**Run tests with coverage:**
```bash
.venv/bin/coverage run -m pytest tests
```

**View coverage report in terminal:**
```bash
.venv/bin/coverage report -m
```

**Generate HTML coverage report:**
```bash
.venv/bin/coverage html
```

Then open `htmlcov/index.html` in your web browser to view the detailed coverage report.

**One-liner to run tests and view coverage:**
```bash
.venv/bin/coverage run -m pytest tests && .venv/bin/coverage report -m
```

### Documentation

Docs are generated using [pdoc](https://pdoc.dev/). To generate docs for this project, run:

```bash
# Install development dependencies
uv sync --group dev

# Generate docs
uv run pdoc --output-dir=docs src/wyzeapy
```
