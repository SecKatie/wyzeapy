from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="GetIrrigationIotPropResponse200DataProps")


@_attrs_define
class GetIrrigationIotPropResponse200DataProps:
    """
    Attributes:
        rssi (int | Unset):
        ip (str | Unset):
        sn (str | Unset):
        ssid (str | Unset):
        iot_state (str | Unset):
    """

    rssi: int | Unset = UNSET
    ip: str | Unset = UNSET
    sn: str | Unset = UNSET
    ssid: str | Unset = UNSET
    iot_state: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        rssi = self.rssi

        ip = self.ip

        sn = self.sn

        ssid = self.ssid

        iot_state = self.iot_state

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if rssi is not UNSET:
            field_dict["RSSI"] = rssi
        if ip is not UNSET:
            field_dict["IP"] = ip
        if sn is not UNSET:
            field_dict["sn"] = sn
        if ssid is not UNSET:
            field_dict["ssid"] = ssid
        if iot_state is not UNSET:
            field_dict["iot_state"] = iot_state

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        rssi = d.pop("RSSI", UNSET)

        ip = d.pop("IP", UNSET)

        sn = d.pop("sn", UNSET)

        ssid = d.pop("ssid", UNSET)

        iot_state = d.pop("iot_state", UNSET)

        get_irrigation_iot_prop_response_200_data_props = cls(
            rssi=rssi,
            ip=ip,
            sn=sn,
            ssid=ssid,
            iot_state=iot_state,
        )

        get_irrigation_iot_prop_response_200_data_props.additional_properties = d
        return get_irrigation_iot_prop_response_200_data_props

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
