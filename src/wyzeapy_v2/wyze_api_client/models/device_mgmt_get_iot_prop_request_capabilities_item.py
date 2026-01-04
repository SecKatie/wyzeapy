from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="DeviceMgmtGetIotPropRequestCapabilitiesItem")


@_attrs_define
class DeviceMgmtGetIotPropRequestCapabilitiesItem:
    """
    Attributes:
        iid (int | Unset):
        name (str | Unset):
        properties (list[str] | Unset):
    """

    iid: int | Unset = UNSET
    name: str | Unset = UNSET
    properties: list[str] | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        iid = self.iid

        name = self.name

        properties: list[str] | Unset = UNSET
        if not isinstance(self.properties, Unset):
            properties = self.properties

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if iid is not UNSET:
            field_dict["iid"] = iid
        if name is not UNSET:
            field_dict["name"] = name
        if properties is not UNSET:
            field_dict["properties"] = properties

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        iid = d.pop("iid", UNSET)

        name = d.pop("name", UNSET)

        properties = cast(list[str], d.pop("properties", UNSET))

        device_mgmt_get_iot_prop_request_capabilities_item = cls(
            iid=iid,
            name=name,
            properties=properties,
        )

        device_mgmt_get_iot_prop_request_capabilities_item.additional_properties = d
        return device_mgmt_get_iot_prop_request_capabilities_item

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
