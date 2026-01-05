from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.device_mgmt_run_action_request_capabilities_item_name import (
    DeviceMgmtRunActionRequestCapabilitiesItemName,
)
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.device_mgmt_run_action_request_capabilities_item_functions_item import (
        DeviceMgmtRunActionRequestCapabilitiesItemFunctionsItem,
    )
    from ..models.device_mgmt_run_action_request_capabilities_item_properties_item import (
        DeviceMgmtRunActionRequestCapabilitiesItemPropertiesItem,
    )


T = TypeVar("T", bound="DeviceMgmtRunActionRequestCapabilitiesItem")


@_attrs_define
class DeviceMgmtRunActionRequestCapabilitiesItem:
    """
    Attributes:
        iid (int | Unset):
        name (DeviceMgmtRunActionRequestCapabilitiesItemName | Unset):
        properties (list[DeviceMgmtRunActionRequestCapabilitiesItemPropertiesItem] | Unset):
        functions (list[DeviceMgmtRunActionRequestCapabilitiesItemFunctionsItem] | Unset):
    """

    iid: int | Unset = UNSET
    name: DeviceMgmtRunActionRequestCapabilitiesItemName | Unset = UNSET
    properties: list[DeviceMgmtRunActionRequestCapabilitiesItemPropertiesItem] | Unset = UNSET
    functions: list[DeviceMgmtRunActionRequestCapabilitiesItemFunctionsItem] | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        iid = self.iid

        name: str | Unset = UNSET
        if not isinstance(self.name, Unset):
            name = self.name.value

        properties: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.properties, Unset):
            properties = []
            for properties_item_data in self.properties:
                properties_item = properties_item_data.to_dict()
                properties.append(properties_item)

        functions: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.functions, Unset):
            functions = []
            for functions_item_data in self.functions:
                functions_item = functions_item_data.to_dict()
                functions.append(functions_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if iid is not UNSET:
            field_dict["iid"] = iid
        if name is not UNSET:
            field_dict["name"] = name
        if properties is not UNSET:
            field_dict["properties"] = properties
        if functions is not UNSET:
            field_dict["functions"] = functions

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.device_mgmt_run_action_request_capabilities_item_functions_item import (
            DeviceMgmtRunActionRequestCapabilitiesItemFunctionsItem,
        )
        from ..models.device_mgmt_run_action_request_capabilities_item_properties_item import (
            DeviceMgmtRunActionRequestCapabilitiesItemPropertiesItem,
        )

        d = dict(src_dict)
        iid = d.pop("iid", UNSET)

        _name = d.pop("name", UNSET)
        name: DeviceMgmtRunActionRequestCapabilitiesItemName | Unset
        if isinstance(_name, Unset):
            name = UNSET
        else:
            name = DeviceMgmtRunActionRequestCapabilitiesItemName(_name)

        _properties = d.pop("properties", UNSET)
        properties: list[DeviceMgmtRunActionRequestCapabilitiesItemPropertiesItem] | Unset = UNSET
        if _properties is not UNSET:
            properties = []
            for properties_item_data in _properties:
                properties_item = DeviceMgmtRunActionRequestCapabilitiesItemPropertiesItem.from_dict(
                    properties_item_data
                )

                properties.append(properties_item)

        _functions = d.pop("functions", UNSET)
        functions: list[DeviceMgmtRunActionRequestCapabilitiesItemFunctionsItem] | Unset = UNSET
        if _functions is not UNSET:
            functions = []
            for functions_item_data in _functions:
                functions_item = DeviceMgmtRunActionRequestCapabilitiesItemFunctionsItem.from_dict(functions_item_data)

                functions.append(functions_item)

        device_mgmt_run_action_request_capabilities_item = cls(
            iid=iid,
            name=name,
            properties=properties,
            functions=functions,
        )

        device_mgmt_run_action_request_capabilities_item.additional_properties = d
        return device_mgmt_run_action_request_capabilities_item

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
