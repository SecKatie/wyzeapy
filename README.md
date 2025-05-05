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

### Documentation

Docs are generated using [pdoc](https://pdoc.dev/). To generate docs for this project, run:

```bash
# Activate the poetry environment (that includes the dev dependencies)
eval "$(poetry env activate)"

# Generate docs
pdoc --output-dir=docs src/wyzeapy
```

[Full doc reference](https://seckatie.github.io/wyzeapy/) - Please note that I am still working on doc strings so please be patient.

