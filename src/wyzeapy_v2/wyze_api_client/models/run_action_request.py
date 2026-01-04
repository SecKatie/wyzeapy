from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.run_action_request_action_key import RunActionRequestActionKey
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.run_action_request_action_params import RunActionRequestActionParams


T = TypeVar("T", bound="RunActionRequest")


@_attrs_define
class RunActionRequest:
    """
    Attributes:
        provider_key (str): Device product model
        instance_id (str): Device MAC address
        action_key (RunActionRequestActionKey): Action to perform
        phone_system_type (str | Unset): Phone system type (1 for Android) Example: 1.
        app_version (str | Unset): Application version Example: 2.18.43.
        app_ver (str | Unset): Full application version string Example: com.hualai.WyzeCam___2.18.43.
        app_name (str | Unset): Application name Example: com.hualai.WyzeCam.
        phone_id (UUID | Unset): Unique phone identifier
        sc (str | Unset): Security code
        sv (str | Unset): Security version
        ts (int | Unset): Unix timestamp in seconds
        access_token (str | Unset): User access token
        action_params (RunActionRequestActionParams | Unset):
        custom_string (str | Unset):
    """

    provider_key: str
    instance_id: str
    action_key: RunActionRequestActionKey
    phone_system_type: str | Unset = UNSET
    app_version: str | Unset = UNSET
    app_ver: str | Unset = UNSET
    app_name: str | Unset = UNSET
    phone_id: UUID | Unset = UNSET
    sc: str | Unset = UNSET
    sv: str | Unset = UNSET
    ts: int | Unset = UNSET
    access_token: str | Unset = UNSET
    action_params: RunActionRequestActionParams | Unset = UNSET
    custom_string: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        provider_key = self.provider_key

        instance_id = self.instance_id

        action_key = self.action_key.value

        phone_system_type = self.phone_system_type

        app_version = self.app_version

        app_ver = self.app_ver

        app_name = self.app_name

        phone_id: str | Unset = UNSET
        if not isinstance(self.phone_id, Unset):
            phone_id = str(self.phone_id)

        sc = self.sc

        sv = self.sv

        ts = self.ts

        access_token = self.access_token

        action_params: dict[str, Any] | Unset = UNSET
        if not isinstance(self.action_params, Unset):
            action_params = self.action_params.to_dict()

        custom_string = self.custom_string

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "provider_key": provider_key,
                "instance_id": instance_id,
                "action_key": action_key,
            }
        )
        if phone_system_type is not UNSET:
            field_dict["phone_system_type"] = phone_system_type
        if app_version is not UNSET:
            field_dict["app_version"] = app_version
        if app_ver is not UNSET:
            field_dict["app_ver"] = app_ver
        if app_name is not UNSET:
            field_dict["app_name"] = app_name
        if phone_id is not UNSET:
            field_dict["phone_id"] = phone_id
        if sc is not UNSET:
            field_dict["sc"] = sc
        if sv is not UNSET:
            field_dict["sv"] = sv
        if ts is not UNSET:
            field_dict["ts"] = ts
        if access_token is not UNSET:
            field_dict["access_token"] = access_token
        if action_params is not UNSET:
            field_dict["action_params"] = action_params
        if custom_string is not UNSET:
            field_dict["custom_string"] = custom_string

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.run_action_request_action_params import RunActionRequestActionParams

        d = dict(src_dict)
        provider_key = d.pop("provider_key")

        instance_id = d.pop("instance_id")

        action_key = RunActionRequestActionKey(d.pop("action_key"))

        phone_system_type = d.pop("phone_system_type", UNSET)

        app_version = d.pop("app_version", UNSET)

        app_ver = d.pop("app_ver", UNSET)

        app_name = d.pop("app_name", UNSET)

        _phone_id = d.pop("phone_id", UNSET)
        phone_id: UUID | Unset
        if isinstance(_phone_id, Unset):
            phone_id = UNSET
        else:
            phone_id = UUID(_phone_id)

        sc = d.pop("sc", UNSET)

        sv = d.pop("sv", UNSET)

        ts = d.pop("ts", UNSET)

        access_token = d.pop("access_token", UNSET)

        _action_params = d.pop("action_params", UNSET)
        action_params: RunActionRequestActionParams | Unset
        if isinstance(_action_params, Unset):
            action_params = UNSET
        else:
            action_params = RunActionRequestActionParams.from_dict(_action_params)

        custom_string = d.pop("custom_string", UNSET)

        run_action_request = cls(
            provider_key=provider_key,
            instance_id=instance_id,
            action_key=action_key,
            phone_system_type=phone_system_type,
            app_version=app_version,
            app_ver=app_ver,
            app_name=app_name,
            phone_id=phone_id,
            sc=sc,
            sv=sv,
            ts=ts,
            access_token=access_token,
            action_params=action_params,
            custom_string=custom_string,
        )

        run_action_request.additional_properties = d
        return run_action_request

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
