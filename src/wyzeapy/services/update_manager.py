from asyncio import sleep
from dataclasses import dataclass, field
from heapq import heappush, heappop
from typing import Any
from math import ceil
from ..types import Device
import logging
import threading

"""
Asynchronous device update scheduling and management.

This module provides classes to schedule and execute periodic updates of
Wyze devices, ensuring rate limits and fair distribution of update calls.
"""

_LOGGER = logging.getLogger(__name__)

INTERVAL = 300
MAX_SLOTS = 225


@dataclass(order=True)
class DeviceUpdater(object):
    """Represents a scheduled update task for a single device.

    Attributes:
        service: The service instance responsible for updating the device.
        device: The Device object to be updated.
        update_in: Countdown ticks until the next update is due.
        updates_per_interval: Number of updates allowed per INTERVAL.
    """

    device: Device = field(compare=False)
    service: Any = field(compare=False)
    update_in: int  # Countdown ticks until this device should be updated
    updates_per_interval: int = field(compare=False)

    def __init__(self, service, device: Device, update_interval: int):
        """
        This function initializes a DeviceUpdater object
        :param service: The WyzeApy service connected to a device
        :param device: A WyzeApy device that needs to be in the update que
        :param update_interval: How many seconds should be targeted between updates. **Note this value may shift based on 1 call per sec and load.
        """
        self.service = service
        self.device = device
        self.update_in = 0  # Always initialize at 0 so that we get the first update ASAP. The items will shift based on priority after this.
        self.updates_per_interval = ceil(INTERVAL / update_interval)

    async def update(self, mutex: threading.Lock):
        # We only want to update if the update_in counter is zero
        if self.update_in <= 0:
            _LOGGER.debug("Updating device: " + self.device.nickname)
            # Acquire the mutex before making the async call
            mutex.acquire()
            try:
                # Get the updated info for the device from Wyze's API
                self.device = await self.service.update(self.device)
                # Callback to provide the updated info to the subscriber
                self.device.callback_function(self.device)
            except Exception:
                _LOGGER.exception("Unknown error happened during updating device info")
            finally:
                # Release the mutex after the async call
                mutex.release()
            # Once it reaches zero and we update the device we want to reset the update_in counter
            self.update_in = ceil(INTERVAL / self.updates_per_interval)
        else:
            # Don't update and instead just reduce the counter by 1
            self.tick_tock()

    def tick_tock(self):
        # Every time we update a device we want to reduce the update_in counter so that it will get closer to updating
        if self.update_in > 0:
            self.update_in -= 1

    def delay(self):
        # This should be called to reduce the number of updates per interval so that new devices can be added into the queue fairly
        if self.updates_per_interval > 1:
            self.updates_per_interval -= 1


class UpdateManager:
    """Manager for scheduling and executing periodic device updates.

    Maintains a priority queue of DeviceUpdater instances and enforces rate
    limits and fair distribution of update calls across devices.
    """

    updaters = []
    removed_updaters = []
    mutex = threading.Lock()

    def check_if_removed(self, updater: DeviceUpdater):
        for item in self.removed_updaters:
            if updater is item:
                return True
        return False

    # This function should be called once every second
    async def update_next(self):
        # If there are no updaters in the queue we don't need to do anything
        if len(self.updaters) == 0:
            _LOGGER.debug("No devices to update in queue")
            return
        while True:
            # First we get the next updater off the queue
            updater = heappop(self.updaters)
            # if the updater has been removed, pop the next and clear it from the removed updaters
            if self.removed_updaters:
                while self.check_if_removed(updater):
                    self.removed_updaters.remove(updater)
                    updater = heappop(self.updaters)
            # We then reduce the counter for all the other updaters
            self.tick_tock()
            # Then we update the target device
            await updater.update(
                self.mutex
            )  # It will only update if it is time for it to update. Otherwise it just reduces its update_in counter.
            # Then we put it back at the end of the queue. Or the front again if it wasn't ready to update
            heappush(self.updaters, updater)
            await sleep(1)

    def filled_slots(self):
        # This just returns the number of available slots
        current_slots = 0
        for a_updater in self.updaters:
            current_slots += a_updater.updates_per_interval

        return current_slots

    def decrease_updates_per_interval(self):
        # This will add a delay for all devices so we can squeeze more in there
        for a_updater in self.updaters:
            a_updater.delay()

    def tick_tock(self):
        # This will reduce the update_in counter for all devices
        for a_updater in self.updaters:
            a_updater.tick_tock()

    def add_updater(self, updater: DeviceUpdater):
        if len(self.updaters) >= MAX_SLOTS:
            _LOGGER.exception("No more devices can be updated within the rate limit")
            raise Exception("No more devices can be updated within the rate limit")

        # When we add a new updater it has to fit within the max slots or we will not add it
        while (self.filled_slots() + updater.updates_per_interval) > MAX_SLOTS:
            _LOGGER.debug(
                "Reducing updates per interval to fit new device as slots are full: %s",
                self.filled_slots(),
            )
            # If we are overflowing the available slots we will reduce the frequency of updates evenly for all devices until we can fit in one more.
            self.decrease_updates_per_interval()
            updater.delay()

        # Once it fits we will add the new updater to the queue
        heappush(self.updaters, updater)

    def del_updater(self, updater: DeviceUpdater):
        self.removed_updaters.append(updater)
        _LOGGER.debug("Removing device from update queue")
