from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.lock_info_request_with_keypad import LockInfoRequestWithKeypad
from ..types import UNSET, Unset

T = TypeVar("T", bound="LockInfoRequest")


@_attrs_define
class LockInfoRequest:
    """
    Attributes:
        uuid (str):
        access_token (str):
        key (str):
        timestamp (str):
        sign (str):
        with_keypad (LockInfoRequestWithKeypad | Unset):
    """

    uuid: str
    access_token: str
    key: str
    timestamp: str
    sign: str
    with_keypad: LockInfoRequestWithKeypad | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        uuid = self.uuid

        access_token = self.access_token

        key = self.key

        timestamp = self.timestamp

        sign = self.sign

        with_keypad: str | Unset = UNSET
        if not isinstance(self.with_keypad, Unset):
            with_keypad = self.with_keypad.value

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "uuid": uuid,
                "access_token": access_token,
                "key": key,
                "timestamp": timestamp,
                "sign": sign,
            }
        )
        if with_keypad is not UNSET:
            field_dict["with_keypad"] = with_keypad

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        uuid = d.pop("uuid")

        access_token = d.pop("access_token")

        key = d.pop("key")

        timestamp = d.pop("timestamp")

        sign = d.pop("sign")

        _with_keypad = d.pop("with_keypad", UNSET)
        with_keypad: LockInfoRequestWithKeypad | Unset
        if isinstance(_with_keypad, Unset):
            with_keypad = UNSET
        else:
            with_keypad = LockInfoRequestWithKeypad(_with_keypad)

        lock_info_request = cls(
            uuid=uuid,
            access_token=access_token,
            key=key,
            timestamp=timestamp,
            sign=sign,
            with_keypad=with_keypad,
        )

        lock_info_request.additional_properties = d
        return lock_info_request

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
