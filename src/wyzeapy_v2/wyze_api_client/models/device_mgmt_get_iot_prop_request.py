from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.device_mgmt_get_iot_prop_request_capabilities_item import (
        DeviceMgmtGetIotPropRequestCapabilitiesItem,
    )
    from ..models.device_mgmt_get_iot_prop_request_target_info import (
        DeviceMgmtGetIotPropRequestTargetInfo,
    )


T = TypeVar("T", bound="DeviceMgmtGetIotPropRequest")


@_attrs_define
class DeviceMgmtGetIotPropRequest:
    """
    Attributes:
        capabilities (list[DeviceMgmtGetIotPropRequestCapabilitiesItem]):
        nonce (int):
        target_info (DeviceMgmtGetIotPropRequestTargetInfo):
    """

    capabilities: list[DeviceMgmtGetIotPropRequestCapabilitiesItem]
    nonce: int
    target_info: DeviceMgmtGetIotPropRequestTargetInfo
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        capabilities = []
        for capabilities_item_data in self.capabilities:
            capabilities_item = capabilities_item_data.to_dict()
            capabilities.append(capabilities_item)

        nonce = self.nonce

        target_info = self.target_info.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "capabilities": capabilities,
                "nonce": nonce,
                "targetInfo": target_info,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.device_mgmt_get_iot_prop_request_capabilities_item import (
            DeviceMgmtGetIotPropRequestCapabilitiesItem,
        )
        from ..models.device_mgmt_get_iot_prop_request_target_info import (
            DeviceMgmtGetIotPropRequestTargetInfo,
        )

        d = dict(src_dict)
        capabilities = []
        _capabilities = d.pop("capabilities")
        for capabilities_item_data in _capabilities:
            capabilities_item = DeviceMgmtGetIotPropRequestCapabilitiesItem.from_dict(
                capabilities_item_data
            )

            capabilities.append(capabilities_item)

        nonce = d.pop("nonce")

        target_info = DeviceMgmtGetIotPropRequestTargetInfo.from_dict(
            d.pop("targetInfo")
        )

        device_mgmt_get_iot_prop_request = cls(
            capabilities=capabilities,
            nonce=nonce,
            target_info=target_info,
        )

        device_mgmt_get_iot_prop_request.additional_properties = d
        return device_mgmt_get_iot_prop_request

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
