from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.stream_data_item_property import StreamDataItemProperty
    from ..models.stream_params import StreamParams


T = TypeVar("T", bound="StreamDataItem")


@_attrs_define
class StreamDataItem:
    """
    Attributes:
        device_id (str | Unset): Device MAC address
        provider (str | Unset): Stream provider
        property_ (StreamDataItemProperty | Unset): Device properties (iot-state, iot-power, etc.)
        params (StreamParams | Unset):
    """

    device_id: str | Unset = UNSET
    provider: str | Unset = UNSET
    property_: StreamDataItemProperty | Unset = UNSET
    params: StreamParams | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        device_id = self.device_id

        provider = self.provider

        property_: dict[str, Any] | Unset = UNSET
        if not isinstance(self.property_, Unset):
            property_ = self.property_.to_dict()

        params: dict[str, Any] | Unset = UNSET
        if not isinstance(self.params, Unset):
            params = self.params.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if device_id is not UNSET:
            field_dict["device_id"] = device_id
        if provider is not UNSET:
            field_dict["provider"] = provider
        if property_ is not UNSET:
            field_dict["property"] = property_
        if params is not UNSET:
            field_dict["params"] = params

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.stream_data_item_property import StreamDataItemProperty
        from ..models.stream_params import StreamParams

        d = dict(src_dict)
        device_id = d.pop("device_id", UNSET)

        provider = d.pop("provider", UNSET)

        _property_ = d.pop("property", UNSET)
        property_: StreamDataItemProperty | Unset
        if isinstance(_property_, Unset):
            property_ = UNSET
        else:
            property_ = StreamDataItemProperty.from_dict(_property_)

        _params = d.pop("params", UNSET)
        params: StreamParams | Unset
        if isinstance(_params, Unset):
            params = UNSET
        else:
            params = StreamParams.from_dict(_params)

        stream_data_item = cls(
            device_id=device_id,
            provider=provider,
            property_=property_,
            params=params,
        )

        stream_data_item.additional_properties = d
        return stream_data_item

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
