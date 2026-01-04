from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.get_irrigation_iot_prop_response_200_data_props import (
        GetIrrigationIotPropResponse200DataProps,
    )


T = TypeVar("T", bound="GetIrrigationIotPropResponse200Data")


@_attrs_define
class GetIrrigationIotPropResponse200Data:
    """
    Attributes:
        props (GetIrrigationIotPropResponse200DataProps | Unset):
    """

    props: GetIrrigationIotPropResponse200DataProps | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        props: dict[str, Any] | Unset = UNSET
        if not isinstance(self.props, Unset):
            props = self.props.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if props is not UNSET:
            field_dict["props"] = props

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.get_irrigation_iot_prop_response_200_data_props import (
            GetIrrigationIotPropResponse200DataProps,
        )

        d = dict(src_dict)
        _props = d.pop("props", UNSET)
        props: GetIrrigationIotPropResponse200DataProps | Unset
        if isinstance(_props, Unset):
            props = UNSET
        else:
            props = GetIrrigationIotPropResponse200DataProps.from_dict(_props)

        get_irrigation_iot_prop_response_200_data = cls(
            props=props,
        )

        get_irrigation_iot_prop_response_200_data.additional_properties = d
        return get_irrigation_iot_prop_response_200_data

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
