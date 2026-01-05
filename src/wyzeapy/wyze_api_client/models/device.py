from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.device_device_params import DeviceDeviceParams


T = TypeVar("T", bound="Device")


@_attrs_define
class Device:
    """
    Attributes:
        mac (str | Unset): Device MAC address
        product_type (str | Unset): Product type category
        product_model (str | Unset): Product model identifier
        nickname (str | Unset): User-defined device name
        device_params (DeviceDeviceParams | Unset): Device-specific parameters
        parent_device_mac (str | Unset): Parent device MAC for sub-devices
        firmware_ver (str | Unset): Firmware version
        hardware_ver (str | Unset): Hardware version
        conn_state (int | Unset): Connection state
        push_switch (int | Unset): Push notification switch state
    """

    mac: str | Unset = UNSET
    product_type: str | Unset = UNSET
    product_model: str | Unset = UNSET
    nickname: str | Unset = UNSET
    device_params: DeviceDeviceParams | Unset = UNSET
    parent_device_mac: str | Unset = UNSET
    firmware_ver: str | Unset = UNSET
    hardware_ver: str | Unset = UNSET
    conn_state: int | Unset = UNSET
    push_switch: int | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        mac = self.mac

        product_type = self.product_type

        product_model = self.product_model

        nickname = self.nickname

        device_params: dict[str, Any] | Unset = UNSET
        if not isinstance(self.device_params, Unset):
            device_params = self.device_params.to_dict()

        parent_device_mac = self.parent_device_mac

        firmware_ver = self.firmware_ver

        hardware_ver = self.hardware_ver

        conn_state = self.conn_state

        push_switch = self.push_switch

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if mac is not UNSET:
            field_dict["mac"] = mac
        if product_type is not UNSET:
            field_dict["product_type"] = product_type
        if product_model is not UNSET:
            field_dict["product_model"] = product_model
        if nickname is not UNSET:
            field_dict["nickname"] = nickname
        if device_params is not UNSET:
            field_dict["device_params"] = device_params
        if parent_device_mac is not UNSET:
            field_dict["parent_device_mac"] = parent_device_mac
        if firmware_ver is not UNSET:
            field_dict["firmware_ver"] = firmware_ver
        if hardware_ver is not UNSET:
            field_dict["hardware_ver"] = hardware_ver
        if conn_state is not UNSET:
            field_dict["conn_state"] = conn_state
        if push_switch is not UNSET:
            field_dict["push_switch"] = push_switch

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.device_device_params import DeviceDeviceParams

        d = dict(src_dict)
        mac = d.pop("mac", UNSET)

        product_type = d.pop("product_type", UNSET)

        product_model = d.pop("product_model", UNSET)

        nickname = d.pop("nickname", UNSET)

        _device_params = d.pop("device_params", UNSET)
        device_params: DeviceDeviceParams | Unset
        if isinstance(_device_params, Unset):
            device_params = UNSET
        else:
            device_params = DeviceDeviceParams.from_dict(_device_params)

        parent_device_mac = d.pop("parent_device_mac", UNSET)

        firmware_ver = d.pop("firmware_ver", UNSET)

        hardware_ver = d.pop("hardware_ver", UNSET)

        conn_state = d.pop("conn_state", UNSET)

        push_switch = d.pop("push_switch", UNSET)

        device = cls(
            mac=mac,
            product_type=product_type,
            product_model=product_model,
            nickname=nickname,
            device_params=device_params,
            parent_device_mac=parent_device_mac,
            firmware_ver=firmware_ver,
            hardware_ver=hardware_ver,
            conn_state=conn_state,
            push_switch=push_switch,
        )

        device.additional_properties = d
        return device

    @property
    def additional_keys(self) -> list[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
