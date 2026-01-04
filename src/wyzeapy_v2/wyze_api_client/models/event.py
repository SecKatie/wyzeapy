from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.event_file import EventFile


T = TypeVar("T", bound="Event")


@_attrs_define
class Event:
    """
    Attributes:
        event_id (str | Unset): Unique event identifier
        device_mac (str | Unset): Device MAC address
        device_model (str | Unset): Device model
        event_category (int | Unset): Event category code
        event_value (str | Unset): Event value
        event_ts (int | Unset): Event timestamp in milliseconds
        file_list (list[EventFile] | Unset):
    """

    event_id: str | Unset = UNSET
    device_mac: str | Unset = UNSET
    device_model: str | Unset = UNSET
    event_category: int | Unset = UNSET
    event_value: str | Unset = UNSET
    event_ts: int | Unset = UNSET
    file_list: list[EventFile] | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        event_id = self.event_id

        device_mac = self.device_mac

        device_model = self.device_model

        event_category = self.event_category

        event_value = self.event_value

        event_ts = self.event_ts

        file_list: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.file_list, Unset):
            file_list = []
            for file_list_item_data in self.file_list:
                file_list_item = file_list_item_data.to_dict()
                file_list.append(file_list_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if event_id is not UNSET:
            field_dict["event_id"] = event_id
        if device_mac is not UNSET:
            field_dict["device_mac"] = device_mac
        if device_model is not UNSET:
            field_dict["device_model"] = device_model
        if event_category is not UNSET:
            field_dict["event_category"] = event_category
        if event_value is not UNSET:
            field_dict["event_value"] = event_value
        if event_ts is not UNSET:
            field_dict["event_ts"] = event_ts
        if file_list is not UNSET:
            field_dict["file_list"] = file_list

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.event_file import EventFile

        d = dict(src_dict)
        event_id = d.pop("event_id", UNSET)

        device_mac = d.pop("device_mac", UNSET)

        device_model = d.pop("device_model", UNSET)

        event_category = d.pop("event_category", UNSET)

        event_value = d.pop("event_value", UNSET)

        event_ts = d.pop("event_ts", UNSET)

        _file_list = d.pop("file_list", UNSET)
        file_list: list[EventFile] | Unset = UNSET
        if _file_list is not UNSET:
            file_list = []
            for file_list_item_data in _file_list:
                file_list_item = EventFile.from_dict(file_list_item_data)

                file_list.append(file_list_item)

        event = cls(
            event_id=event_id,
            device_mac=device_mac,
            device_model=device_model,
            event_category=event_category,
            event_value=event_value,
            event_ts=event_ts,
            file_list=file_list,
        )

        event.additional_properties = d
        return event

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
