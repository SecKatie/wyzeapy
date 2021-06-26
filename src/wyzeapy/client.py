#  Copyright (c) 2021. Mulliken, LLC - All Rights Reserved
#  You may use, distribute and modify this code under the terms
#  of the attached license. You should have received a copy of
#  the license with this file. If not, please write to:
#  joshua@mulliken.net to receive a copy
import asyncio
import logging
import time
from asyncio import Task
from threading import Thread

from typing import Any, Optional, List, Tuple, Iterable, Dict
from .net_client import NetClient
from .exceptions import ActionNotSupported, UnknownApiError, AccessTokenError
from .types import ThermostatProps, Device, DeviceTypes, PropertyIDs, Event, Group, HMSStatus, Sensor

_LOGGER = logging.getLogger(__name__)

BLINK_TIME = 0.2  # The time it takes (in seconds) to ensure proper operation


class Client:
    _devices: Optional[List[Device]] = None
    _valid_login: bool

    def __init__(self, email: str, password: str):
        self._last_sensor_update = time.time()
        self._latest_sensors: List[Sensor] = []
        self._last_event_update: float = time.time()
        self._latest_events: Optional[List[Event]] = None
        self.email: str = email
        self.password: str = password
        self.sensor_update_interval: float = 5  # Initial time in seconds that a cached sensor value is assumed to be
        # fresh
        self.event_update_interval: float = 5  # Initial time in seconds that a cached event value is assumed to be
        # fresh
        self.previous_sensor_update_times: List[float] = []  # List that grows a max of 10 ints
        self.previous_event_update_times: List[float] = []  # List that grows a max of 10 ints

        # Locks
        self.sensor_lock = asyncio.Lock()
        self.event_lock = asyncio.Lock()

        self.net_client = NetClient()

    _event_task: Task
    _sensor_task: Task

    async def async_init(self):
        await self.net_client.async_init()

        self._valid_login = await self.net_client.login(self.email, self.password)

        event_loop = asyncio.get_event_loop()

        self._sensor_thread = Thread(target=self.sensor_update_worker, args=(event_loop,), daemon=True)
        self._sensor_thread.start()
        self._event_thread = Thread(target=self.event_update_worker, args=(event_loop,), daemon=True)
        self._event_thread.start()

    async def async_close(self):
        await self.net_client.async_close()

        self._event_thread.join(timeout=0)
        self._sensor_thread.join(timeout=0)

    @property
    def valid_login(self) -> bool:
        return self._valid_login

    async def reauthenticate(self) -> None:
        await self.net_client.login(self.email, self.password)

    @staticmethod
    def create_pid_pair(pid_enum: PropertyIDs, value: str) -> Dict[str, str]:
        return {"pid": pid_enum.value, "pvalue": value}

    async def get_plugs(self) -> List[Device]:
        if self._devices is None:
            self._devices = await self.get_devices()

        return [device for device in self._devices if device.type is DeviceTypes.PLUG or
                device.type is DeviceTypes.OUTDOOR_PLUG]

    async def get_cameras(self) -> List[Device]:
        if self._devices is None:
            self._devices = await self.get_devices()

        return [device for device in self._devices if device.type is DeviceTypes.CAMERA]

    async def get_locks(self) -> List[Device]:
        if self._devices is None:
            self._devices = await self.get_devices()

        return [device for device in self._devices if device.type is DeviceTypes.LOCK]

    async def get_thermostats(self) -> List[Device]:
        if self._devices is None:
            self._devices = await self.get_devices()

        return [device for device in self._devices if device.type is DeviceTypes.THERMOSTAT]

    async def get_bulbs(self) -> List[Device]:
        if self._devices is None:
            self._devices = await self.get_devices()

        return [device for device in self._devices if device.type is DeviceTypes.LIGHT or
                device.type is DeviceTypes.MESH_LIGHT]

    async def get_sensors(self, force_update: bool = False) -> List[Sensor]:
        if self._devices is None or force_update is True:
            self._devices = await self.get_devices()

        self._latest_sensors = [Sensor(device.raw_dict) for device in self._devices if
                                device.type is DeviceTypes.MOTION_SENSOR or
                                device.type is DeviceTypes.CONTACT_SENSOR]

        return self._latest_sensors

    async def get_sensor_state(self, sensor: Sensor) -> Sensor:
        _LOGGER.debug(f"Sensor: Getting latest")

        current_update_time = time.time()  # Time value to check if the current value is fresh

        if current_update_time - self._last_sensor_update >= self.sensor_update_interval:
            _LOGGER.debug(f"Sensor: Refreshing information")

            start_time = time.time()
            self._latest_sensors = await self.get_sensors(force_update=True)
            end_time = time.time()
            sensor_update_time = end_time - start_time
            self.previous_sensor_update_times.append(sensor_update_time)
            if len(self.previous_sensor_update_times) >= 11:
                self.previous_sensor_update_times.pop(0)

            self.sensor_update_interval = (sum(self.previous_sensor_update_times) / len(
                self.previous_sensor_update_times)) + BLINK_TIME  # Freshness calculation

            _LOGGER.debug(f"Sensor: Update interval: {self.sensor_update_interval}")

            self._last_sensor_update = current_update_time

        for i in self._latest_sensors:
            if i.mac == sensor.mac:
                return i

        raise RuntimeError(f"Unable to find sensor with mac: {sensor.mac}")

    _subscribers: List[Tuple[Any, Sensor]] = []

    async def register_for_sensor_updates(self, callback, sensor):
        if (callback, sensor) not in self._subscribers:
            self._subscribers.append((callback, sensor))

    def sensor_update_worker(self, loop):
        while True:
            try:
                _LOGGER.debug("Updating sensors")
                try:
                    sensors = asyncio.run_coroutine_threadsafe(self.get_sensors(force_update=True), loop).result()
                except AccessTokenError:
                    asyncio.run_coroutine_threadsafe(self.reauthenticate(), loop).result()
                    sensors = asyncio.run_coroutine_threadsafe(self.get_sensors(force_update=True), loop).result()

                for callback, sensor in self._subscribers:
                    for i in sensors:
                        if i.mac == sensor.mac:
                            _LOGGER.debug(f"Updating {i.mac}")
                            callback(i)
            except Exception as e:
                _LOGGER.error(e)

    def event_update_worker(self, loop):
        while True:
            try:
                _LOGGER.debug("Updating events")
                try:
                    response = asyncio.run_coroutine_threadsafe(self.net_client.get_full_event_list(10), loop).result()
                except AccessTokenError:
                    asyncio.run_coroutine_threadsafe(self.reauthenticate(), loop).result()
                    response = asyncio.run_coroutine_threadsafe(self.net_client.get_full_event_list(10), loop).result()

                raw_events = response['data']['event_list']
                latest_events = [Event(raw_event) for raw_event in raw_events]

                for callback, device in self._event_subscribers:
                    if (event := self.return_event_for_device(device, latest_events)) is not None:
                        _LOGGER.debug(f"Updating {device.mac}")
                        callback(event)
            except Exception as e:
                _LOGGER.error(e)

    async def register_for_event_updates(self, callback, device):
        if (callback, device) not in self._event_subscribers:
            self._event_subscribers.append((callback, device))

    async def get_devices(self) -> List[Device]:
        object_list: Dict[Any, Any] = await self.net_client.get_object_list()

        return [Device(device) for device in object_list['data']['device_list']]

    async def get_groups(self) -> List[Group]:
        object_list: Dict[Any, Any] = await self.net_client.get_auto_group_list()

        return [Group(group) for group in object_list['data']['auto_group_list']]

    async def activate_group(self, group: Group) -> None:
        await self.net_client.auto_group_run(group)

    async def turn_on(self, device: Device, extra_pids: Optional[Iterable[Dict[Any, Any]]] = None) -> None:
        device_type: DeviceTypes = DeviceTypes(device.product_type)

        if device_type in [
            DeviceTypes.PLUG,
            DeviceTypes.OUTDOOR_PLUG
        ]:
            await self.net_client.set_property(device, PropertyIDs.ON.value, "1")
        elif device_type in [
            DeviceTypes.LIGHT
        ]:
            plist = [
                self.create_pid_pair(PropertyIDs.ON, "1")
            ]
            if extra_pids is not None:
                plist.extend(extra_pids)

            await self.net_client.set_property_list(device, plist)
        elif device_type in [
            DeviceTypes.MESH_LIGHT
        ]:
            plist = [
                self.create_pid_pair(PropertyIDs.ON, "1")
            ]
            if extra_pids is not None:
                plist.extend(extra_pids)

            await self.net_client.run_action_list(device, plist)
        elif device_type in [
            DeviceTypes.LOCK
        ]:
            await self.net_client.lock_control(device, "remoteLock")
        elif device_type in [
            DeviceTypes.CAMERA
        ]:
            await self.net_client.run_action(device, "power_on")
        else:
            raise ActionNotSupported(device_type.value)

    async def turn_off(self, device: Device, extra_pids: Optional[Iterable[Dict[Any, Any]]] = None) -> None:
        device_type: DeviceTypes = DeviceTypes(device.product_type)

        if device_type in [
            DeviceTypes.PLUG,
            DeviceTypes.OUTDOOR_PLUG
        ]:
            await self.net_client.set_property(device, PropertyIDs.ON.value, "0")
        elif device_type in [
            DeviceTypes.LIGHT
        ]:
            plist = [
                self.create_pid_pair(PropertyIDs.ON, "0")
            ]
            if extra_pids is not None:
                plist.extend(extra_pids)

            await self.net_client.set_property_list(device, plist)
        elif device_type in [
            DeviceTypes.MESH_LIGHT
        ]:
            plist = [
                self.create_pid_pair(PropertyIDs.ON, "0")
            ]
            if extra_pids is not None:
                plist.extend(extra_pids)

            await self.net_client.run_action_list(device, plist)
        elif device_type in [
            DeviceTypes.LOCK
        ]:
            await self.net_client.lock_control(device, "remoteUnlock")
        elif device_type in [
            DeviceTypes.CAMERA
        ]:
            await self.net_client.run_action(device, "power_off")
        else:
            raise ActionNotSupported(device_type.value)

    async def get_info(self, device: Device) -> List[Tuple[PropertyIDs, Any]]:
        properties = (await self.net_client.get_property_list(device))['data']['property_list']

        property_list = []
        for property in properties:
            try:
                property_id = PropertyIDs(property['pid'])
                property_list.append((
                    property_id,
                    property['value']
                ))
            except ValueError:
                pass

        return property_list

    async def get_events(self, device: Device) -> List[Event]:
        raw_events = (await self.net_client.get_event_list(device, 10))['data']['event_list']

        events = []
        if len(raw_events) > 0:
            for raw_event in raw_events:
                event = Event(raw_event)
                events.append(event)

        return events

    _event_subscribers: List[Tuple[Any, Device]] = []

    async def get_latest_event(self, device: Device) -> Optional[Event]:
        raw_events = (await self.net_client.get_event_list(device, 10))['data']['event_list']

        if len(raw_events) > 0:
            return Event(raw_events[0])

        return None

    async def get_cached_latest_event(self, device: Device) -> Optional[Event]:
        _LOGGER.debug(f"Event: Getting latest")
        current_update_time = time.time()  # Time value to check if the current value is fresh

        if self._latest_events is None or current_update_time - self._last_event_update > self.event_update_interval:
            _LOGGER.debug(f"Event: Refreshing information")

            start_time = time.time()
            raw_events = (await self.net_client.get_full_event_list(10))['data']['event_list']
            self._latest_events = [Event(raw_event) for raw_event in raw_events]
            end_time = time.time()
            event_update_time = end_time - start_time
            self.previous_event_update_times.append(event_update_time)
            if len(self.previous_event_update_times) >= 11:
                self.previous_event_update_times.pop(0)

            self.event_update_interval = (sum(self.previous_event_update_times) / len(
                self.previous_event_update_times)) + BLINK_TIME  # Freshness calculation

            _LOGGER.debug(f"Event: Update interval: {self.event_update_interval}")

            self._last_event_update = current_update_time

            return self.return_event_for_device(device, self._latest_events)

        return self.return_event_for_device(device, self._latest_events)

    @staticmethod
    def return_event_for_device(device: Device, events: List[Event]) -> Optional[Event]:
        for event in events:
            if event.device_mac == device.mac:
                return event

        return None

    async def get_thermostat_info(self, device: Device) -> List[Tuple[ThermostatProps, Any]]:
        if DeviceTypes(device.product_type) not in [
            DeviceTypes.THERMOSTAT
        ]:
            raise ActionNotSupported(device.product_type)

        properties = (await self.net_client.thermostat_get_iot_prop(device))['data']['props']

        device_props = []
        for property in properties:
            try:
                prop = ThermostatProps(property)
                device_props.append((prop, properties[property]))
            except ValueError as e:
                _LOGGER.debug(f"{e} with value {properties[property]}")

        return device_props

    async def set_thermostat_prop(self, device: Device, prop: ThermostatProps, value: Any) -> None:
        if DeviceTypes(device.product_type) not in [
            DeviceTypes.THERMOSTAT
        ]:
            raise ActionNotSupported(device.product_type)

        await self.net_client.thermostat_set_iot_prop(device, prop, value)

    async def has_hms(self) -> bool:
        if await self.net_client.get_hms_id() is None:
            return False

        return True

    async def get_hms_info(self) -> HMSStatus:
        hms_id = await self.net_client.get_hms_id()
        assert hms_id is not None
        status_response = await self.net_client.monitoring_profile_state_status(hms_id)
        if status_response.get('status') == 200:
            status = status_response.get('message')
            if status == 'disarm':
                return HMSStatus.DISARMED
            elif status == 'home':
                return HMSStatus.HOME
            elif status == 'away':
                return HMSStatus.AWAY
            elif status == 'changing':
                return HMSStatus.DISARMED
            else:
                raise UnknownApiError(status_response)
        else:
            raise UnknownApiError(status_response)

    async def set_hms_status(self, state: HMSStatus) -> None:
        hms_id = await self.net_client.get_hms_id()
        assert hms_id is not None
        if state == HMSStatus.DISARMED:
            await self.net_client.monitoring_profile_active(hms_id, 0, 0)
            await self.net_client.disable_reme_alarm(hms_id)
        elif state == HMSStatus.HOME:
            await self.net_client.monitoring_profile_active(hms_id, 1, 0)
        elif state == HMSStatus.AWAY:
            await self.net_client.monitoring_profile_active(hms_id, 0, 1)
        else:
            raise AttributeError("Status must be one of HMSStatus values")
