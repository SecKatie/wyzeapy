from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.set_thermostat_iot_prop_body_props import SetThermostatIotPropBodyProps


T = TypeVar("T", bound="SetThermostatIotPropBody")


@_attrs_define
class SetThermostatIotPropBody:
    """
    Attributes:
        did (str | Unset):
        model (str | Unset):
        props (SetThermostatIotPropBodyProps | Unset):
        is_sub_device (int | Unset):
        nonce (str | Unset):
    """

    did: str | Unset = UNSET
    model: str | Unset = UNSET
    props: SetThermostatIotPropBodyProps | Unset = UNSET
    is_sub_device: int | Unset = UNSET
    nonce: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        did = self.did

        model = self.model

        props: dict[str, Any] | Unset = UNSET
        if not isinstance(self.props, Unset):
            props = self.props.to_dict()

        is_sub_device = self.is_sub_device

        nonce = self.nonce

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if did is not UNSET:
            field_dict["did"] = did
        if model is not UNSET:
            field_dict["model"] = model
        if props is not UNSET:
            field_dict["props"] = props
        if is_sub_device is not UNSET:
            field_dict["is_sub_device"] = is_sub_device
        if nonce is not UNSET:
            field_dict["nonce"] = nonce

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.set_thermostat_iot_prop_body_props import SetThermostatIotPropBodyProps

        d = dict(src_dict)
        did = d.pop("did", UNSET)

        model = d.pop("model", UNSET)

        _props = d.pop("props", UNSET)
        props: SetThermostatIotPropBodyProps | Unset
        if isinstance(_props, Unset):
            props = UNSET
        else:
            props = SetThermostatIotPropBodyProps.from_dict(_props)

        is_sub_device = d.pop("is_sub_device", UNSET)

        nonce = d.pop("nonce", UNSET)

        set_thermostat_iot_prop_body = cls(
            did=did,
            model=model,
            props=props,
            is_sub_device=is_sub_device,
            nonce=nonce,
        )

        set_thermostat_iot_prop_body.additional_properties = d
        return set_thermostat_iot_prop_body

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
