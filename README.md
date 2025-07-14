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
    await client.login("EMAIL", "PASSWORD")


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(async_main())
```

## Thanks to:

- [@shauntarves](https://github.com/shauntarves): for contributing the App ID and Signing Secret
- [@yoinx](https://github.com/yoinx): for considerable contributions to the project


## License

[GNU GPLv3](https://choosealicense.com/licenses/gpl-3.0/)

## Author

Developed by Katie Mulliken ([SecKatie](https://github.com/SecKatie))

## Appendix

### Testing

This project uses Python's built-in `unittest` framework with `coverage` for code coverage reporting.

#### Prerequisites

First, install the development dependencies:

```bash
uv sync --group dev
```

#### Running Tests

**Run all tests:**
```bash
.venv/bin/python -m unittest discover tests
```

**Run tests with verbose output:**
```bash
.venv/bin/python -m unittest discover tests -v
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
.venv/bin/coverage run -m unittest discover tests
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
.venv/bin/coverage run -m unittest discover tests && .venv/bin/coverage report -m
```

### Documentation

Docs are generated using [pdoc](https://pdoc.dev/). To generate docs for this project, run:

```bash
# Install development dependencies
uv sync --group dev

# Generate docs
uv run pdoc --output-dir=docs src/wyzeapy
```
