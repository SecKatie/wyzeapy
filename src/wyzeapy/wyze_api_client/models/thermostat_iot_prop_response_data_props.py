from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.thermostat_iot_prop_response_data_props_current_scenario import (
    ThermostatIotPropResponseDataPropsCurrentScenario,
)
from ..models.thermostat_iot_prop_response_data_props_fan_mode import ThermostatIotPropResponseDataPropsFanMode
from ..models.thermostat_iot_prop_response_data_props_iot_state import ThermostatIotPropResponseDataPropsIotState
from ..models.thermostat_iot_prop_response_data_props_mode_sys import ThermostatIotPropResponseDataPropsModeSys
from ..models.thermostat_iot_prop_response_data_props_temp_unit import ThermostatIotPropResponseDataPropsTempUnit
from ..models.thermostat_iot_prop_response_data_props_working_state import (
    ThermostatIotPropResponseDataPropsWorkingState,
)
from ..types import UNSET, Unset

T = TypeVar("T", bound="ThermostatIotPropResponseDataProps")


@_attrs_define
class ThermostatIotPropResponseDataProps:
    """
    Attributes:
        temperature (str | Unset):
        humidity (str | Unset):
        cool_sp (str | Unset):
        heat_sp (str | Unset):
        mode_sys (ThermostatIotPropResponseDataPropsModeSys | Unset):
        fan_mode (ThermostatIotPropResponseDataPropsFanMode | Unset):
        current_scenario (ThermostatIotPropResponseDataPropsCurrentScenario | Unset):
        temp_unit (ThermostatIotPropResponseDataPropsTempUnit | Unset):
        iot_state (ThermostatIotPropResponseDataPropsIotState | Unset):
        working_state (ThermostatIotPropResponseDataPropsWorkingState | Unset):
    """

    temperature: str | Unset = UNSET
    humidity: str | Unset = UNSET
    cool_sp: str | Unset = UNSET
    heat_sp: str | Unset = UNSET
    mode_sys: ThermostatIotPropResponseDataPropsModeSys | Unset = UNSET
    fan_mode: ThermostatIotPropResponseDataPropsFanMode | Unset = UNSET
    current_scenario: ThermostatIotPropResponseDataPropsCurrentScenario | Unset = UNSET
    temp_unit: ThermostatIotPropResponseDataPropsTempUnit | Unset = UNSET
    iot_state: ThermostatIotPropResponseDataPropsIotState | Unset = UNSET
    working_state: ThermostatIotPropResponseDataPropsWorkingState | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        temperature = self.temperature

        humidity = self.humidity

        cool_sp = self.cool_sp

        heat_sp = self.heat_sp

        mode_sys: str | Unset = UNSET
        if not isinstance(self.mode_sys, Unset):
            mode_sys = self.mode_sys.value

        fan_mode: str | Unset = UNSET
        if not isinstance(self.fan_mode, Unset):
            fan_mode = self.fan_mode.value

        current_scenario: str | Unset = UNSET
        if not isinstance(self.current_scenario, Unset):
            current_scenario = self.current_scenario.value

        temp_unit: str | Unset = UNSET
        if not isinstance(self.temp_unit, Unset):
            temp_unit = self.temp_unit.value

        iot_state: str | Unset = UNSET
        if not isinstance(self.iot_state, Unset):
            iot_state = self.iot_state.value

        working_state: str | Unset = UNSET
        if not isinstance(self.working_state, Unset):
            working_state = self.working_state.value

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if temperature is not UNSET:
            field_dict["temperature"] = temperature
        if humidity is not UNSET:
            field_dict["humidity"] = humidity
        if cool_sp is not UNSET:
            field_dict["cool_sp"] = cool_sp
        if heat_sp is not UNSET:
            field_dict["heat_sp"] = heat_sp
        if mode_sys is not UNSET:
            field_dict["mode_sys"] = mode_sys
        if fan_mode is not UNSET:
            field_dict["fan_mode"] = fan_mode
        if current_scenario is not UNSET:
            field_dict["current_scenario"] = current_scenario
        if temp_unit is not UNSET:
            field_dict["temp_unit"] = temp_unit
        if iot_state is not UNSET:
            field_dict["iot_state"] = iot_state
        if working_state is not UNSET:
            field_dict["working_state"] = working_state

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        temperature = d.pop("temperature", UNSET)

        humidity = d.pop("humidity", UNSET)

        cool_sp = d.pop("cool_sp", UNSET)

        heat_sp = d.pop("heat_sp", UNSET)

        _mode_sys = d.pop("mode_sys", UNSET)
        mode_sys: ThermostatIotPropResponseDataPropsModeSys | Unset
        if isinstance(_mode_sys, Unset):
            mode_sys = UNSET
        else:
            mode_sys = ThermostatIotPropResponseDataPropsModeSys(_mode_sys)

        _fan_mode = d.pop("fan_mode", UNSET)
        fan_mode: ThermostatIotPropResponseDataPropsFanMode | Unset
        if isinstance(_fan_mode, Unset):
            fan_mode = UNSET
        else:
            fan_mode = ThermostatIotPropResponseDataPropsFanMode(_fan_mode)

        _current_scenario = d.pop("current_scenario", UNSET)
        current_scenario: ThermostatIotPropResponseDataPropsCurrentScenario | Unset
        if isinstance(_current_scenario, Unset):
            current_scenario = UNSET
        else:
            current_scenario = ThermostatIotPropResponseDataPropsCurrentScenario(_current_scenario)

        _temp_unit = d.pop("temp_unit", UNSET)
        temp_unit: ThermostatIotPropResponseDataPropsTempUnit | Unset
        if isinstance(_temp_unit, Unset):
            temp_unit = UNSET
        else:
            temp_unit = ThermostatIotPropResponseDataPropsTempUnit(_temp_unit)

        _iot_state = d.pop("iot_state", UNSET)
        iot_state: ThermostatIotPropResponseDataPropsIotState | Unset
        if isinstance(_iot_state, Unset):
            iot_state = UNSET
        else:
            iot_state = ThermostatIotPropResponseDataPropsIotState(_iot_state)

        _working_state = d.pop("working_state", UNSET)
        working_state: ThermostatIotPropResponseDataPropsWorkingState | Unset
        if isinstance(_working_state, Unset):
            working_state = UNSET
        else:
            working_state = ThermostatIotPropResponseDataPropsWorkingState(_working_state)

        thermostat_iot_prop_response_data_props = cls(
            temperature=temperature,
            humidity=humidity,
            cool_sp=cool_sp,
            heat_sp=heat_sp,
            mode_sys=mode_sys,
            fan_mode=fan_mode,
            current_scenario=current_scenario,
            temp_unit=temp_unit,
            iot_state=iot_state,
            working_state=working_state,
        )

        thermostat_iot_prop_response_data_props.additional_properties = d
        return thermostat_iot_prop_response_data_props

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
