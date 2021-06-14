#  Copyright (c) 2021. Mulliken, LLC - All Rights Reserved
#  You may use, distribute and modify this code under the terms
#  of the attached license. You should have received a copy of
#  the license with this file. If not, please write to:
#  joshua@mulliken.net to receive a copy
import logging
import time

from typing import Any, Optional, List, Tuple, Iterable, Dict
from .base_client import NetClient
from .exceptions import ActionNotSupported, UnknownApiError
from .types import ThermostatProps, Device, DeviceTypes, PropertyIDs, Event, Group, HMSStatus, Sensor

_LOGGER = logging.getLogger(__name__)


class Client:
    _devices: Optional[List[Device]] = None

    def __init__(self, email: str, password: str):
        self._last_sensor_update = time.time()
        self._latest_sensors: List[Sensor] = []
        self._last_event_update: float = time.time()
        self._latest_events: Optional[List[Event]] = None
        self.email = email
        self.password = password

        self.net_client = NetClient()
        self._valid_login = self.net_client.login(self.email, self.password)

    @property
    def valid_login(self) -> bool:
        return self._valid_login

    def reauthenticate(self) -> None:
        self.net_client.login(self.email, self.password)

    @staticmethod
    def create_pid_pair(pid_enum: PropertyIDs, value: str) -> Dict[str, str]:
        return {"pid": pid_enum.value, "pvalue": value}

    def get_plugs(self) -> List[Device]:
        if self._devices is None:
            self._devices = self.get_devices()

        return [device for device in self._devices if device.type is DeviceTypes.PLUG or
                device.type is DeviceTypes.OUTDOOR_PLUG]

    def get_cameras(self) -> List[Device]:
        if self._devices is None:
            self._devices = self.get_devices()

        return [device for device in self._devices if device.type is DeviceTypes.CAMERA]

    def get_locks(self) -> List[Device]:
        if self._devices is None:
            self._devices = self.get_devices()

        return [device for device in self._devices if device.type is DeviceTypes.LOCK]

    def get_thermostats(self) -> List[Device]:
        if self._devices is None:
            self._devices = self.get_devices()

        return [device for device in self._devices if device.type is DeviceTypes.THERMOSTAT]

    def get_bulbs(self) -> List[Device]:
        if self._devices is None:
            self._devices = self.get_devices()

        return [device for device in self._devices if device.type is DeviceTypes.LIGHT or
                device.type is DeviceTypes.MESH_LIGHT]

    def get_sensors(self, force_update: bool = False) -> List[Sensor]:
        if self._devices is None or force_update is True:
            self._devices = self.get_devices()

        self._latest_sensors = [Sensor(device.raw_dict) for device in self._devices if
                                device.type is DeviceTypes.MOTION_SENSOR or
                                device.type is DeviceTypes.CONTACT_SENSOR]

        return self._latest_sensors

    def get_sensor_state(self, sensor: Sensor) -> Sensor:
        current_update_time = time.time()
        if current_update_time - self._last_sensor_update >= 5:
            self._latest_sensors = self.get_sensors(force_update=True)
            self._last_sensor_update = current_update_time

        for i in self._latest_sensors:
            if i.mac == sensor.mac:
                return i

        raise RuntimeError(f"Unable to find sensor with mac: {sensor.mac}")

    def get_devices(self) -> List[Device]:
        object_list = self.net_client.get_object_list()

        return [Device(device) for device in object_list['data']['device_list']]

    def get_groups(self) -> List[Group]:
        object_list = self.net_client.get_auto_group_list()

        return [Group(group) for group in object_list['data']['auto_group_list']]

    def activate_group(self, group: Group) -> None:
        self.net_client.auto_group_run(group)

    def turn_on(self, device: Device, extra_pids: Optional[Iterable[Dict[Any, Any]]] = None) -> None:
        device_type: DeviceTypes = DeviceTypes(device.product_type)

        if device_type in [
            DeviceTypes.PLUG,
            DeviceTypes.OUTDOOR_PLUG
        ]:
            self.net_client.set_property(device, PropertyIDs.ON.value, "1")
        elif device_type in [
            DeviceTypes.LIGHT
        ]:
            plist = [
                self.create_pid_pair(PropertyIDs.ON, "1")
            ]
            if extra_pids is not None:
                plist.extend(extra_pids)

            self.net_client.set_property_list(device, plist)
        elif device_type in [
            DeviceTypes.MESH_LIGHT
        ]:
            plist = [
                self.create_pid_pair(PropertyIDs.ON, "1")
            ]
            if extra_pids is not None:
                plist.extend(extra_pids)

            self.net_client.run_action_list(device, plist)
        elif device_type in [
            DeviceTypes.LOCK
        ]:
            self.net_client.lock_control(device, "remoteLock")
        elif device_type in [
            DeviceTypes.CAMERA
        ]:
            self.net_client.run_action(device, "power_on")
        else:
            raise ActionNotSupported(device_type.value)

    def turn_off(self, device: Device, extra_pids: Optional[Iterable[Dict[Any, Any]]] = None) -> None:
        device_type: DeviceTypes = DeviceTypes(device.product_type)

        if device_type in [
            DeviceTypes.PLUG,
            DeviceTypes.OUTDOOR_PLUG
        ]:
            self.net_client.set_property(device, PropertyIDs.ON.value, "0")
        elif device_type in [
            DeviceTypes.LIGHT
        ]:
            plist = [
                self.create_pid_pair(PropertyIDs.ON, "0")
            ]
            if extra_pids is not None:
                plist.extend(extra_pids)

            self.net_client.set_property_list(device, plist)
        elif device_type in [
            DeviceTypes.MESH_LIGHT
        ]:
            plist = [
                self.create_pid_pair(PropertyIDs.ON, "0")
            ]
            if extra_pids is not None:
                plist.extend(extra_pids)

            self.net_client.run_action_list(device, plist)
        elif device_type in [
            DeviceTypes.LOCK
        ]:
            self.net_client.lock_control(device, "remoteUnlock")
        elif device_type in [
            DeviceTypes.CAMERA
        ]:
            self.net_client.run_action(device, "power_off")
        else:
            raise ActionNotSupported(device_type.value)

    def get_info(self, device: Device) -> List[Tuple[PropertyIDs, Any]]:
        properties = self.net_client.get_property_list(device)['data']['property_list']

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

    def get_events(self, device: Device) -> List[Event]:
        raw_events = self.net_client.get_event_list(device, 10)['data']['event_list']

        events = []
        if len(raw_events) > 0:
            for raw_event in raw_events:
                event = Event(raw_event)
                events.append(event)

        return events

    def get_latest_event(self, device: Device) -> Optional[Event]:
        raw_events = self.net_client.get_event_list(device, 10)['data']['event_list']

        if len(raw_events) > 0:
            return Event(raw_events[0])

        return None

    def get_cached_latest_event(self, device: Device) -> Optional[Event]:
        if self._latest_events is not None and time.time() - self._last_event_update < 5:
            return self.return_event_for_device(device, self._latest_events)

        raw_events = self.net_client.get_full_event_list(10)['data']['event_list']

        self._latest_events = [Event(raw_event) for raw_event in raw_events]
        return self.return_event_for_device(device, self._latest_events)

    def return_event_for_device(self, device: Device, events: List[Event]) -> Optional[Event]:
        for event in events:
            if event.device_mac == device.mac:
                return event

        return None

    def get_thermostat_info(self, device: Device) -> List[Tuple[ThermostatProps, Any]]:
        if DeviceTypes(device.product_type) not in [
            DeviceTypes.THERMOSTAT
        ]:
            raise ActionNotSupported(device.product_type)

        properties = self.net_client.thermostat_get_iot_prop(device)['data']['props']

        device_props = []
        for property in properties:
            try:
                prop = ThermostatProps(property)
                device_props.append((prop, properties[property]))
            except ValueError as e:
                _LOGGER.debug(f"{e} with value {properties[property]}")

        return device_props

    def set_thermostat_prop(self, device: Device, prop: ThermostatProps, value: Any) -> None:
        if DeviceTypes(device.product_type) not in [
            DeviceTypes.THERMOSTAT
        ]:
            raise ActionNotSupported(device.product_type)

        self.net_client.thermostat_set_iot_prop(device, prop, value)

    def has_hms(self) -> bool:
        if self.net_client.get_hms_id() is None:
            return False

        return True

    def get_hms_info(self) -> HMSStatus:
        hms_id = self.net_client.get_hms_id()
        assert hms_id is not None
        status_response = self.net_client.monitoring_profile_state_status(hms_id)
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

    def set_hms_status(self, state: HMSStatus) -> None:
        hms_id = self.net_client.get_hms_id()
        assert hms_id is not None
        if state == HMSStatus.DISARMED:
            self.net_client.monitoring_profile_active(hms_id, 0, 0)
            self.net_client.disable_reme_alarm(hms_id)
        elif state == HMSStatus.HOME:
            self.net_client.monitoring_profile_active(hms_id, 1, 0)
        elif state == HMSStatus.AWAY:
            self.net_client.monitoring_profile_active(hms_id, 0, 1)
        else:
            raise AttributeError("Status must be one of HMSStatus values")
