from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar(
    "T", bound="GetIrrigationScheduleRunsResponse200DataSchedulesItemZoneRunsItem"
)


@_attrs_define
class GetIrrigationScheduleRunsResponse200DataSchedulesItemZoneRunsItem:
    """
    Attributes:
        zone_number (int | Unset):
        zone_name (str | Unset):
    """

    zone_number: int | Unset = UNSET
    zone_name: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        zone_number = self.zone_number

        zone_name = self.zone_name

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if zone_number is not UNSET:
            field_dict["zone_number"] = zone_number
        if zone_name is not UNSET:
            field_dict["zone_name"] = zone_name

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        zone_number = d.pop("zone_number", UNSET)

        zone_name = d.pop("zone_name", UNSET)

        get_irrigation_schedule_runs_response_200_data_schedules_item_zone_runs_item = (
            cls(
                zone_number=zone_number,
                zone_name=zone_name,
            )
        )

        get_irrigation_schedule_runs_response_200_data_schedules_item_zone_runs_item.additional_properties = d
        return (
            get_irrigation_schedule_runs_response_200_data_schedules_item_zone_runs_item
        )

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
