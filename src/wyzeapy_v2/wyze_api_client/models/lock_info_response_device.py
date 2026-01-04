from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.lock_info_response_device_locker_status import (
        LockInfoResponseDeviceLockerStatus,
    )


T = TypeVar("T", bound="LockInfoResponseDevice")


@_attrs_define
class LockInfoResponseDevice:
    """
    Attributes:
        uuid (str | Unset):
        onoff_line (int | Unset): Online status (1=online)
        door_open_status (int | Unset): Door open status (1=open)
        trash_mode (int | Unset):
        locker_status (LockInfoResponseDeviceLockerStatus | Unset):
    """

    uuid: str | Unset = UNSET
    onoff_line: int | Unset = UNSET
    door_open_status: int | Unset = UNSET
    trash_mode: int | Unset = UNSET
    locker_status: LockInfoResponseDeviceLockerStatus | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        uuid = self.uuid

        onoff_line = self.onoff_line

        door_open_status = self.door_open_status

        trash_mode = self.trash_mode

        locker_status: dict[str, Any] | Unset = UNSET
        if not isinstance(self.locker_status, Unset):
            locker_status = self.locker_status.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if uuid is not UNSET:
            field_dict["uuid"] = uuid
        if onoff_line is not UNSET:
            field_dict["onoff_line"] = onoff_line
        if door_open_status is not UNSET:
            field_dict["door_open_status"] = door_open_status
        if trash_mode is not UNSET:
            field_dict["trash_mode"] = trash_mode
        if locker_status is not UNSET:
            field_dict["locker_status"] = locker_status

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.lock_info_response_device_locker_status import (
            LockInfoResponseDeviceLockerStatus,
        )

        d = dict(src_dict)
        uuid = d.pop("uuid", UNSET)

        onoff_line = d.pop("onoff_line", UNSET)

        door_open_status = d.pop("door_open_status", UNSET)

        trash_mode = d.pop("trash_mode", UNSET)

        _locker_status = d.pop("locker_status", UNSET)
        locker_status: LockInfoResponseDeviceLockerStatus | Unset
        if isinstance(_locker_status, Unset):
            locker_status = UNSET
        else:
            locker_status = LockInfoResponseDeviceLockerStatus.from_dict(_locker_status)

        lock_info_response_device = cls(
            uuid=uuid,
            onoff_line=onoff_line,
            door_open_status=door_open_status,
            trash_mode=trash_mode,
            locker_status=locker_status,
        )

        lock_info_response_device.additional_properties = d
        return lock_info_response_device

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
