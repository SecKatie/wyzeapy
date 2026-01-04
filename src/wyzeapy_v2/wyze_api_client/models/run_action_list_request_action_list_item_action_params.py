from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.run_action_list_request_action_list_item_action_params_list_item import (
        RunActionListRequestActionListItemActionParamsListItem,
    )


T = TypeVar("T", bound="RunActionListRequestActionListItemActionParams")


@_attrs_define
class RunActionListRequestActionListItemActionParams:
    """
    Attributes:
        list_ (list[RunActionListRequestActionListItemActionParamsListItem] | Unset):
    """

    list_: list[RunActionListRequestActionListItemActionParamsListItem] | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        list_: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.list_, Unset):
            list_ = []
            for list_item_data in self.list_:
                list_item = list_item_data.to_dict()
                list_.append(list_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if list_ is not UNSET:
            field_dict["list"] = list_

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.run_action_list_request_action_list_item_action_params_list_item import (
            RunActionListRequestActionListItemActionParamsListItem,
        )

        d = dict(src_dict)
        _list_ = d.pop("list", UNSET)
        list_: list[RunActionListRequestActionListItemActionParamsListItem] | Unset = (
            UNSET
        )
        if _list_ is not UNSET:
            list_ = []
            for list_item_data in _list_:
                list_item = (
                    RunActionListRequestActionListItemActionParamsListItem.from_dict(
                        list_item_data
                    )
                )

                list_.append(list_item)

        run_action_list_request_action_list_item_action_params = cls(
            list_=list_,
        )

        run_action_list_request_action_list_item_action_params.additional_properties = d
        return run_action_list_request_action_list_item_action_params

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
