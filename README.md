
# Wyzeapy

A python library for the (unofficial) Wyze Labs web APIs.

## Used By

This project is used by the [ha-wyzeapi](https://github.com/JoshuaMulliken/ha-wyzeapi) project. Let me know if you are utilizing it so that I can feature your project here!

  
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


## License

[GNU GPLv3](https://choosealicense.com/licenses/gpl-3.0/)

  
## Appendix

[Full doc reference](https://joshuamulliken.github.io/wyzeapy/wyzeapy/)

  