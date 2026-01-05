from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.device import Device


T = TypeVar("T", bound="GetObjectListResponseData")


@_attrs_define
class GetObjectListResponseData:
    """
    Attributes:
        device_list (list[Device] | Unset):
    """

    device_list: list[Device] | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        device_list: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.device_list, Unset):
            device_list = []
            for device_list_item_data in self.device_list:
                device_list_item = device_list_item_data.to_dict()
                device_list.append(device_list_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if device_list is not UNSET:
            field_dict["device_list"] = device_list

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.device import Device

        d = dict(src_dict)
        _device_list = d.pop("device_list", UNSET)
        device_list: list[Device] | Unset = UNSET
        if _device_list is not UNSET:
            device_list = []
            for device_list_item_data in _device_list:
                device_list_item = Device.from_dict(device_list_item_data)

                device_list.append(device_list_item)

        get_object_list_response_data = cls(
            device_list=device_list,
        )

        get_object_list_response_data.additional_properties = d
        return get_object_list_response_data

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
