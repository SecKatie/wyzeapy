from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.hms_state_status_response_message import HMSStateStatusResponseMessage
from ..types import UNSET, Unset

T = TypeVar("T", bound="HMSStateStatusResponse")


@_attrs_define
class HMSStateStatusResponse:
    """
    Attributes:
        message (HMSStateStatusResponseMessage | Unset):
    """

    message: HMSStateStatusResponseMessage | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        message: str | Unset = UNSET
        if not isinstance(self.message, Unset):
            message = self.message.value

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if message is not UNSET:
            field_dict["message"] = message

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        _message = d.pop("message", UNSET)
        message: HMSStateStatusResponseMessage | Unset
        if isinstance(_message, Unset):
            message = UNSET
        else:
            message = HMSStateStatusResponseMessage(_message)

        hms_state_status_response = cls(
            message=message,
        )

        hms_state_status_response.additional_properties = d
        return hms_state_status_response

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
