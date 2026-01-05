from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="GetEventListBody")


@_attrs_define
class GetEventListBody:
    """
    Attributes:
        phone_system_type (str | Unset): Phone system type (1 for Android) Example: 1.
        app_version (str | Unset): Application version Example: 2.18.43.
        app_ver (str | Unset): Full application version string Example: com.hualai.WyzeCam___2.18.43.
        app_name (str | Unset): Application name Example: com.hualai.WyzeCam.
        phone_id (UUID | Unset): Unique phone identifier
        sc (str | Unset): Security code
        sv (str | Unset): Security version
        ts (int | Unset): Unix timestamp in seconds
        access_token (str | Unset): User access token
        count (int | Unset): Number of events to retrieve
        begin_time (int | Unset):
        end_time (int | Unset):
        event_type (str | Unset):
        event_value_list (list[str] | Unset):
        device_mac_list (list[str] | Unset):
        order_by (int | Unset):
    """

    phone_system_type: str | Unset = UNSET
    app_version: str | Unset = UNSET
    app_ver: str | Unset = UNSET
    app_name: str | Unset = UNSET
    phone_id: UUID | Unset = UNSET
    sc: str | Unset = UNSET
    sv: str | Unset = UNSET
    ts: int | Unset = UNSET
    access_token: str | Unset = UNSET
    count: int | Unset = UNSET
    begin_time: int | Unset = UNSET
    end_time: int | Unset = UNSET
    event_type: str | Unset = UNSET
    event_value_list: list[str] | Unset = UNSET
    device_mac_list: list[str] | Unset = UNSET
    order_by: int | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
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

        count = self.count

        begin_time = self.begin_time

        end_time = self.end_time

        event_type = self.event_type

        event_value_list: list[str] | Unset = UNSET
        if not isinstance(self.event_value_list, Unset):
            event_value_list = self.event_value_list

        device_mac_list: list[str] | Unset = UNSET
        if not isinstance(self.device_mac_list, Unset):
            device_mac_list = self.device_mac_list

        order_by = self.order_by

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
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
        if count is not UNSET:
            field_dict["count"] = count
        if begin_time is not UNSET:
            field_dict["begin_time"] = begin_time
        if end_time is not UNSET:
            field_dict["end_time"] = end_time
        if event_type is not UNSET:
            field_dict["event_type"] = event_type
        if event_value_list is not UNSET:
            field_dict["event_value_list"] = event_value_list
        if device_mac_list is not UNSET:
            field_dict["device_mac_list"] = device_mac_list
        if order_by is not UNSET:
            field_dict["order_by"] = order_by

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
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

        count = d.pop("count", UNSET)

        begin_time = d.pop("begin_time", UNSET)

        end_time = d.pop("end_time", UNSET)

        event_type = d.pop("event_type", UNSET)

        event_value_list = cast(list[str], d.pop("event_value_list", UNSET))

        device_mac_list = cast(list[str], d.pop("device_mac_list", UNSET))

        order_by = d.pop("order_by", UNSET)

        get_event_list_body = cls(
            phone_system_type=phone_system_type,
            app_version=app_version,
            app_ver=app_ver,
            app_name=app_name,
            phone_id=phone_id,
            sc=sc,
            sv=sv,
            ts=ts,
            access_token=access_token,
            count=count,
            begin_time=begin_time,
            end_time=end_time,
            event_type=event_type,
            event_value_list=event_value_list,
            device_mac_list=device_mac_list,
            order_by=order_by,
        )

        get_event_list_body.additional_properties = d
        return get_event_list_body

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
