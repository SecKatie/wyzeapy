from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="IrrigationZone")


@_attrs_define
class IrrigationZone:
    """
    Attributes:
        zone_number (int | Unset):
        name (str | Unset):
        enabled (bool | Unset):
        zone_id (str | Unset):
        smart_duration (int | Unset): Duration in seconds
    """

    zone_number: int | Unset = UNSET
    name: str | Unset = UNSET
    enabled: bool | Unset = UNSET
    zone_id: str | Unset = UNSET
    smart_duration: int | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        zone_number = self.zone_number

        name = self.name

        enabled = self.enabled

        zone_id = self.zone_id

        smart_duration = self.smart_duration

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if zone_number is not UNSET:
            field_dict["zone_number"] = zone_number
        if name is not UNSET:
            field_dict["name"] = name
        if enabled is not UNSET:
            field_dict["enabled"] = enabled
        if zone_id is not UNSET:
            field_dict["zone_id"] = zone_id
        if smart_duration is not UNSET:
            field_dict["smart_duration"] = smart_duration

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        zone_number = d.pop("zone_number", UNSET)

        name = d.pop("name", UNSET)

        enabled = d.pop("enabled", UNSET)

        zone_id = d.pop("zone_id", UNSET)

        smart_duration = d.pop("smart_duration", UNSET)

        irrigation_zone = cls(
            zone_number=zone_number,
            name=name,
            enabled=enabled,
            zone_id=zone_id,
            smart_duration=smart_duration,
        )

        irrigation_zone.additional_properties = d
        return irrigation_zone

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
