from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.irrigation_stop_request_action import IrrigationStopRequestAction

T = TypeVar("T", bound="IrrigationStopRequest")


@_attrs_define
class IrrigationStopRequest:
    """
    Attributes:
        device_id (str):
        nonce (str):
        action (IrrigationStopRequestAction):
    """

    device_id: str
    nonce: str
    action: IrrigationStopRequestAction
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        device_id = self.device_id

        nonce = self.nonce

        action = self.action.value

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "device_id": device_id,
                "nonce": nonce,
                "action": action,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        device_id = d.pop("device_id")

        nonce = d.pop("nonce")

        action = IrrigationStopRequestAction(d.pop("action"))

        irrigation_stop_request = cls(
            device_id=device_id,
            nonce=nonce,
            action=action,
        )

        irrigation_stop_request.additional_properties = d
        return irrigation_stop_request

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
