from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.wall_switch_iot_prop_response_data_props_iot_state import WallSwitchIotPropResponseDataPropsIotState
from ..models.wall_switch_iot_prop_response_data_props_single_press_type import (
    WallSwitchIotPropResponseDataPropsSinglePressType,
)
from ..types import UNSET, Unset

T = TypeVar("T", bound="WallSwitchIotPropResponseDataProps")


@_attrs_define
class WallSwitchIotPropResponseDataProps:
    """
    Attributes:
        iot_state (WallSwitchIotPropResponseDataPropsIotState | Unset):
        switch_power (bool | Unset):
        switch_iot (bool | Unset):
        single_press_type (WallSwitchIotPropResponseDataPropsSinglePressType | Unset): 1=Classic, 2=IoT
    """

    iot_state: WallSwitchIotPropResponseDataPropsIotState | Unset = UNSET
    switch_power: bool | Unset = UNSET
    switch_iot: bool | Unset = UNSET
    single_press_type: WallSwitchIotPropResponseDataPropsSinglePressType | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        iot_state: str | Unset = UNSET
        if not isinstance(self.iot_state, Unset):
            iot_state = self.iot_state.value

        switch_power = self.switch_power

        switch_iot = self.switch_iot

        single_press_type: int | Unset = UNSET
        if not isinstance(self.single_press_type, Unset):
            single_press_type = self.single_press_type.value

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if iot_state is not UNSET:
            field_dict["iot_state"] = iot_state
        if switch_power is not UNSET:
            field_dict["switch-power"] = switch_power
        if switch_iot is not UNSET:
            field_dict["switch-iot"] = switch_iot
        if single_press_type is not UNSET:
            field_dict["single_press_type"] = single_press_type

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        _iot_state = d.pop("iot_state", UNSET)
        iot_state: WallSwitchIotPropResponseDataPropsIotState | Unset
        if isinstance(_iot_state, Unset):
            iot_state = UNSET
        else:
            iot_state = WallSwitchIotPropResponseDataPropsIotState(_iot_state)

        switch_power = d.pop("switch-power", UNSET)

        switch_iot = d.pop("switch-iot", UNSET)

        _single_press_type = d.pop("single_press_type", UNSET)
        single_press_type: WallSwitchIotPropResponseDataPropsSinglePressType | Unset
        if isinstance(_single_press_type, Unset):
            single_press_type = UNSET
        else:
            single_press_type = WallSwitchIotPropResponseDataPropsSinglePressType(_single_press_type)

        wall_switch_iot_prop_response_data_props = cls(
            iot_state=iot_state,
            switch_power=switch_power,
            switch_iot=switch_iot,
            single_press_type=single_press_type,
        )

        wall_switch_iot_prop_response_data_props.additional_properties = d
        return wall_switch_iot_prop_response_data_props

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
