from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.lock_info_response_device import LockInfoResponseDevice


T = TypeVar("T", bound="LockInfoResponse")


@_attrs_define
class LockInfoResponse:
    """
    Attributes:
        device (LockInfoResponseDevice | Unset):
    """

    device: LockInfoResponseDevice | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        device: dict[str, Any] | Unset = UNSET
        if not isinstance(self.device, Unset):
            device = self.device.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if device is not UNSET:
            field_dict["device"] = device

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.lock_info_response_device import LockInfoResponseDevice

        d = dict(src_dict)
        _device = d.pop("device", UNSET)
        device: LockInfoResponseDevice | Unset
        if isinstance(_device, Unset):
            device = UNSET
        else:
            device = LockInfoResponseDevice.from_dict(_device)

        lock_info_response = cls(
            device=device,
        )

        lock_info_response.additional_properties = d
        return lock_info_response

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
