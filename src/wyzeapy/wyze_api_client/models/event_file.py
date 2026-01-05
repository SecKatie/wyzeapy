from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="EventFile")


@_attrs_define
class EventFile:
    """
    Attributes:
        file_id (str | Unset): File identifier
        type_ (int | Unset): File type (1=Image, 2=Video)
        url (str | Unset): File URL
        status (int | Unset): File status
    """

    file_id: str | Unset = UNSET
    type_: int | Unset = UNSET
    url: str | Unset = UNSET
    status: int | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        file_id = self.file_id

        type_ = self.type_

        url = self.url

        status = self.status

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if file_id is not UNSET:
            field_dict["file_id"] = file_id
        if type_ is not UNSET:
            field_dict["type"] = type_
        if url is not UNSET:
            field_dict["url"] = url
        if status is not UNSET:
            field_dict["status"] = status

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        file_id = d.pop("file_id", UNSET)

        type_ = d.pop("type", UNSET)

        url = d.pop("url", UNSET)

        status = d.pop("status", UNSET)

        event_file = cls(
            file_id=file_id,
            type_=type_,
            url=url,
            status=status,
        )

        event_file.additional_properties = d
        return event_file

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
