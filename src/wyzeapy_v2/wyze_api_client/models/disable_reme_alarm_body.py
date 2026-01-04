from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.disable_reme_alarm_body_remediation_id import (
    DisableRemeAlarmBodyRemediationId,
)
from ..types import UNSET, Unset

T = TypeVar("T", bound="DisableRemeAlarmBody")


@_attrs_define
class DisableRemeAlarmBody:
    """
    Attributes:
        hms_id (str | Unset):
        remediation_id (DisableRemeAlarmBodyRemediationId | Unset):
    """

    hms_id: str | Unset = UNSET
    remediation_id: DisableRemeAlarmBodyRemediationId | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        hms_id = self.hms_id

        remediation_id: str | Unset = UNSET
        if not isinstance(self.remediation_id, Unset):
            remediation_id = self.remediation_id.value

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if hms_id is not UNSET:
            field_dict["hms_id"] = hms_id
        if remediation_id is not UNSET:
            field_dict["remediation_id"] = remediation_id

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        hms_id = d.pop("hms_id", UNSET)

        _remediation_id = d.pop("remediation_id", UNSET)
        remediation_id: DisableRemeAlarmBodyRemediationId | Unset
        if isinstance(_remediation_id, Unset):
            remediation_id = UNSET
        else:
            remediation_id = DisableRemeAlarmBodyRemediationId(_remediation_id)

        disable_reme_alarm_body = cls(
            hms_id=hms_id,
            remediation_id=remediation_id,
        )

        disable_reme_alarm_body.additional_properties = d
        return disable_reme_alarm_body

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
