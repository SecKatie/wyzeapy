from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.get_streams_request_device import GetStreamsRequestDevice


T = TypeVar("T", bound="GetStreamsRequest")


@_attrs_define
class GetStreamsRequest:
    """
    Attributes:
        device_list (list[GetStreamsRequestDevice]): List of devices to get stream info for
        nonce (str): Nonce value (typically timestamp in milliseconds)
    """

    device_list: list[GetStreamsRequestDevice]
    nonce: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        device_list = []
        for device_list_item_data in self.device_list:
            device_list_item = device_list_item_data.to_dict()
            device_list.append(device_list_item)

        nonce = self.nonce

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "device_list": device_list,
                "nonce": nonce,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.get_streams_request_device import GetStreamsRequestDevice

        d = dict(src_dict)
        device_list = []
        _device_list = d.pop("device_list")
        for device_list_item_data in _device_list:
            device_list_item = GetStreamsRequestDevice.from_dict(device_list_item_data)

            device_list.append(device_list_item)

        nonce = d.pop("nonce")

        get_streams_request = cls(
            device_list=device_list,
            nonce=nonce,
        )

        get_streams_request.additional_properties = d
        return get_streams_request

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
