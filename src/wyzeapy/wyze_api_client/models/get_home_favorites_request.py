from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="GetHomeFavoritesRequest")


@_attrs_define
class GetHomeFavoritesRequest:
    """
    Attributes:
        home_id (str): The home ID to get favorites for
        nonce (str): Nonce value (typically timestamp in milliseconds)
    """

    home_id: str
    nonce: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        home_id = self.home_id

        nonce = self.nonce

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "home_id": home_id,
                "nonce": nonce,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        home_id = d.pop("home_id")

        nonce = d.pop("nonce")

        get_home_favorites_request = cls(
            home_id=home_id,
            nonce=nonce,
        )

        get_home_favorites_request.additional_properties = d
        return get_home_favorites_request

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
