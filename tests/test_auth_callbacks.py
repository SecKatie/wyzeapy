"""Refresh callbacks may make ordinary reads using the committed token."""

import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest

from wyzeapy import Wyzeapy
from wyzeapy.wyze_auth_lib import Token


@pytest.fixture
def refresh_client(monkeypatch):
    client = Wyzeapy()
    client._auth_lib.token = Token("old-access", "old-refresh")
    calls = []

    async def post(url, **kwargs):
        calls.append(url)
        if url.endswith("/refresh_token"):
            result = {
                "code": "1",
                "data": {"access_token": "new-access", "refresh_token": "new-refresh"},
            }
        elif url.endswith("/get_object_list"):
            assert kwargs["json"]["access_token"] == "new-access"
            result = {"code": "1", "data": {"device_list": [{"mac": "fake-device"}]}}
        else:
            raise AssertionError("Unexpected request: " + url)
        return SimpleNamespace(json=AsyncMock(return_value=result))

    session = MagicMock()
    session.__aenter__.return_value.post = AsyncMock(side_effect=post)
    monkeypatch.setattr("wyzeapy.wyze_auth_lib._create_client_session", lambda: session)
    return client, calls


@pytest.mark.asyncio
@pytest.mark.parametrize("reason", ["proactive", "expired", "forced"])
async def test_refresh_callback_can_read_through_an_existing_service(
    refresh_client, reason
):
    client, calls = refresh_client
    auth = client._auth_lib
    service = await client.bulb_service
    received = []

    async def callback(token):
        # Callback delivery must remain inside the serialized auth generation.
        assert auth.refresh_lock.locked()
        assert token is auth.token
        assert not token.expired
        received.extend(await service.get_object_list())

    client.register_for_token_callback(callback)
    if reason == "proactive":
        auth.token._refresh_time = 1
    elif reason == "expired":
        auth.token.expired = True
    operation = auth.refresh() if reason == "forced" else auth.refresh_if_should()
    await asyncio.wait_for(operation, timeout=1)
    assert [device.mac for device in received] == ["fake-device"]
    assert sum(url.endswith("/refresh_token") for url in calls) == 1
    assert not auth.token.expired
    assert not auth.refresh_lock.locked()


@pytest.mark.asyncio
@pytest.mark.parametrize("failure", ["error", "cancel"])
async def test_callback_failure_keeps_the_committed_token_and_releases_lock(
    refresh_client, failure
):
    client, calls = refresh_client
    auth = client._auth_lib
    auth.token.expired = True
    entered, release = asyncio.Event(), asyncio.Event()

    async def callback(token):
        entered.set()
        await release.wait()
        raise ValueError("fake callback failure")

    client.register_for_token_callback(callback)
    task = asyncio.create_task(auth.refresh_if_should())
    await asyncio.wait_for(entered.wait(), 1)
    if failure == "cancel":
        task.cancel()
        expected = asyncio.CancelledError
    else:
        release.set()
        expected = ValueError
    with pytest.raises(expected):
        await task
    assert auth.token.access_token == "new-access"
    assert not auth.token.expired
    assert not auth.refresh_lock.locked()
    client.unregister_for_token_callback(callback)
    await auth.refresh_if_should()
    assert len(calls) == 1


@pytest.mark.asyncio
@pytest.mark.parametrize("reason", ["proactive", "expired"])
@pytest.mark.parametrize(
    "helper", ["_get_plan_binding_list_by_user", "_monitoring_profile_state_status"]
)
async def test_hms_reads_share_one_conditional_refresh(
    refresh_client, monkeypatch, reason, helper
):
    client, calls = refresh_client
    auth = client._auth_lib
    if reason == "proactive":
        auth.token._refresh_time = 1
    else:
        auth.token.expired = True
    auth.get = AsyncMock(return_value={"message": "fake success", "data": []})
    entered, release = asyncio.Event(), asyncio.Event()
    refresh = auth._refresh

    async def delayed_refresh():
        entered.set()
        await release.wait()
        await refresh()

    monkeypatch.setattr(auth, "_refresh", delayed_refresh)
    method = getattr(client._service, helper)
    args = ("fake-hms",) if helper == "_monitoring_profile_state_status" else ()
    first = asyncio.create_task(method(*args))
    await asyncio.wait_for(entered.wait(), 1)
    second = asyncio.create_task(method(*args))
    await asyncio.sleep(0)
    release.set()
    await asyncio.wait_for(asyncio.gather(first, second), 1)
    assert sum(url.endswith("/refresh_token") for url in calls) == 1
    assert auth.get.await_count == 2
    for call in auth.get.await_args_list:
        assert call.kwargs["headers"]["access_token"] == "new-access"


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "username,new_username",
    [(None, "named@example.test"), ("named@example.test", None)],
)
async def test_token_only_login_is_supported_but_cannot_change_bound_identity(
    refresh_client, monkeypatch, username, new_username
):
    client, calls = refresh_client
    monkeypatch.setattr("wyzeapy.wyze_auth_lib.async_get_ssl_context", AsyncMock())
    await client.login(username, None, None, None, Token("fake-access", "fake-refresh"))
    service = await client.bulb_service
    await service.get_object_list()
    owner, token, inventory = (
        client._auth_lib,
        client._auth_lib.token,
        client._context.devices,
    )
    count = len(calls)
    with pytest.raises(ValueError, match="different username"):
        await client.login(
            new_username, None, None, None, Token("other-access", "other-refresh")
        )
    assert len(calls) == count
    assert service._auth_lib is owner
    assert owner.token is token
    assert client._context.devices is inventory
    assert client._context.username == username
