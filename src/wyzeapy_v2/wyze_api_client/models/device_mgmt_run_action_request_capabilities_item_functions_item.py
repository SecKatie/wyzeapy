from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.device_mgmt_run_action_request_capabilities_item_functions_item_in import (
        DeviceMgmtRunActionRequestCapabilitiesItemFunctionsItemIn,
    )


T = TypeVar("T", bound="DeviceMgmtRunActionRequestCapabilitiesItemFunctionsItem")


@_attrs_define
class DeviceMgmtRunActionRequestCapabilitiesItemFunctionsItem:
    """
    Attributes:
        name (str | Unset):
        in_ (DeviceMgmtRunActionRequestCapabilitiesItemFunctionsItemIn | Unset):
    """

    name: str | Unset = UNSET
    in_: DeviceMgmtRunActionRequestCapabilitiesItemFunctionsItemIn | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        name = self.name

        in_: dict[str, Any] | Unset = UNSET
        if not isinstance(self.in_, Unset):
            in_ = self.in_.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if name is not UNSET:
            field_dict["name"] = name
        if in_ is not UNSET:
            field_dict["in"] = in_

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.device_mgmt_run_action_request_capabilities_item_functions_item_in import (
            DeviceMgmtRunActionRequestCapabilitiesItemFunctionsItemIn,
        )

        d = dict(src_dict)
        name = d.pop("name", UNSET)

        _in_ = d.pop("in", UNSET)
        in_: DeviceMgmtRunActionRequestCapabilitiesItemFunctionsItemIn | Unset
        if isinstance(_in_, Unset):
            in_ = UNSET
        else:
            in_ = DeviceMgmtRunActionRequestCapabilitiesItemFunctionsItemIn.from_dict(
                _in_
            )

        device_mgmt_run_action_request_capabilities_item_functions_item = cls(
            name=name,
            in_=in_,
        )

        device_mgmt_run_action_request_capabilities_item_functions_item.additional_properties = d
        return device_mgmt_run_action_request_capabilities_item_functions_item

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
