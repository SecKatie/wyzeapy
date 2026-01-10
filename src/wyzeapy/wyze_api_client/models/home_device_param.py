from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.home_device_param_p2p import HomeDeviceParamP2P
    from ..models.home_device_param_thumbnail import HomeDeviceParamThumbnail


T = TypeVar("T", bound="HomeDeviceParam")


@_attrs_define
class HomeDeviceParam:
    """
    Attributes:
        firmware_version (str | Unset):
        hardware_version (str | Unset):
        thumbnail (HomeDeviceParamThumbnail | Unset):
        p2p (HomeDeviceParamP2P | Unset):
    """

    firmware_version: str | Unset = UNSET
    hardware_version: str | Unset = UNSET
    thumbnail: HomeDeviceParamThumbnail | Unset = UNSET
    p2p: HomeDeviceParamP2P | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        firmware_version = self.firmware_version

        hardware_version = self.hardware_version

        thumbnail: dict[str, Any] | Unset = UNSET
        if not isinstance(self.thumbnail, Unset):
            thumbnail = self.thumbnail.to_dict()

        p2p: dict[str, Any] | Unset = UNSET
        if not isinstance(self.p2p, Unset):
            p2p = self.p2p.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if firmware_version is not UNSET:
            field_dict["firmware_version"] = firmware_version
        if hardware_version is not UNSET:
            field_dict["hardware_version"] = hardware_version
        if thumbnail is not UNSET:
            field_dict["thumbnail"] = thumbnail
        if p2p is not UNSET:
            field_dict["p2p"] = p2p

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.home_device_param_p2p import HomeDeviceParamP2P
        from ..models.home_device_param_thumbnail import HomeDeviceParamThumbnail

        d = dict(src_dict)
        firmware_version = d.pop("firmware_version", UNSET)

        hardware_version = d.pop("hardware_version", UNSET)

        _thumbnail = d.pop("thumbnail", UNSET)
        thumbnail: HomeDeviceParamThumbnail | Unset
        if isinstance(_thumbnail, Unset):
            thumbnail = UNSET
        else:
            thumbnail = HomeDeviceParamThumbnail.from_dict(_thumbnail)

        _p2p = d.pop("p2p", UNSET)
        p2p: HomeDeviceParamP2P | Unset
        if isinstance(_p2p, Unset):
            p2p = UNSET
        else:
            p2p = HomeDeviceParamP2P.from_dict(_p2p)

        home_device_param = cls(
            firmware_version=firmware_version,
            hardware_version=hardware_version,
            thumbnail=thumbnail,
            p2p=p2p,
        )

        home_device_param.additional_properties = d
        return home_device_param

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
