from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.property_ import Property


T = TypeVar("T", bound="GetPropertyListResponseData")


@_attrs_define
class GetPropertyListResponseData:
    """
    Attributes:
        property_list (list[Property] | Unset):
    """

    property_list: list[Property] | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        property_list: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.property_list, Unset):
            property_list = []
            for property_list_item_data in self.property_list:
                property_list_item = property_list_item_data.to_dict()
                property_list.append(property_list_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if property_list is not UNSET:
            field_dict["property_list"] = property_list

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.property_ import Property

        d = dict(src_dict)
        _property_list = d.pop("property_list", UNSET)
        property_list: list[Property] | Unset = UNSET
        if _property_list is not UNSET:
            property_list = []
            for property_list_item_data in _property_list:
                property_list_item = Property.from_dict(property_list_item_data)

                property_list.append(property_list_item)

        get_property_list_response_data = cls(
            property_list=property_list,
        )

        get_property_list_response_data.additional_properties = d
        return get_property_list_response_data

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
