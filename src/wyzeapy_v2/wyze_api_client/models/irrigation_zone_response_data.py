from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.irrigation_zone import IrrigationZone


T = TypeVar("T", bound="IrrigationZoneResponseData")


@_attrs_define
class IrrigationZoneResponseData:
    """
    Attributes:
        zones (list[IrrigationZone] | Unset):
    """

    zones: list[IrrigationZone] | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        zones: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.zones, Unset):
            zones = []
            for zones_item_data in self.zones:
                zones_item = zones_item_data.to_dict()
                zones.append(zones_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if zones is not UNSET:
            field_dict["zones"] = zones

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.irrigation_zone import IrrigationZone

        d = dict(src_dict)
        _zones = d.pop("zones", UNSET)
        zones: list[IrrigationZone] | Unset = UNSET
        if _zones is not UNSET:
            zones = []
            for zones_item_data in _zones:
                zones_item = IrrigationZone.from_dict(zones_item_data)

                zones.append(zones_item)

        irrigation_zone_response_data = cls(
            zones=zones,
        )

        irrigation_zone_response_data.additional_properties = d
        return irrigation_zone_response_data

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
