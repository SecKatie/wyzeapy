from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="IrrigationQuickRunRequestZoneRunsItem")


@_attrs_define
class IrrigationQuickRunRequestZoneRunsItem:
    """
    Attributes:
        zone_number (int | Unset):
        duration (int | Unset): Duration in seconds
    """

    zone_number: int | Unset = UNSET
    duration: int | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        zone_number = self.zone_number

        duration = self.duration

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if zone_number is not UNSET:
            field_dict["zone_number"] = zone_number
        if duration is not UNSET:
            field_dict["duration"] = duration

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        zone_number = d.pop("zone_number", UNSET)

        duration = d.pop("duration", UNSET)

        irrigation_quick_run_request_zone_runs_item = cls(
            zone_number=zone_number,
            duration=duration,
        )

        irrigation_quick_run_request_zone_runs_item.additional_properties = d
        return irrigation_quick_run_request_zone_runs_item

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
