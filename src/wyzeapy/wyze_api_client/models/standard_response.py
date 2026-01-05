from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.standard_response_data import StandardResponseData


T = TypeVar("T", bound="StandardResponse")


@_attrs_define
class StandardResponse:
    """
    Attributes:
        code (str | Unset): Response code
        msg (str | Unset): Response message
        data (StandardResponseData | Unset): Response data
    """

    code: str | Unset = UNSET
    msg: str | Unset = UNSET
    data: StandardResponseData | Unset = UNSET
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
        from ..models.standard_response_data import StandardResponseData

        d = dict(src_dict)
        code = d.pop("code", UNSET)

        msg = d.pop("msg", UNSET)

        _data = d.pop("data", UNSET)
        data: StandardResponseData | Unset
        if isinstance(_data, Unset):
            data = UNSET
        else:
            data = StandardResponseData.from_dict(_data)

        standard_response = cls(
            code=code,
            msg=msg,
            data=data,
        )

        standard_response.additional_properties = d
        return standard_response

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
