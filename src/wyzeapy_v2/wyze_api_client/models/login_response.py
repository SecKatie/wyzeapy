from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.login_response_mfa_details_type_0 import LoginResponseMfaDetailsType0


T = TypeVar("T", bound="LoginResponse")


@_attrs_define
class LoginResponse:
    """
    Attributes:
        access_token (str | Unset): Access token for API calls
        refresh_token (str | Unset): Token to refresh access token
        user_id (str | Unset): User identifier
        mfa_options (list[str] | Unset): Available MFA options if 2FA required
        mfa_details (LoginResponseMfaDetailsType0 | None | Unset): MFA details if 2FA required
        sms_session_id (str | Unset): SMS session ID for SMS 2FA
    """

    access_token: str | Unset = UNSET
    refresh_token: str | Unset = UNSET
    user_id: str | Unset = UNSET
    mfa_options: list[str] | Unset = UNSET
    mfa_details: LoginResponseMfaDetailsType0 | None | Unset = UNSET
    sms_session_id: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.login_response_mfa_details_type_0 import (
            LoginResponseMfaDetailsType0,
        )

        access_token = self.access_token

        refresh_token = self.refresh_token

        user_id = self.user_id

        mfa_options: list[str] | Unset = UNSET
        if not isinstance(self.mfa_options, Unset):
            mfa_options = self.mfa_options

        mfa_details: dict[str, Any] | None | Unset
        if isinstance(self.mfa_details, Unset):
            mfa_details = UNSET
        elif isinstance(self.mfa_details, LoginResponseMfaDetailsType0):
            mfa_details = self.mfa_details.to_dict()
        else:
            mfa_details = self.mfa_details

        sms_session_id = self.sms_session_id

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if access_token is not UNSET:
            field_dict["access_token"] = access_token
        if refresh_token is not UNSET:
            field_dict["refresh_token"] = refresh_token
        if user_id is not UNSET:
            field_dict["user_id"] = user_id
        if mfa_options is not UNSET:
            field_dict["mfa_options"] = mfa_options
        if mfa_details is not UNSET:
            field_dict["mfa_details"] = mfa_details
        if sms_session_id is not UNSET:
            field_dict["sms_session_id"] = sms_session_id

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.login_response_mfa_details_type_0 import (
            LoginResponseMfaDetailsType0,
        )

        d = dict(src_dict)
        access_token = d.pop("access_token", UNSET)

        refresh_token = d.pop("refresh_token", UNSET)

        user_id = d.pop("user_id", UNSET)

        mfa_options = cast(list[str], d.pop("mfa_options", UNSET))

        def _parse_mfa_details(
            data: object,
        ) -> LoginResponseMfaDetailsType0 | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                mfa_details_type_0 = LoginResponseMfaDetailsType0.from_dict(data)

                return mfa_details_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(LoginResponseMfaDetailsType0 | None | Unset, data)

        mfa_details = _parse_mfa_details(d.pop("mfa_details", UNSET))

        sms_session_id = d.pop("sms_session_id", UNSET)

        login_response = cls(
            access_token=access_token,
            refresh_token=refresh_token,
            user_id=user_id,
            mfa_options=mfa_options,
            mfa_details=mfa_details,
            sms_session_id=sms_session_id,
        )

        login_response.additional_properties = d
        return login_response

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
