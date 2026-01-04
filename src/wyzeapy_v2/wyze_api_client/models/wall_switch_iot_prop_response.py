from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.wall_switch_iot_prop_response_data import (
        WallSwitchIotPropResponseData,
    )


T = TypeVar("T", bound="WallSwitchIotPropResponse")


@_attrs_define
class WallSwitchIotPropResponse:
    """
    Attributes:
        data (WallSwitchIotPropResponseData | Unset):
    """

    data: WallSwitchIotPropResponseData | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        data: dict[str, Any] | Unset = UNSET
        if not isinstance(self.data, Unset):
            data = self.data.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if data is not UNSET:
            field_dict["data"] = data

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.wall_switch_iot_prop_response_data import (
            WallSwitchIotPropResponseData,
        )

        d = dict(src_dict)
        _data = d.pop("data", UNSET)
        data: WallSwitchIotPropResponseData | Unset
        if isinstance(_data, Unset):
            data = UNSET
        else:
            data = WallSwitchIotPropResponseData.from_dict(_data)

        wall_switch_iot_prop_response = cls(
            data=data,
        )

        wall_switch_iot_prop_response.additional_properties = d
        return wall_switch_iot_prop_response

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
