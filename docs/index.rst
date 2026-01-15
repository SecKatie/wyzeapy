wyzeapy
=======

A Python library for interacting with Wyze smart home devices.

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   api/wyzeapy
   api/devices
   api/services

Installation
------------

.. code-block:: bash

   pip install wyzeapy

Quick Start
-----------

.. code-block:: python

   import asyncio
   from wyzeapy import Wyzeapy

   async def main():
       async with Wyzeapy("email@example.com", "password", "key_id", "api_key") as wyze:
           # Get all devices
           devices = await wyze.list_devices()
           for device in devices:
               print(f"{device.nickname}: {device.type.value}")

           # Control a light
           for device in devices:
               if hasattr(device, "set_brightness"):
                   await device.turn_on()
                   await device.set_brightness(75)

   asyncio.run(main())

With 2FA
---------

If your account has two-factor authentication enabled, provide a callback:

.. code-block:: python

   def get_2fa_code(auth_type: str) -> str:
       return input(f"Enter {auth_type} code: ")

   async with Wyzeapy(email, password, key_id, api_key,
                   tfa_callback=get_2fa_code) as wyze:
       devices = await wyze.list_devices()

Indices and tables
=====================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
