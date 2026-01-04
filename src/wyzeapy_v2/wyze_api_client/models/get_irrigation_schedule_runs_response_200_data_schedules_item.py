from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.get_irrigation_schedule_runs_response_200_data_schedules_item_schedule_state import (
    GetIrrigationScheduleRunsResponse200DataSchedulesItemScheduleState,
)
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.get_irrigation_schedule_runs_response_200_data_schedules_item_zone_runs_item import (
        GetIrrigationScheduleRunsResponse200DataSchedulesItemZoneRunsItem,
    )


T = TypeVar("T", bound="GetIrrigationScheduleRunsResponse200DataSchedulesItem")


@_attrs_define
class GetIrrigationScheduleRunsResponse200DataSchedulesItem:
    """
    Attributes:
        schedule_state (GetIrrigationScheduleRunsResponse200DataSchedulesItemScheduleState | Unset):
        zone_runs (list[GetIrrigationScheduleRunsResponse200DataSchedulesItemZoneRunsItem] | Unset):
    """

    schedule_state: (
        GetIrrigationScheduleRunsResponse200DataSchedulesItemScheduleState | Unset
    ) = UNSET
    zone_runs: (
        list[GetIrrigationScheduleRunsResponse200DataSchedulesItemZoneRunsItem] | Unset
    ) = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        schedule_state: str | Unset = UNSET
        if not isinstance(self.schedule_state, Unset):
            schedule_state = self.schedule_state.value

        zone_runs: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.zone_runs, Unset):
            zone_runs = []
            for zone_runs_item_data in self.zone_runs:
                zone_runs_item = zone_runs_item_data.to_dict()
                zone_runs.append(zone_runs_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if schedule_state is not UNSET:
            field_dict["schedule_state"] = schedule_state
        if zone_runs is not UNSET:
            field_dict["zone_runs"] = zone_runs

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.get_irrigation_schedule_runs_response_200_data_schedules_item_zone_runs_item import (
            GetIrrigationScheduleRunsResponse200DataSchedulesItemZoneRunsItem,
        )

        d = dict(src_dict)
        _schedule_state = d.pop("schedule_state", UNSET)
        schedule_state: (
            GetIrrigationScheduleRunsResponse200DataSchedulesItemScheduleState | Unset
        )
        if isinstance(_schedule_state, Unset):
            schedule_state = UNSET
        else:
            schedule_state = (
                GetIrrigationScheduleRunsResponse200DataSchedulesItemScheduleState(
                    _schedule_state
                )
            )

        _zone_runs = d.pop("zone_runs", UNSET)
        zone_runs: (
            list[GetIrrigationScheduleRunsResponse200DataSchedulesItemZoneRunsItem]
            | Unset
        ) = UNSET
        if _zone_runs is not UNSET:
            zone_runs = []
            for zone_runs_item_data in _zone_runs:
                zone_runs_item = GetIrrigationScheduleRunsResponse200DataSchedulesItemZoneRunsItem.from_dict(
                    zone_runs_item_data
                )

                zone_runs.append(zone_runs_item)

        get_irrigation_schedule_runs_response_200_data_schedules_item = cls(
            schedule_state=schedule_state,
            zone_runs=zone_runs,
        )

        get_irrigation_schedule_runs_response_200_data_schedules_item.additional_properties = d
        return get_irrigation_schedule_runs_response_200_data_schedules_item

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
