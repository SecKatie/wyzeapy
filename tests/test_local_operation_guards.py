"""Local device commands enforce ownership before creating any HTTP session."""

import asyncio
from unittest.mock import AsyncMock, MagicMock

import pytest

from wyzeapy import Wyzeapy
from wyzeapy.services.bulb_service import Bulb
from wyzeapy.wyze_auth_lib import Token


COMMANDS = [
    ("turn_on", {"local_control": True}),
    ("turn_off", {"local_control": True}),
    ("set_brightness", {"brightness": 50}),
    ("set_color_temp", {"color_temp": 4000}),
    ("set_color", {"color": "FF0000", "local_control": True}),
]


def mesh_bulb():
    return Bulb(
        {
            "mac": "fake-mac",
            "product_type": "MeshLight",
            "product_model": "WLPA19C",
            "device_params": {"ip": "192.0.2.1"},
        }
    )


@pytest.mark.asyncio
@pytest.mark.parametrize("method,kwargs", COMMANDS)
@pytest.mark.parametrize("state", ["login", "mfa", "wrong-loop"])
async def test_local_commands_reject_invalid_owner_state_without_network(
    monkeypatch, method, kwargs, state
):
    client = Wyzeapy()
    client._auth_lib.token = Token("fake-access", "fake-refresh")
    service = await client.bulb_service
    bulb = mesh_bulb()
    client._context.bind_loop()
    session = MagicMock(side_effect=AssertionError("No LAN or cloud HTTP is permitted"))
    encrypt = MagicMock(side_effect=AssertionError("Reject before building a payload"))
    monkeypatch.setattr("wyzeapy.services.base_service.aiohttp.ClientSession", session)
    monkeypatch.setattr("wyzeapy.wyze_auth_lib._create_client_session", session)
    monkeypatch.setattr("wyzeapy.services.base_service.wyze_encrypt", encrypt)

    async def command():
        await getattr(service, method)(bulb, **kwargs)

    if state == "login":
        client._context.login_pending = True
    elif state == "mfa":
        client._context.mfa = object()
    expected = (
        "original event loop"
        if state == "wrong-loop"
        else "Authentication is in progress"
    )
    with pytest.raises(RuntimeError, match=expected):
        if state == "wrong-loop":
            await asyncio.to_thread(lambda: asyncio.run(command()))
        else:
            await command()
    session.assert_not_called()
    encrypt.assert_not_called()
    assert not bulb.cloud_fallback


@pytest.mark.asyncio
async def test_ready_local_command_preserves_local_transport_without_refresh(
    monkeypatch,
):
    client = Wyzeapy()
    client._auth_lib.token = Token("fake-access", "fake-refresh")
    client._auth_lib.refresh_if_should = AsyncMock()
    service = await client.bulb_service
    session = MagicMock()
    transport = MagicMock()
    session.return_value.__aenter__.return_value = transport
    response = transport.post.return_value.__aenter__.return_value
    response.text = AsyncMock(return_value="fake local success")
    monkeypatch.setattr("wyzeapy.services.base_service.aiohttp.ClientSession", session)
    monkeypatch.setattr(
        "wyzeapy.services.base_service.wyze_encrypt",
        MagicMock(return_value="fake encrypted payload"),
    )
    await service.set_brightness(mesh_bulb(), 50)
    session.assert_called_once_with()
    client._auth_lib.refresh_if_should.assert_not_awaited()
