from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.wall_switch_iot_prop_response_data_props import WallSwitchIotPropResponseDataProps


T = TypeVar("T", bound="WallSwitchIotPropResponseData")


@_attrs_define
class WallSwitchIotPropResponseData:
    """
    Attributes:
        props (WallSwitchIotPropResponseDataProps | Unset):
    """

    props: WallSwitchIotPropResponseDataProps | Unset = UNSET
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
        from ..models.wall_switch_iot_prop_response_data_props import WallSwitchIotPropResponseDataProps

        d = dict(src_dict)
        _props = d.pop("props", UNSET)
        props: WallSwitchIotPropResponseDataProps | Unset
        if isinstance(_props, Unset):
            props = UNSET
        else:
            props = WallSwitchIotPropResponseDataProps.from_dict(_props)

        wall_switch_iot_prop_response_data = cls(
            props=props,
        )

        wall_switch_iot_prop_response_data.additional_properties = d
        return wall_switch_iot_prop_response_data

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
