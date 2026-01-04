from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.get_plan_binding_list_response_200_data_item_device_list_item import (
        GetPlanBindingListResponse200DataItemDeviceListItem,
    )


T = TypeVar("T", bound="GetPlanBindingListResponse200DataItem")


@_attrs_define
class GetPlanBindingListResponse200DataItem:
    """
    Attributes:
        device_list (list[GetPlanBindingListResponse200DataItemDeviceListItem] | Unset):
    """

    device_list: list[GetPlanBindingListResponse200DataItemDeviceListItem] | Unset = UNSET
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
            field_dict["deviceList"] = device_list

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.get_plan_binding_list_response_200_data_item_device_list_item import (
            GetPlanBindingListResponse200DataItemDeviceListItem,
        )

        d = dict(src_dict)
        _device_list = d.pop("deviceList", UNSET)
        device_list: list[GetPlanBindingListResponse200DataItemDeviceListItem] | Unset = UNSET
        if _device_list is not UNSET:
            device_list = []
            for device_list_item_data in _device_list:
                device_list_item = GetPlanBindingListResponse200DataItemDeviceListItem.from_dict(device_list_item_data)

                device_list.append(device_list_item)

        get_plan_binding_list_response_200_data_item = cls(
            device_list=device_list,
        )

        get_plan_binding_list_response_200_data_item.additional_properties = d
        return get_plan_binding_list_response_200_data_item

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
