from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.stream_data_item import StreamDataItem


T = TypeVar("T", bound="GetStreamsResponse")


@_attrs_define
class GetStreamsResponse:
    """
    Attributes:
        code (str | Unset): Response code (1 for success)
        ts (int | Unset): Server timestamp
        msg (str | Unset): Response message
        data (list[StreamDataItem] | Unset):
        trace_id (str | Unset):
    """

    code: str | Unset = UNSET
    ts: int | Unset = UNSET
    msg: str | Unset = UNSET
    data: list[StreamDataItem] | Unset = UNSET
    trace_id: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        code = self.code

        ts = self.ts

        msg = self.msg

        data: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.data, Unset):
            data = []
            for data_item_data in self.data:
                data_item = data_item_data.to_dict()
                data.append(data_item)

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
        from ..models.stream_data_item import StreamDataItem

        d = dict(src_dict)
        code = d.pop("code", UNSET)

        ts = d.pop("ts", UNSET)

        msg = d.pop("msg", UNSET)

        _data = d.pop("data", UNSET)
        data: list[StreamDataItem] | Unset = UNSET
        if _data is not UNSET:
            data = []
            for data_item_data in _data:
                data_item = StreamDataItem.from_dict(data_item_data)

                data.append(data_item)

        trace_id = d.pop("traceId", UNSET)

        get_streams_response = cls(
            code=code,
            ts=ts,
            msg=msg,
            data=data,
            trace_id=trace_id,
        )

        get_streams_response.additional_properties = d
        return get_streams_response

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
