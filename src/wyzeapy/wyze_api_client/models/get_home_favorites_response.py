from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.home_favorites_data import HomeFavoritesData


T = TypeVar("T", bound="GetHomeFavoritesResponse")


@_attrs_define
class GetHomeFavoritesResponse:
    """
    Attributes:
        code (str | Unset): Response code (1 for success)
        ts (int | Unset): Server timestamp
        msg (str | Unset): Response message
        data (HomeFavoritesData | Unset):
        trace_id (str | Unset):
    """

    code: str | Unset = UNSET
    ts: int | Unset = UNSET
    msg: str | Unset = UNSET
    data: HomeFavoritesData | Unset = UNSET
    trace_id: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        code = self.code

        ts = self.ts

        msg = self.msg

        data: dict[str, Any] | Unset = UNSET
        if not isinstance(self.data, Unset):
            data = self.data.to_dict()

        trace_id = self.trace_id

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if code is not UNSET:
            field_dict["code"] = code
        if ts is not UNSET:
            field_dict["ts"] = ts
        if msg is not UNSET:
            field_dict["msg"] = msg
        if data is not UNSET:
            field_dict["data"] = data
        if trace_id is not UNSET:
            field_dict["traceId"] = trace_id

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.home_favorites_data import HomeFavoritesData

        d = dict(src_dict)
        code = d.pop("code", UNSET)

        ts = d.pop("ts", UNSET)

        msg = d.pop("msg", UNSET)

        _data = d.pop("data", UNSET)
        data: HomeFavoritesData | Unset
        if isinstance(_data, Unset):
            data = UNSET
        else:
            data = HomeFavoritesData.from_dict(_data)

        trace_id = d.pop("traceId", UNSET)

        get_home_favorites_response = cls(
            code=code,
            ts=ts,
            msg=msg,
            data=data,
            trace_id=trace_id,
        )

        get_home_favorites_response.additional_properties = d
        return get_home_favorites_response

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
