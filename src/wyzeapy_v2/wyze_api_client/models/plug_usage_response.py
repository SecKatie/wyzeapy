from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.plug_usage_response_data import PlugUsageResponseData


T = TypeVar("T", bound="PlugUsageResponse")


@_attrs_define
class PlugUsageResponse:
    """
    Attributes:
        code (str | Unset):
        msg (str | Unset):
        data (PlugUsageResponseData | Unset):
    """

    code: str | Unset = UNSET
    msg: str | Unset = UNSET
    data: PlugUsageResponseData | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        code = self.code

        msg = self.msg

        data: dict[str, Any] | Unset = UNSET
        if not isinstance(self.data, Unset):
            data = self.data.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if code is not UNSET:
            field_dict["code"] = code
        if msg is not UNSET:
            field_dict["msg"] = msg
        if data is not UNSET:
            field_dict["data"] = data

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.plug_usage_response_data import PlugUsageResponseData

        d = dict(src_dict)
        code = d.pop("code", UNSET)

        msg = d.pop("msg", UNSET)

        _data = d.pop("data", UNSET)
        data: PlugUsageResponseData | Unset
        if isinstance(_data, Unset):
            data = UNSET
        else:
            data = PlugUsageResponseData.from_dict(_data)

        plug_usage_response = cls(
            code=code,
            msg=msg,
            data=data,
        )

        plug_usage_response.additional_properties = d
        return plug_usage_response

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
