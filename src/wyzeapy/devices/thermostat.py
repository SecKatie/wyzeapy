"""Wyze Thermostat device."""

from __future__ import annotations

from typing import TYPE_CHECKING

from .base import WyzeDevice
from ..const import OLIVE_APP_ID, APP_INFO
from ..exceptions import ActionFailedError, ApiRequestError
from ..wyze_api_client.models import (
    SetThermostatIotPropBody,
    SetThermostatIotPropBodyProps,
)
from ..wyze_api_client.api.thermostat import (
    get_thermostat_iot_prop,
    set_thermostat_iot_prop,
)

if TYPE_CHECKING:
    from ..models import ThermostatState


class WyzeThermostat(WyzeDevice):
    """Wyze Thermostat device."""

    @property
    def temperature(self) -> float | None:
        """Current temperature."""
        return self.device_params.get("temperature")

    @property
    def humidity(self) -> int | None:
        """Current humidity percentage."""
        return self.device_params.get("humidity")

    @property
    def cool_setpoint(self) -> float | None:
        """Cooling setpoint temperature."""
        return self.device_params.get("cool_sp")

    @property
    def heat_setpoint(self) -> float | None:
        """Heating setpoint temperature."""
        return self.device_params.get("heat_sp")

    @property
    def hvac_mode(self) -> str | None:
        """HVAC mode (auto, heat, cool, off)."""
        return self.device_params.get("mode_sys")

    @property
    def fan_mode(self) -> str | None:
        """Fan mode (auto, on, off)."""
        return self.device_params.get("fan_mode")

    @property
    def working_state(self) -> str | None:
        """Current working state (idle, heating, cooling)."""
        return self.device_params.get("working_state")

    async def get_state(self) -> "ThermostatState":
        """
        Get current thermostat state from the API.

        :returns: ThermostatState object with current temperature, setpoints, and mode.
        :rtype: ThermostatState
        """
        from ..models import ThermostatState

        ctx = self._get_context()
        await ctx.ensure_token_valid()

        access_token = ctx.access_token
        nonce = int(ctx.nonce())

        # Keys to request - common thermostat properties
        keys = "temperature,humidity,cool_sp,heat_sp,mode_sys,fan_mode,working_state,temp_unit"
        payload = {"keys": keys, "did": self.mac or "", "nonce": str(nonce)}
        signature = ctx.olive_create_signature(payload, access_token)

        platform_client = ctx.get_platform_client()

        response = await get_thermostat_iot_prop.asyncio(
            client=platform_client,
            keys=keys,
            did=self.mac or "",
            nonce=nonce,
            appid=OLIVE_APP_ID,
            appinfo=APP_INFO,
            phoneid=ctx.phone_id,
            signature2=signature,
        )

        if response is None:
            raise ApiRequestError("get_thermostat_state", f"device_mac={self.mac}")

        raw_data = response.to_dict() if hasattr(response, "to_dict") else {}
        return ThermostatState.from_api_response(raw_data)

    async def _set_properties(
        self,
        *,
        cool_setpoint: int | None = None,
        heat_setpoint: int | None = None,
        fan_mode: str | None = None,
        hvac_mode: str | None = None,
    ) -> None:
        """Set thermostat properties."""
        ctx = self._get_context()
        await ctx.ensure_token_valid()

        access_token = ctx.access_token
        nonce = ctx.nonce()

        # Build props
        props = SetThermostatIotPropBodyProps()
        if cool_setpoint is not None:
            props["cool_sp"] = cool_setpoint
        if heat_setpoint is not None:
            props["heat_sp"] = heat_setpoint
        if fan_mode is not None:
            props["fan_mode"] = fan_mode
        if hvac_mode is not None:
            props["mode_sys"] = hvac_mode

        body = SetThermostatIotPropBody(
            did=self.mac or "",
            model=self.product_model or "",
            props=props,
            is_sub_device=0,
            nonce=nonce,
        )

        body_dict = body.to_dict()
        signature = ctx.olive_create_signature(body_dict, access_token)

        platform_client = ctx.get_platform_client()

        response = await set_thermostat_iot_prop.asyncio(
            client=platform_client,
            body=body,
            appid=OLIVE_APP_ID,
            appinfo=APP_INFO,
            phoneid=ctx.phone_id,
            signature2=signature,
        )

        if response is None:
            raise ActionFailedError("set_thermostat_props", self.mac or "", None)
        if getattr(response, "code", None) != "1":
            raise ActionFailedError("set_thermostat_props", self.mac or "", response)

    async def set_cool_setpoint(self, temperature: int) -> None:
        """
        Set cooling setpoint temperature.

        :param temperature: The target cooling temperature.
        :raises ActionFailedError: If setting the temperature fails.
        """
        await self._set_properties(cool_setpoint=temperature)

    async def set_heat_setpoint(self, temperature: int) -> None:
        """
        Set heating setpoint temperature.

        :param temperature: The target heating temperature.
        :raises ActionFailedError: If setting the temperature fails.
        """
        await self._set_properties(heat_setpoint=temperature)

    async def set_hvac_mode(self, mode: str) -> None:
        """
        Set HVAC mode.

        :param mode: The mode ('off', 'heat', 'cool', 'auto').
        :raises ActionFailedError: If setting the mode fails.
        """
        await self._set_properties(hvac_mode=mode)

    async def set_fan_mode(self, mode: str) -> None:
        """
        Set fan mode.

        :param mode: The mode ('auto', 'on', 'cycle').
        :raises ActionFailedError: If setting the mode fails.
        """
        await self._set_properties(fan_mode=mode)
