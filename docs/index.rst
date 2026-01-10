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
       client = await Wyzeapy.create()
       await client.login("email@example.com", "password")

       # Get all devices
       devices = await client.get_devices()
       for device in devices:
           print(device.nickname)

   asyncio.run(main())

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
