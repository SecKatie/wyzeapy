from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.get_object_list_response_data import GetObjectListResponseData


T = TypeVar("T", bound="GetObjectListResponse")


@_attrs_define
class GetObjectListResponse:
    """
    Attributes:
        code (str | Unset):
        msg (str | Unset):
        data (GetObjectListResponseData | Unset):
    """

    code: str | Unset = UNSET
    msg: str | Unset = UNSET
    data: GetObjectListResponseData | Unset = UNSET
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
        from ..models.get_object_list_response_data import GetObjectListResponseData

        d = dict(src_dict)
        code = d.pop("code", UNSET)

        msg = d.pop("msg", UNSET)

        _data = d.pop("data", UNSET)
        data: GetObjectListResponseData | Unset
        if isinstance(_data, Unset):
            data = UNSET
        else:
            data = GetObjectListResponseData.from_dict(_data)

        get_object_list_response = cls(
            code=code,
            msg=msg,
            data=data,
        )

        get_object_list_response.additional_properties = d
        return get_object_list_response

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
