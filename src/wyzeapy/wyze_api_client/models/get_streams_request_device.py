from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="GetStreamsRequestDevice")


@_attrs_define
class GetStreamsRequestDevice:
    """
    Attributes:
        device_id (str): Device MAC address
        device_model (str): Device model identifier
        provider (str): Stream provider (typically 'tutk') Default: 'tutk'.
    """

    device_id: str
    device_model: str
    provider: str = "tutk"
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        device_id = self.device_id

        device_model = self.device_model

        provider = self.provider

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "device_id": device_id,
                "device_model": device_model,
                "provider": provider,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        device_id = d.pop("device_id")

        device_model = d.pop("device_model")

        provider = d.pop("provider")

        get_streams_request_device = cls(
            device_id=device_id,
            device_model=device_model,
            provider=provider,
        )

        get_streams_request_device.additional_properties = d
        return get_streams_request_device

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
