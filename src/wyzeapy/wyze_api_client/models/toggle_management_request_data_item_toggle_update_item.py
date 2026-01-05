from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.toggle_management_request_data_item_toggle_update_item_toggle_status import (
    ToggleManagementRequestDataItemToggleUpdateItemToggleStatus,
)
from ..types import UNSET, Unset

T = TypeVar("T", bound="ToggleManagementRequestDataItemToggleUpdateItem")


@_attrs_define
class ToggleManagementRequestDataItemToggleUpdateItem:
    """
    Attributes:
        toggle_id (str | Unset):
        toggle_status (ToggleManagementRequestDataItemToggleUpdateItemToggleStatus | Unset):
    """

    toggle_id: str | Unset = UNSET
    toggle_status: ToggleManagementRequestDataItemToggleUpdateItemToggleStatus | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        toggle_id = self.toggle_id

        toggle_status: str | Unset = UNSET
        if not isinstance(self.toggle_status, Unset):
            toggle_status = self.toggle_status.value

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if toggle_id is not UNSET:
            field_dict["toggle_id"] = toggle_id
        if toggle_status is not UNSET:
            field_dict["toggle_status"] = toggle_status

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        toggle_id = d.pop("toggle_id", UNSET)

        _toggle_status = d.pop("toggle_status", UNSET)
        toggle_status: ToggleManagementRequestDataItemToggleUpdateItemToggleStatus | Unset
        if isinstance(_toggle_status, Unset):
            toggle_status = UNSET
        else:
            toggle_status = ToggleManagementRequestDataItemToggleUpdateItemToggleStatus(_toggle_status)

        toggle_management_request_data_item_toggle_update_item = cls(
            toggle_id=toggle_id,
            toggle_status=toggle_status,
        )

        toggle_management_request_data_item_toggle_update_item.additional_properties = d
        return toggle_management_request_data_item_toggle_update_item

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
