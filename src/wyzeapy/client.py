#  Copyright (c) 2021. Mulliken, LLC - All Rights Reserved
#  You may use, distribute and modify this code under the terms
#  of the attached license. You should have received a copy of
#  the license with this file. If not, please write to:
#  joshua@mulliken.net to receive a copy

import re

from .base_client import BaseClient, Device, DeviceTypes, ActionNotSupported, PropertyIDs


class Client:
    def __init__(self, email, password):
        self.email = email
        self.password = password

        self.client = BaseClient()
        self.client.login(self.email, self.password)

    def reauthenticate(self):
        self.client.login(self.email, self.password)

    @staticmethod
    def create_pid_pair(pid_enum: PropertyIDs, value):
        return {"pid": pid_enum.value, "pvalue": value}

    def get_devices(self):
        object_list = self.client.get_object_list()

        devices = []
        for device in object_list['data']['device_list']:
            devices.append(Device(device))

        return devices

    def turn_on(self, device: Device, extra_pids=None):
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
        else:
            raise ActionNotSupported(device_type.value)

    def turn_off(self, device: Device, extra_pids=None):
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
        else:
            raise ActionNotSupported(device_type.value)

    def set_brightness(self, device: Device, brightness: int):
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

    def set_color(self, device, rgb_hex_string):
        if DeviceTypes(device.product_type) not in [
            DeviceTypes.MESH_LIGHT
        ]:
            raise ActionNotSupported(device.product_type)

        if len(rgb_hex_string) != 6 or bool(re.compile(r'[^A-F0-9]').search(rgb_hex_string)):
            raise AttributeError("Value must be a valid hex string in the format: 000000-FFFFFF")

        self.turn_on(device, extra_pids=[
            self.create_pid_pair(PropertyIDs.COLOR, rgb_hex_string)
        ])

    def get_info(self, device):
        properties = self.client.get_property_list(device)['data']['device_list'][0]['device_property_list']

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
