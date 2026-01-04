from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.device_mgmt_run_action_request_capabilities_item import (
        DeviceMgmtRunActionRequestCapabilitiesItem,
    )
    from ..models.device_mgmt_run_action_request_target_info import (
        DeviceMgmtRunActionRequestTargetInfo,
    )


T = TypeVar("T", bound="DeviceMgmtRunActionRequest")


@_attrs_define
class DeviceMgmtRunActionRequest:
    """
    Attributes:
        capabilities (list[DeviceMgmtRunActionRequestCapabilitiesItem]):
        nonce (int):
        target_info (DeviceMgmtRunActionRequestTargetInfo):
        transaction_id (str | Unset):
    """

    capabilities: list[DeviceMgmtRunActionRequestCapabilitiesItem]
    nonce: int
    target_info: DeviceMgmtRunActionRequestTargetInfo
    transaction_id: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        capabilities = []
        for capabilities_item_data in self.capabilities:
            capabilities_item = capabilities_item_data.to_dict()
            capabilities.append(capabilities_item)

        nonce = self.nonce

        target_info = self.target_info.to_dict()

        transaction_id = self.transaction_id

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "capabilities": capabilities,
                "nonce": nonce,
                "targetInfo": target_info,
            }
        )
        if transaction_id is not UNSET:
            field_dict["transactionId"] = transaction_id

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.device_mgmt_run_action_request_capabilities_item import (
            DeviceMgmtRunActionRequestCapabilitiesItem,
        )
        from ..models.device_mgmt_run_action_request_target_info import (
            DeviceMgmtRunActionRequestTargetInfo,
        )

        d = dict(src_dict)
        capabilities = []
        _capabilities = d.pop("capabilities")
        for capabilities_item_data in _capabilities:
            capabilities_item = DeviceMgmtRunActionRequestCapabilitiesItem.from_dict(
                capabilities_item_data
            )

            capabilities.append(capabilities_item)

        nonce = d.pop("nonce")

        target_info = DeviceMgmtRunActionRequestTargetInfo.from_dict(
            d.pop("targetInfo")
        )

        transaction_id = d.pop("transactionId", UNSET)

        device_mgmt_run_action_request = cls(
            capabilities=capabilities,
            nonce=nonce,
            target_info=target_info,
            transaction_id=transaction_id,
        )

        device_mgmt_run_action_request.additional_properties = d
        return device_mgmt_run_action_request

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
