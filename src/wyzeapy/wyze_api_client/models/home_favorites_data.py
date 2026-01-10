from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.home_device_item import HomeDeviceItem
    from ..models.home_favorites_data_app_settings_item import HomeFavoritesDataAppSettingsItem
    from ..models.home_favorites_data_device_group_list_item import HomeFavoritesDataDeviceGroupListItem


T = TypeVar("T", bound="HomeFavoritesData")


@_attrs_define
class HomeFavoritesData:
    """
    Attributes:
        id (str | Unset): Home ID
        name (str | Unset): Home name
        device_group_list (list[HomeFavoritesDataDeviceGroupListItem] | Unset):
        device_list (list[HomeDeviceItem] | Unset):
        app_settings (list[HomeFavoritesDataAppSettingsItem] | Unset):
        sort_type (int | Unset):
        sort_direction (int | Unset):
    """

    id: str | Unset = UNSET
    name: str | Unset = UNSET
    device_group_list: list[HomeFavoritesDataDeviceGroupListItem] | Unset = UNSET
    device_list: list[HomeDeviceItem] | Unset = UNSET
    app_settings: list[HomeFavoritesDataAppSettingsItem] | Unset = UNSET
    sort_type: int | Unset = UNSET
    sort_direction: int | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        name = self.name

        device_group_list: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.device_group_list, Unset):
            device_group_list = []
            for device_group_list_item_data in self.device_group_list:
                device_group_list_item = device_group_list_item_data.to_dict()
                device_group_list.append(device_group_list_item)

        device_list: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.device_list, Unset):
            device_list = []
            for device_list_item_data in self.device_list:
                device_list_item = device_list_item_data.to_dict()
                device_list.append(device_list_item)

        app_settings: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.app_settings, Unset):
            app_settings = []
            for app_settings_item_data in self.app_settings:
                app_settings_item = app_settings_item_data.to_dict()
                app_settings.append(app_settings_item)

        sort_type = self.sort_type

        sort_direction = self.sort_direction

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if id is not UNSET:
            field_dict["id"] = id
        if name is not UNSET:
            field_dict["name"] = name
        if device_group_list is not UNSET:
            field_dict["device_group_list"] = device_group_list
        if device_list is not UNSET:
            field_dict["device_list"] = device_list
        if app_settings is not UNSET:
            field_dict["app_settings"] = app_settings
        if sort_type is not UNSET:
            field_dict["sort_type"] = sort_type
        if sort_direction is not UNSET:
            field_dict["sort_direction"] = sort_direction

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.home_device_item import HomeDeviceItem
        from ..models.home_favorites_data_app_settings_item import HomeFavoritesDataAppSettingsItem
        from ..models.home_favorites_data_device_group_list_item import HomeFavoritesDataDeviceGroupListItem

        d = dict(src_dict)
        id = d.pop("id", UNSET)

        name = d.pop("name", UNSET)

        _device_group_list = d.pop("device_group_list", UNSET)
        device_group_list: list[HomeFavoritesDataDeviceGroupListItem] | Unset = UNSET
        if _device_group_list is not UNSET:
            device_group_list = []
            for device_group_list_item_data in _device_group_list:
                device_group_list_item = HomeFavoritesDataDeviceGroupListItem.from_dict(device_group_list_item_data)

                device_group_list.append(device_group_list_item)

        _device_list = d.pop("device_list", UNSET)
        device_list: list[HomeDeviceItem] | Unset = UNSET
        if _device_list is not UNSET:
            device_list = []
            for device_list_item_data in _device_list:
                device_list_item = HomeDeviceItem.from_dict(device_list_item_data)

                device_list.append(device_list_item)

        _app_settings = d.pop("app_settings", UNSET)
        app_settings: list[HomeFavoritesDataAppSettingsItem] | Unset = UNSET
        if _app_settings is not UNSET:
            app_settings = []
            for app_settings_item_data in _app_settings:
                app_settings_item = HomeFavoritesDataAppSettingsItem.from_dict(app_settings_item_data)

                app_settings.append(app_settings_item)

        sort_type = d.pop("sort_type", UNSET)

        sort_direction = d.pop("sort_direction", UNSET)

        home_favorites_data = cls(
            id=id,
            name=name,
            device_group_list=device_group_list,
            device_list=device_list,
            app_settings=app_settings,
            sort_type=sort_type,
            sort_direction=sort_direction,
        )

        home_favorites_data.additional_properties = d
        return home_favorites_data

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
