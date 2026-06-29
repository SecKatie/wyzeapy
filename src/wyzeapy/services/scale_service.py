"""Wyze Scale service for wyzeapy."""

from __future__ import annotations

import logging
import time
from typing import Any, Dict, List, Optional

from wyzeapy.const import OLIVE_APP_ID, APP_INFO, PHONE_ID
from wyzeapy.crypto import olive_create_signature
from wyzeapy.services.base_service import BaseService
from wyzeapy.types import Device

_LOGGER = logging.getLogger(__name__)

SCALE_HOST = "https://wyze-scale-service.wyzecam.com"
SCALE_MODELS = ("WL_SCU", "WL_SC2", "JA.SC", "JA.SC2")


class ScaleRecord:
    """A single weigh-in. Field names match the Wyze health API payload."""

    def __init__(self, raw: Dict[str, Any]):
        self.raw = raw
        self.data_id = raw.get("data_id")
        self.family_member_id = raw.get("family_member_id")
        self.user_id = raw.get("user_id")
        self.measure_ts = raw.get("measure_ts")
        self.weight = _to_float(raw.get("weight"))        # kg
        self.bmi = _to_float(raw.get("bmi"))
        self.bmr = _to_float(raw.get("bmr"))
        self.body_fat = _to_float(raw.get("body_fat"))    # %
        self.body_water = _to_float(raw.get("body_water"))
        self.bone_mineral = _to_float(raw.get("bone_mineral"))
        self.muscle = _to_float(raw.get("muscle"))
        self.protein = _to_float(raw.get("protein"))      # %
        self.body_vfr = _to_float(raw.get("body_vfr"))    # visceral fat rating
        self.metabolic_age = _to_float(raw.get("metabolic_age"))
        self.heart_rate = _to_float(raw.get("heart_rate"))


class Scale(Device):
    def __init__(self, dictionary: Dict[Any, Any]):
        super().__init__(dictionary)
        self.unit: Optional[str] = None
        self.latest_by_member: Dict[str, ScaleRecord] = {}
        self.available: bool = True


class ScaleService(BaseService):
    async def get_scales(self) -> List[Scale]:
        if self._devices is None:
            self._devices = await self.get_object_list()
        return [
            Scale(d.raw_dict)
            for d in self._devices
            if d.product_model in SCALE_MODELS
        ]

    async def update(self, scale: Scale) -> Scale:
        """Fetch the latest record and store it."""
        try:
            rec = await self._get_latest_record(scale)
            if rec is not None:
                key = rec.user_id or rec.family_member_id or "primary"
                scale.latest_by_member[key] = rec
        except Exception as e:
            _LOGGER.debug("scale update failed: %s", e)
        return scale

    async def _get_latest_record(
        self, scale: Scale, user_id: Optional[str] = None
    ) -> Optional[ScaleRecord]:
        params: Dict[str, Any] = {}
        if user_id:
            params["family_member_id"] = user_id
        data = await self._scale_get("/plugin/scale/get_latest_record", params)
        payload = data.get("data")
        if not payload:
            return None
        # Scale Ultra returns a list — take the most recent (first)
        if isinstance(payload, list):
            payload = payload[0] if payload else None
        return ScaleRecord(payload) if payload else None

    async def _get_record_range(
        self, scale: Scale, user_id: Optional[str], end_ts_ms: int
    ) -> List[ScaleRecord]:
        """Older JA.SC / JA.SC2 path."""
        params: Dict[str, Any] = {"start_time": "0", "end_time": str(end_ts_ms)}
        if user_id:
            params["family_member_id"] = user_id
        data = await self._scale_get("/plugin/scale/get_record_range", params)
        return [ScaleRecord(r) for r in (data.get("data") or [])]

    async def _get_heart_rate(
        self, user_id: Optional[str] = None, record_number: int = 1
    ) -> Optional[float]:
        params: Dict[str, Any] = {"record_number": str(record_number)}
        if user_id:
            params["family_member_id"] = user_id
        data = await self._scale_get(
            "/plugin/scale/get_heart_rate_record_list", params
        )
        rows = data.get("data") or []
        if isinstance(rows, dict):
            rows = rows.get("record_list", [])
        return _to_float(rows[0].get("heart_rate")) if rows else None

    async def _scale_get(self, path: str, params: Dict[str, Any]) -> Dict[Any, Any]:
        await self._auth_lib.refresh_if_should()
        params = dict(params)
        params["nonce"] = str(int(time.time() * 1000))
        params["access_token"] = self._auth_lib.token.access_token
        signature = olive_create_signature(params, self._auth_lib.token.access_token)
        headers = {
            "Accept-Encoding": "gzip",
            "User-Agent": "myapp",
            "appid": OLIVE_APP_ID,
            "appinfo": APP_INFO,
            "phoneid": PHONE_ID,
            "access_token": self._auth_lib.token.access_token,
            "signature2": signature,
        }
        return await self._auth_lib.get(
            SCALE_HOST + path, headers=headers, params=params
        )


def _to_float(v: Any) -> Optional[float]:
    if v is None or v == "":
        return None
    try:
        return float(v)
    except (TypeError, ValueError):
        return None
