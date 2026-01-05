from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.send_sms_code_body_mfa_phone_type import SendSmsCodeBodyMfaPhoneType
from ..types import UNSET, Unset

T = TypeVar("T", bound="SendSmsCodeBody")


@_attrs_define
class SendSmsCodeBody:
    """
    Attributes:
        mfa_phone_type (SendSmsCodeBodyMfaPhoneType | Unset):
        session_id (str | Unset):
        user_id (str | Unset):
    """

    mfa_phone_type: SendSmsCodeBodyMfaPhoneType | Unset = UNSET
    session_id: str | Unset = UNSET
    user_id: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        mfa_phone_type: str | Unset = UNSET
        if not isinstance(self.mfa_phone_type, Unset):
            mfa_phone_type = self.mfa_phone_type.value

        session_id = self.session_id

        user_id = self.user_id

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if mfa_phone_type is not UNSET:
            field_dict["mfaPhoneType"] = mfa_phone_type
        if session_id is not UNSET:
            field_dict["sessionId"] = session_id
        if user_id is not UNSET:
            field_dict["userId"] = user_id

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        _mfa_phone_type = d.pop("mfaPhoneType", UNSET)
        mfa_phone_type: SendSmsCodeBodyMfaPhoneType | Unset
        if isinstance(_mfa_phone_type, Unset):
            mfa_phone_type = UNSET
        else:
            mfa_phone_type = SendSmsCodeBodyMfaPhoneType(_mfa_phone_type)

        session_id = d.pop("sessionId", UNSET)

        user_id = d.pop("userId", UNSET)

        send_sms_code_body = cls(
            mfa_phone_type=mfa_phone_type,
            session_id=session_id,
            user_id=user_id,
        )

        send_sms_code_body.additional_properties = d
        return send_sms_code_body

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
