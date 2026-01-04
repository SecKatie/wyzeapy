from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.plug_usage_response_data_usage_record_list_item import (
        PlugUsageResponseDataUsageRecordListItem,
    )


T = TypeVar("T", bound="PlugUsageResponseData")


@_attrs_define
class PlugUsageResponseData:
    """
    Attributes:
        usage_record_list (list[PlugUsageResponseDataUsageRecordListItem] | Unset):
    """

    usage_record_list: list[PlugUsageResponseDataUsageRecordListItem] | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        usage_record_list: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.usage_record_list, Unset):
            usage_record_list = []
            for usage_record_list_item_data in self.usage_record_list:
                usage_record_list_item = usage_record_list_item_data.to_dict()
                usage_record_list.append(usage_record_list_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if usage_record_list is not UNSET:
            field_dict["usage_record_list"] = usage_record_list

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.plug_usage_response_data_usage_record_list_item import (
            PlugUsageResponseDataUsageRecordListItem,
        )

        d = dict(src_dict)
        _usage_record_list = d.pop("usage_record_list", UNSET)
        usage_record_list: list[PlugUsageResponseDataUsageRecordListItem] | Unset = (
            UNSET
        )
        if _usage_record_list is not UNSET:
            usage_record_list = []
            for usage_record_list_item_data in _usage_record_list:
                usage_record_list_item = (
                    PlugUsageResponseDataUsageRecordListItem.from_dict(
                        usage_record_list_item_data
                    )
                )

                usage_record_list.append(usage_record_list_item)

        plug_usage_response_data = cls(
            usage_record_list=usage_record_list,
        )

        plug_usage_response_data.additional_properties = d
        return plug_usage_response_data

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
