#  Copyright (c) 2021. Mulliken, LLC - All Rights Reserved
#  You may use, distribute and modify this code under the terms
#  of the attached license. You should have received a copy of
#  the license with this file. If not, please write to:
#  joshua@mulliken.net to receive a copy
import logging
import re

from typing import Any, Optional, List, Tuple
from .base_client import BaseClient
from .exceptions import ActionNotSupported
from .types import ThermostatProps, Device, DeviceTypes, PropertyIDs, Event, Group

_LOGGER = logging.getLogger(__name__)

class Client:
    def __init__(self, email, password):
        self.email = email
        self.password = password

        self.client = BaseClient()
        self._valid_login = self.client.login(self.email, self.password)

    @property
    def valid_login(self):
        return self._valid_login

    def reauthenticate(self) -> None:
        self.client.login(self.email, self.password)

    @staticmethod
    def create_pid_pair(pid_enum: PropertyIDs, value) -> dict:
        return {"pid": pid_enum.value, "pvalue": value}

    def get_devices(self) -> List[Device]:
        object_list = self.client.get_object_list()

        devices = []
        for device in object_list['data']['device_list']:
            devices.append(Device(device))

        return devices

    def get_groups(self):
        object_list = self.client.get_auto_group_list()

        groups = []
        for group in object_list['data']['auto_group_list']:
            groups.append(Group(group))

        return groups

    def activate_group(self, group: Group):
        self.client.auto_group_run(group)

    def turn_on(self, device: Device, extra_pids=None) -> None:
        device_type: DeviceTypes = DeviceTypes(device.product_type)

        if device_type in [
            DeviceTypes.PLUG,
            DeviceTypes.OUTDOOR_PLUG
        ]:
            self.client.set_property(device, PropertyIDs.ON.value, "1")
        elif device_type in [
            DeviceTypes.LIGHT
        ]:
            plist = [
                self.create_pid_pair(PropertyIDs.ON, "1")
            ]
            if extra_pids is not None:
                plist.extend(extra_pids)

            self.client.set_property_list(device, plist)
        elif device_type in [
            DeviceTypes.MESH_LIGHT
        ]:
            plist = [
                self.create_pid_pair(PropertyIDs.ON, "1")
            ]
            if extra_pids is not None:
                plist.extend(extra_pids)

            self.client.run_action_list(device, plist)
        elif device_type in [
            DeviceTypes.LOCK
        ]:
            self.client.lock_control(device, "remoteLock")
        elif device_type in [
            DeviceTypes.CAMERA
        ]:
            self.client.run_action(device, "power_on")
        else:
            raise ActionNotSupported(device_type.value)

    def turn_off(self, device: Device, extra_pids=None) -> None:
        device_type: DeviceTypes = DeviceTypes(device.product_type)

        if device_type in [
            DeviceTypes.PLUG,
            DeviceTypes.OUTDOOR_PLUG
        ]:
            self.client.set_property(device, PropertyIDs.ON.value, "0")
        elif device_type in [
            DeviceTypes.LIGHT
        ]:
            plist = [
                self.create_pid_pair(PropertyIDs.ON, "0")
            ]
            if extra_pids is not None:
                plist.extend(extra_pids)

            self.client.set_property_list(device, plist)
        elif device_type in [
            DeviceTypes.MESH_LIGHT
        ]:
            plist = [
                self.create_pid_pair(PropertyIDs.ON, "0")
            ]
            if extra_pids is not None:
                plist.extend(extra_pids)

            self.client.run_action_list(device, plist)
        elif device_type in [
            DeviceTypes.LOCK
        ]:
            self.client.lock_control(device, "remoteUnlock")
        elif device_type in [
            DeviceTypes.CAMERA
        ]:
            self.client.run_action(device, "power_off")
        else:
            raise ActionNotSupported(device_type.value)

    def set_brightness(self, device: Device, brightness: int) -> None:
        if DeviceTypes(device.product_type) not in [
            DeviceTypes.LIGHT,
            DeviceTypes.MESH_LIGHT
        ]:
            raise ActionNotSupported(device.product_type)

        if brightness > 100 or brightness < 0:
            raise AttributeError("Value must be between 0 and 100")

        self.turn_on(device, extra_pids=[
            self.create_pid_pair(PropertyIDs.BRIGHTNESS, str(brightness))
        ])

    def set_color(self, device, rgb_hex_string) -> None:
        if DeviceTypes(device.product_type) not in [
            DeviceTypes.MESH_LIGHT
        ]:
            raise ActionNotSupported(device.product_type)

        if len(rgb_hex_string) != 6 or bool(re.compile(r'[^A-F0-9]').search(rgb_hex_string)):
            raise AttributeError("Value must be a valid hex string in the format: 000000-FFFFFF")

        self.turn_on(device, extra_pids=[
            self.create_pid_pair(PropertyIDs.COLOR, rgb_hex_string)
        ])

    def get_info(self, device) -> List[Tuple[PropertyIDs, Any]]:
        properties = self.client.get_property_list(device)['data']['property_list']

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

    def get_events(self, device) -> List[Event]:
        raw_events = self.client.get_event_list(device, 10)['data']['event_list']

        events = []
        if len(raw_events) > 0:
            for raw_event in raw_events:
                event = Event(raw_event)
                events.append(event)

        return events

    def get_latest_event(self, device) -> Optional[Event]:
        raw_events = self.client.get_event_list(device, 10)['data']['event_list']

        if len(raw_events) > 0:
            return Event(raw_events[0])

        return None

    def get_thermostat_info(self, device) -> List[Tuple[ThermostatProps, Any]]:
        if DeviceTypes(device.product_type) not in [
            DeviceTypes.THERMOSTAT
        ]:
            raise ActionNotSupported(device.product_type)

        properties = self.client.thermostat_get_iot_prop(device)['data']['props']

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

        self.client.thermostat_set_iot_prop(device, prop, value)
