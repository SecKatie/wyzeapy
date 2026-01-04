from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.toggle_management_request_data_item_toggle_update_item import (
        ToggleManagementRequestDataItemToggleUpdateItem,
    )


T = TypeVar("T", bound="ToggleManagementRequestDataItem")


@_attrs_define
class ToggleManagementRequestDataItem:
    """
    Attributes:
        device_firmware (str | Unset):
        device_id (str | Unset):
        device_model (str | Unset):
        page_id (list[str] | Unset):
        toggle_update (list[ToggleManagementRequestDataItemToggleUpdateItem] | Unset):
    """

    device_firmware: str | Unset = UNSET
    device_id: str | Unset = UNSET
    device_model: str | Unset = UNSET
    page_id: list[str] | Unset = UNSET
    toggle_update: list[ToggleManagementRequestDataItemToggleUpdateItem] | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        device_firmware = self.device_firmware

        device_id = self.device_id

        device_model = self.device_model

        page_id: list[str] | Unset = UNSET
        if not isinstance(self.page_id, Unset):
            page_id = self.page_id

        toggle_update: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.toggle_update, Unset):
            toggle_update = []
            for toggle_update_item_data in self.toggle_update:
                toggle_update_item = toggle_update_item_data.to_dict()
                toggle_update.append(toggle_update_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if device_firmware is not UNSET:
            field_dict["device_firmware"] = device_firmware
        if device_id is not UNSET:
            field_dict["device_id"] = device_id
        if device_model is not UNSET:
            field_dict["device_model"] = device_model
        if page_id is not UNSET:
            field_dict["page_id"] = page_id
        if toggle_update is not UNSET:
            field_dict["toggle_update"] = toggle_update

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.toggle_management_request_data_item_toggle_update_item import (
            ToggleManagementRequestDataItemToggleUpdateItem,
        )

        d = dict(src_dict)
        device_firmware = d.pop("device_firmware", UNSET)

        device_id = d.pop("device_id", UNSET)

        device_model = d.pop("device_model", UNSET)

        page_id = cast(list[str], d.pop("page_id", UNSET))

        _toggle_update = d.pop("toggle_update", UNSET)
        toggle_update: list[ToggleManagementRequestDataItemToggleUpdateItem] | Unset = (
            UNSET
        )
        if _toggle_update is not UNSET:
            toggle_update = []
            for toggle_update_item_data in _toggle_update:
                toggle_update_item = (
                    ToggleManagementRequestDataItemToggleUpdateItem.from_dict(
                        toggle_update_item_data
                    )
                )

                toggle_update.append(toggle_update_item)

        toggle_management_request_data_item = cls(
            device_firmware=device_firmware,
            device_id=device_id,
            device_model=device_model,
            page_id=page_id,
            toggle_update=toggle_update,
        )

        toggle_management_request_data_item.additional_properties = d
        return toggle_management_request_data_item

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
