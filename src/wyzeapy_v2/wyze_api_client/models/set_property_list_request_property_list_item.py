from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="SetPropertyListRequestPropertyListItem")


@_attrs_define
class SetPropertyListRequestPropertyListItem:
    """
    Attributes:
        pid (str | Unset):
        pvalue (str | Unset):
    """

    pid: str | Unset = UNSET
    pvalue: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        pid = self.pid

        pvalue = self.pvalue

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if pid is not UNSET:
            field_dict["pid"] = pid
        if pvalue is not UNSET:
            field_dict["pvalue"] = pvalue

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        pid = d.pop("pid", UNSET)

        pvalue = d.pop("pvalue", UNSET)

        set_property_list_request_property_list_item = cls(
            pid=pid,
            pvalue=pvalue,
        )

        set_property_list_request_property_list_item.additional_properties = d
        return set_property_list_request_property_list_item

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
