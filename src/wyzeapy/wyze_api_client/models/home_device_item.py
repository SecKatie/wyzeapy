from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.home_device_param import HomeDeviceParam
    from ..models.home_device_property import HomeDeviceProperty


T = TypeVar("T", bound="HomeDeviceItem")


@_attrs_define
class HomeDeviceItem:
    """
    Attributes:
        device_id (str | Unset): Device MAC address or unique identifier
        device_param (HomeDeviceParam | Unset):
        is_favorite (int | Unset): Whether device is favorited (1=yes, 0=no)
        nickname (str | Unset): User-assigned device name
        device_model (str | Unset): Device model identifier
        device_category (str | Unset): Device category (Camera, gateway, ChimeSensor, etc.)
        property_ (HomeDeviceProperty | Unset): Device properties (varies by device type)
        role (int | Unset):
        sort_id (int | Unset):
        favorite_order (int | Unset):
        device_order (int | Unset):
    """

    device_id: str | Unset = UNSET
    device_param: HomeDeviceParam | Unset = UNSET
    is_favorite: int | Unset = UNSET
    nickname: str | Unset = UNSET
    device_model: str | Unset = UNSET
    device_category: str | Unset = UNSET
    property_: HomeDeviceProperty | Unset = UNSET
    role: int | Unset = UNSET
    sort_id: int | Unset = UNSET
    favorite_order: int | Unset = UNSET
    device_order: int | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        device_id = self.device_id

        device_param: dict[str, Any] | Unset = UNSET
        if not isinstance(self.device_param, Unset):
            device_param = self.device_param.to_dict()

        is_favorite = self.is_favorite

        nickname = self.nickname

        device_model = self.device_model

        device_category = self.device_category

        property_: dict[str, Any] | Unset = UNSET
        if not isinstance(self.property_, Unset):
            property_ = self.property_.to_dict()

        role = self.role

        sort_id = self.sort_id

        favorite_order = self.favorite_order

        device_order = self.device_order

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if device_id is not UNSET:
            field_dict["device_id"] = device_id
        if device_param is not UNSET:
            field_dict["device_param"] = device_param
        if is_favorite is not UNSET:
            field_dict["is_favorite"] = is_favorite
        if nickname is not UNSET:
            field_dict["nickname"] = nickname
        if device_model is not UNSET:
            field_dict["device_model"] = device_model
        if device_category is not UNSET:
            field_dict["device_category"] = device_category
        if property_ is not UNSET:
            field_dict["property"] = property_
        if role is not UNSET:
            field_dict["role"] = role
        if sort_id is not UNSET:
            field_dict["sort_id"] = sort_id
        if favorite_order is not UNSET:
            field_dict["favorite_order"] = favorite_order
        if device_order is not UNSET:
            field_dict["device_order"] = device_order

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.home_device_param import HomeDeviceParam
        from ..models.home_device_property import HomeDeviceProperty

        d = dict(src_dict)
        device_id = d.pop("device_id", UNSET)

        _device_param = d.pop("device_param", UNSET)
        device_param: HomeDeviceParam | Unset
        if isinstance(_device_param, Unset):
            device_param = UNSET
        else:
            device_param = HomeDeviceParam.from_dict(_device_param)

        is_favorite = d.pop("is_favorite", UNSET)

        nickname = d.pop("nickname", UNSET)

        device_model = d.pop("device_model", UNSET)

        device_category = d.pop("device_category", UNSET)

        _property_ = d.pop("property", UNSET)
        property_: HomeDeviceProperty | Unset
        if isinstance(_property_, Unset):
            property_ = UNSET
        else:
            property_ = HomeDeviceProperty.from_dict(_property_)

        role = d.pop("role", UNSET)

        sort_id = d.pop("sort_id", UNSET)

        favorite_order = d.pop("favorite_order", UNSET)

        device_order = d.pop("device_order", UNSET)

        home_device_item = cls(
            device_id=device_id,
            device_param=device_param,
            is_favorite=is_favorite,
            nickname=nickname,
            device_model=device_model,
            device_category=device_category,
            property_=property_,
            role=role,
            sort_id=sort_id,
            favorite_order=favorite_order,
            device_order=device_order,
        )

        home_device_item.additional_properties = d
        return home_device_item

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
