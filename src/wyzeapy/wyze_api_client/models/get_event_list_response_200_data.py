from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.event import Event


T = TypeVar("T", bound="GetEventListResponse200Data")


@_attrs_define
class GetEventListResponse200Data:
    """
    Attributes:
        event_list (list[Event] | Unset):
    """

    event_list: list[Event] | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        event_list: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.event_list, Unset):
            event_list = []
            for event_list_item_data in self.event_list:
                event_list_item = event_list_item_data.to_dict()
                event_list.append(event_list_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if event_list is not UNSET:
            field_dict["event_list"] = event_list

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.event import Event

        d = dict(src_dict)
        _event_list = d.pop("event_list", UNSET)
        event_list: list[Event] | Unset = UNSET
        if _event_list is not UNSET:
            event_list = []
            for event_list_item_data in _event_list:
                event_list_item = Event.from_dict(event_list_item_data)

                event_list.append(event_list_item)

        get_event_list_response_200_data = cls(
            event_list=event_list,
        )

        get_event_list_response_200_data.additional_properties = d
        return get_event_list_response_200_data

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
