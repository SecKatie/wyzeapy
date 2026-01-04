from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.lock_control_request_action import LockControlRequestAction

T = TypeVar("T", bound="LockControlRequest")


@_attrs_define
class LockControlRequest:
    """
    Attributes:
        uuid (str): Lock UUID
        action (LockControlRequestAction):
        access_token (str):
        key (str): Ford app key
        timestamp (str): Timestamp in milliseconds
        sign (str): Request signature
    """

    uuid: str
    action: LockControlRequestAction
    access_token: str
    key: str
    timestamp: str
    sign: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        uuid = self.uuid

        action = self.action.value

        access_token = self.access_token

        key = self.key

        timestamp = self.timestamp

        sign = self.sign

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "uuid": uuid,
                "action": action,
                "access_token": access_token,
                "key": key,
                "timestamp": timestamp,
                "sign": sign,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        uuid = d.pop("uuid")

        action = LockControlRequestAction(d.pop("action"))

        access_token = d.pop("access_token")

        key = d.pop("key")

        timestamp = d.pop("timestamp")

        sign = d.pop("sign")

        lock_control_request = cls(
            uuid=uuid,
            action=action,
            access_token=access_token,
            key=key,
            timestamp=timestamp,
            sign=sign,
        )

        lock_control_request.additional_properties = d
        return lock_control_request

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
