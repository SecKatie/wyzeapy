from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="HomeDeviceParamThumbnail")


@_attrs_define
class HomeDeviceParamThumbnail:
    """
    Attributes:
        rotate (int | Unset):
        width (int | Unset):
        height (int | Unset):
        ts (int | Unset):
        url (str | Unset):
    """

    rotate: int | Unset = UNSET
    width: int | Unset = UNSET
    height: int | Unset = UNSET
    ts: int | Unset = UNSET
    url: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        rotate = self.rotate

        width = self.width

        height = self.height

        ts = self.ts

        url = self.url

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if rotate is not UNSET:
            field_dict["rotate"] = rotate
        if width is not UNSET:
            field_dict["width"] = width
        if height is not UNSET:
            field_dict["height"] = height
        if ts is not UNSET:
            field_dict["ts"] = ts
        if url is not UNSET:
            field_dict["url"] = url

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        rotate = d.pop("rotate", UNSET)

        width = d.pop("width", UNSET)

        height = d.pop("height", UNSET)

        ts = d.pop("ts", UNSET)

        url = d.pop("url", UNSET)

        home_device_param_thumbnail = cls(
            rotate=rotate,
            width=width,
            height=height,
            ts=ts,
            url=url,
        )

        home_device_param_thumbnail.additional_properties = d
        return home_device_param_thumbnail

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
