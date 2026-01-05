from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.irrigation_quick_run_request_zone_runs_item import IrrigationQuickRunRequestZoneRunsItem


T = TypeVar("T", bound="IrrigationQuickRunRequest")


@_attrs_define
class IrrigationQuickRunRequest:
    """
    Attributes:
        device_id (str):
        nonce (str):
        zone_runs (list[IrrigationQuickRunRequestZoneRunsItem]):
    """

    device_id: str
    nonce: str
    zone_runs: list[IrrigationQuickRunRequestZoneRunsItem]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        device_id = self.device_id

        nonce = self.nonce

        zone_runs = []
        for zone_runs_item_data in self.zone_runs:
            zone_runs_item = zone_runs_item_data.to_dict()
            zone_runs.append(zone_runs_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "device_id": device_id,
                "nonce": nonce,
                "zone_runs": zone_runs,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.irrigation_quick_run_request_zone_runs_item import IrrigationQuickRunRequestZoneRunsItem

        d = dict(src_dict)
        device_id = d.pop("device_id")

        nonce = d.pop("nonce")

        zone_runs = []
        _zone_runs = d.pop("zone_runs")
        for zone_runs_item_data in _zone_runs:
            zone_runs_item = IrrigationQuickRunRequestZoneRunsItem.from_dict(zone_runs_item_data)

            zone_runs.append(zone_runs_item)

        irrigation_quick_run_request = cls(
            device_id=device_id,
            nonce=nonce,
            zone_runs=zone_runs,
        )

        irrigation_quick_run_request.additional_properties = d
        return irrigation_quick_run_request

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
