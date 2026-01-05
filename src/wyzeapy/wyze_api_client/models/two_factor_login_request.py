from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.two_factor_login_request_mfa_type import TwoFactorLoginRequestMfaType

T = TypeVar("T", bound="TwoFactorLoginRequest")


@_attrs_define
class TwoFactorLoginRequest:
    """
    Attributes:
        email (str):
        password (str):
        mfa_type (TwoFactorLoginRequestMfaType):
        verification_id (str): App ID for TOTP or session ID for SMS
        verification_code (str): 6-digit verification code
    """

    email: str
    password: str
    mfa_type: TwoFactorLoginRequestMfaType
    verification_id: str
    verification_code: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        email = self.email

        password = self.password

        mfa_type = self.mfa_type.value

        verification_id = self.verification_id

        verification_code = self.verification_code

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "email": email,
                "password": password,
                "mfa_type": mfa_type,
                "verification_id": verification_id,
                "verification_code": verification_code,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        email = d.pop("email")

        password = d.pop("password")

        mfa_type = TwoFactorLoginRequestMfaType(d.pop("mfa_type"))

        verification_id = d.pop("verification_id")

        verification_code = d.pop("verification_code")

        two_factor_login_request = cls(
            email=email,
            password=password,
            mfa_type=mfa_type,
            verification_id=verification_id,
            verification_code=verification_code,
        )

        two_factor_login_request.additional_properties = d
        return two_factor_login_request

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
