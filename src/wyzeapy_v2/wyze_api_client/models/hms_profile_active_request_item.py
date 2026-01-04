from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.hms_profile_active_request_item_active import (
    HMSProfileActiveRequestItemActive,
)
from ..models.hms_profile_active_request_item_state import (
    HMSProfileActiveRequestItemState,
)
from ..types import UNSET, Unset

T = TypeVar("T", bound="HMSProfileActiveRequestItem")


@_attrs_define
class HMSProfileActiveRequestItem:
    """
    Attributes:
        state (HMSProfileActiveRequestItemState | Unset):
        active (HMSProfileActiveRequestItemActive | Unset):
    """

    state: HMSProfileActiveRequestItemState | Unset = UNSET
    active: HMSProfileActiveRequestItemActive | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        state: str | Unset = UNSET
        if not isinstance(self.state, Unset):
            state = self.state.value

        active: int | Unset = UNSET
        if not isinstance(self.active, Unset):
            active = self.active.value

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if state is not UNSET:
            field_dict["state"] = state
        if active is not UNSET:
            field_dict["active"] = active

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        _state = d.pop("state", UNSET)
        state: HMSProfileActiveRequestItemState | Unset
        if isinstance(_state, Unset):
            state = UNSET
        else:
            state = HMSProfileActiveRequestItemState(_state)

        _active = d.pop("active", UNSET)
        active: HMSProfileActiveRequestItemActive | Unset
        if isinstance(_active, Unset):
            active = UNSET
        else:
            active = HMSProfileActiveRequestItemActive(_active)

        hms_profile_active_request_item = cls(
            state=state,
            active=active,
        )

        hms_profile_active_request_item.additional_properties = d
        return hms_profile_active_request_item

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
