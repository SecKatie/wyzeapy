from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="StreamParams")


@_attrs_define
class StreamParams:
    """
    Attributes:
        dtls (int | Unset): Whether DTLS is enabled (1=enabled)
        enr (str | Unset): ENR token for camera authentication
        p2p_id (str | Unset): P2P ID for TUTK connection
    """

    dtls: int | Unset = UNSET
    enr: str | Unset = UNSET
    p2p_id: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        dtls = self.dtls

        enr = self.enr

        p2p_id = self.p2p_id

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if dtls is not UNSET:
            field_dict["dtls"] = dtls
        if enr is not UNSET:
            field_dict["enr"] = enr
        if p2p_id is not UNSET:
            field_dict["p2p_id"] = p2p_id

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        dtls = d.pop("dtls", UNSET)

        enr = d.pop("enr", UNSET)

        p2p_id = d.pop("p2p_id", UNSET)

        stream_params = cls(
            dtls=dtls,
            enr=enr,
            p2p_id=p2p_id,
        )

        stream_params.additional_properties = d
        return stream_params

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
