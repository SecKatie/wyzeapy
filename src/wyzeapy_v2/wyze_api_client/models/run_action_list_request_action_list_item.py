from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.run_action_list_request_action_list_item_action_key import (
    RunActionListRequestActionListItemActionKey,
)
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.run_action_list_request_action_list_item_action_params import (
        RunActionListRequestActionListItemActionParams,
    )


T = TypeVar("T", bound="RunActionListRequestActionListItem")


@_attrs_define
class RunActionListRequestActionListItem:
    """
    Attributes:
        instance_id (str | Unset):
        provider_key (str | Unset):
        action_key (RunActionListRequestActionListItemActionKey | Unset):
        action_params (RunActionListRequestActionListItemActionParams | Unset):
    """

    instance_id: str | Unset = UNSET
    provider_key: str | Unset = UNSET
    action_key: RunActionListRequestActionListItemActionKey | Unset = UNSET
    action_params: RunActionListRequestActionListItemActionParams | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        instance_id = self.instance_id

        provider_key = self.provider_key

        action_key: str | Unset = UNSET
        if not isinstance(self.action_key, Unset):
            action_key = self.action_key.value

        action_params: dict[str, Any] | Unset = UNSET
        if not isinstance(self.action_params, Unset):
            action_params = self.action_params.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if instance_id is not UNSET:
            field_dict["instance_id"] = instance_id
        if provider_key is not UNSET:
            field_dict["provider_key"] = provider_key
        if action_key is not UNSET:
            field_dict["action_key"] = action_key
        if action_params is not UNSET:
            field_dict["action_params"] = action_params

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.run_action_list_request_action_list_item_action_params import (
            RunActionListRequestActionListItemActionParams,
        )

        d = dict(src_dict)
        instance_id = d.pop("instance_id", UNSET)

        provider_key = d.pop("provider_key", UNSET)

        _action_key = d.pop("action_key", UNSET)
        action_key: RunActionListRequestActionListItemActionKey | Unset
        if isinstance(_action_key, Unset):
            action_key = UNSET
        else:
            action_key = RunActionListRequestActionListItemActionKey(_action_key)

        _action_params = d.pop("action_params", UNSET)
        action_params: RunActionListRequestActionListItemActionParams | Unset
        if isinstance(_action_params, Unset):
            action_params = UNSET
        else:
            action_params = RunActionListRequestActionListItemActionParams.from_dict(
                _action_params
            )

        run_action_list_request_action_list_item = cls(
            instance_id=instance_id,
            provider_key=provider_key,
            action_key=action_key,
            action_params=action_params,
        )

        run_action_list_request_action_list_item.additional_properties = d
        return run_action_list_request_action_list_item

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
