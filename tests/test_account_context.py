"""Account ownership exercised through real services and loopback HTTP only."""

import asyncio
from collections import Counter, deque
from types import SimpleNamespace
from urllib.parse import urlsplit
from unittest.mock import AsyncMock, MagicMock, patch

from aiohttp import ClientSession, web
import pytest
import pytest_asyncio

from wyzeapy import Wyzeapy
from wyzeapy.exceptions import (
    AccessTokenError,
    TwoFactorAuthenticationEnabled,
    UnknownApiError,
    _AuthenticationInProgress,
)
from wyzeapy.services.base_service import BaseService
from wyzeapy.services.camera_service import CameraService
from wyzeapy.services.sensor_service import Sensor, SensorService
from wyzeapy.services.update_manager import DeviceUpdater, UpdateManager
from wyzeapy.wyze_auth_lib import Token, WyzeAuthLib


@pytest_asyncio.fixture
async def cloud(monkeypatch):
    state = SimpleNamespace(
        calls=Counter(),
        logins=deque(),
        entered=asyncio.Event(),
        gate=None,
        inventory_error=False,
        inventory_gate=None,
        inventory_entered=asyncio.Event(),
    )

    async def respond(request):
        path = request.path
        state.calls[path] += 1
        payload = await request.json()
        if path == "/api/user/login":
            result = state.logins.popleft() if state.logins else "success"
            if state.gate is not None:
                state.entered.set()
                await state.gate.wait()
            if result == "error":
                return web.json_response({"errorCode": 1000})
            if result == "mfa":
                return web.json_response(
                    {
                        "mfa_options": ["TotpVerificationCode"],
                        "mfa_details": {"totp_apps": [{"app_id": "fake-app"}]},
                    }
                )
            token = payload["email"] + ":" + str(state.calls[path])
            return web.json_response({"access_token": token, "refresh_token": token})
        if path == "/user/login":
            if state.gate is not None:
                state.entered.set()
                await state.gate.wait()
            if payload["verification_code"] == "bad":
                return web.json_response({"errorCode": 1000})
            return web.json_response(
                {"access_token": payload["email"] + ":mfa", "refresh_token": "mfa"}
            )
        if path == "/app/user/refresh_token":
            if state.gate is not None:
                state.entered.set()
                await state.gate.wait()
            token = payload["refresh_token"] + ":refreshed"
            return web.json_response(
                {"code": "1", "data": {"access_token": token, "refresh_token": token}}
            )
        if path == "/app/v2/home_page/get_object_list":
            if state.inventory_gate is not None and payload["access_token"].startswith(
                "a@"
            ):
                state.inventory_entered.set()
                await state.inventory_gate.wait()
            if state.inventory_error:
                return web.json_response({"code": "9999", "msg": "fake error"})
            return web.json_response(
                {
                    "code": "1",
                    "data": {
                        "device_list": [
                            {
                                "mac": "overlapping-id",
                                "product_type": "Light",
                                "product_model": "WLPA19",
                                "nickname": payload["access_token"],
                                "device_params": {
                                    "account": payload["access_token"],
                                    "ip": "127.0.0.1",
                                    "enr": "fake-enr",
                                },
                            }
                        ]
                    },
                }
            )
        raise AssertionError(f"Unexpected test endpoint: {path}")

    app = web.Application()
    app.router.add_post("/{path:.*}", respond)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "127.0.0.1", 0)
    await site.start()
    address = runner.addresses[0]
    base = f"http://127.0.0.1:{address[1]}"

    class LocalSession:
        async def __aenter__(self):
            self.session = ClientSession()
            return self

        async def __aexit__(self, *args):
            await self.session.close()

        async def post(self, url, **kwargs):
            return await self.session.post(base + urlsplit(url).path, **kwargs)

    monkeypatch.setattr("wyzeapy.wyze_auth_lib._create_client_session", LocalSession)
    monkeypatch.setattr("wyzeapy.wyze_auth_lib.async_get_ssl_context", AsyncMock())
    try:
        yield state
    finally:
        if state.gate is not None:
            state.gate.set()
        if state.inventory_gate is not None:
            state.inventory_gate.set()
        await runner.cleanup()


async def login(client, username="a@example.test"):
    await client.login(username, "fake-password", "fake-key-id", "fake-api-key")


@pytest.mark.asyncio
async def test_inventory_shared_within_client_and_isolated_across_clients(
    cloud, monkeypatch
):
    a, b = Wyzeapy(), Wyzeapy()
    await asyncio.gather(login(a), login(b, "b@example.test"))
    bulbs, cameras, other = (
        await a.bulb_service,
        await a.camera_service,
        await b.bulb_service,
    )
    assert bulbs._context is cameras._context is a._context
    assert other._context is not bulbs._context
    assert bulbs._auth_lib is cameras._auth_lib is a._auth_lib
    assert a._auth_lib.refresh_lock is not b._auth_lib.refresh_lock

    # The same inventory supplies all service discovery, without per-service snapshots.
    found = await bulbs.get_bulbs()
    await cameras.get_cameras()
    await other.get_bulbs()
    assert found[0].mac == b._context.devices[0].mac == "overlapping-id"
    assert a._context.devices[0].nickname != b._context.devices[0].nickname
    assert cloud.calls["/app/v2/home_page/get_object_list"] == 2
    assert a._context.last_updated_time == b._context.last_updated_time == 0

    now = 1000
    monkeypatch.setattr("wyzeapy.services.base_service.time.time", lambda: now)
    first = await bulbs.get_updated_params("overlapping-id")
    assert await cameras.get_updated_params("overlapping-id") == first
    assert a._context.last_updated_time == 1000
    assert b._context.last_updated_time == 0
    now = 1299
    await cameras.get_updated_params("overlapping-id")
    assert cloud.calls["/app/v2/home_page/get_object_list"] == 3
    now = 1300
    await cameras.get_updated_params("overlapping-id")
    assert cloud.calls["/app/v2/home_page/get_object_list"] == 4

    snapshot = a._context.devices
    cloud.inventory_error = True
    now = 1600
    with pytest.raises(UnknownApiError, match="fake error"):
        await bulbs.get_updated_params("overlapping-id")
    assert a._context.devices is snapshot
    assert a._context.last_updated_time == 1300


@pytest.mark.asyncio
async def test_every_lazy_service_gets_one_context(cloud, monkeypatch):
    client = Wyzeapy()
    await login(client)
    monkeypatch.setattr(
        "wyzeapy.services.hms_service.HMSService._get_hms_id", AsyncMock()
    )
    for name in (
        "bulb",
        "camera",
        "switch",
        "switch_usage",
        "wall_switch",
        "sensor",
        "hms",
        "irrigation",
        "thermostat",
        "air_purifier",
        "lock",
    ):
        service = await getattr(client, name + "_service")
        assert service._context is client._context
        assert service._auth_lib is client._auth_lib
        assert await getattr(client, name + "_service") is service


@pytest.mark.asyncio
async def test_coordination_and_subscriptions_have_explicit_owners(cloud, monkeypatch):
    a, b = Wyzeapy(), Wyzeapy()
    await asyncio.gather(login(a), login(b, "b@example.test"))
    for kind in ("camera", "sensor"):
        monkeypatch.setattr(f"wyzeapy.services.{kind}_service.Thread", MagicMock())
        sa, sb = (
            await getattr(a, kind + "_service"),
            await getattr(b, kind + "_service"),
        )
        da, db = MagicMock(mac="same"), MagicMock(mac="same")
        ca, cb = MagicMock(), MagicMock()
        await sa.register_for_updates(da, ca)
        await sb.register_for_updates(db, cb)
        assert sa._subscribers == [(da, ca)]
        assert sb._subscribers == [(db, cb)]
        await sa.deregister_for_updates(da)
        assert sb._subscribers == [(db, cb)]

    bulbs, switches, other = (
        await a.bulb_service,
        await a.switch_service,
        await b.bulb_service,
    )
    da, db = MagicMock(mac="same"), MagicMock(mac="same")
    bulbs.register_updater(da, 30)
    other.register_updater(db, 30)
    assert bulbs._context.update_manager is switches._context.update_manager
    assert (
        len(a._context.update_manager.updaters)
        == len(b._context.update_manager.updaters)
        == 1
    )
    bulbs.unregister_updater(da)
    assert not b._context.update_manager.removed_updaters
    assert b._context.updaters[db].device is db
    async with a._context.update_lock:
        assert switches._context.update_lock.locked()
        assert not b._context.update_lock.locked()


@pytest.mark.asyncio
async def test_updater_startup_is_owned_and_once(cloud):
    a, b = Wyzeapy(), Wyzeapy()
    await asyncio.gather(login(a), login(b, "b@example.test"))
    a._context.update_manager.update_next = AsyncMock()
    b._context.update_manager.update_next = AsyncMock()
    with pytest.raises(RuntimeError, match="service instance"):
        await BaseService.start_update_manager()
    await (await a.bulb_service).start_update_manager()
    task = a._context.update_task
    await (await a.switch_service).start_update_manager()
    assert a._context.update_task is task
    assert b._context.update_task is None
    await task
    a._context.update_manager.update_next.assert_awaited_once()
    b._context.update_manager.update_next.assert_not_awaited()


@pytest.mark.asyncio
async def test_same_account_retry_commits_to_existing_services(cloud):
    client = Wyzeapy()
    callback = MagicMock()
    client.register_for_token_callback(callback)
    await login(client)
    service = await client.bulb_service
    owner, lock, old = (
        client._auth_lib,
        client._auth_lib.refresh_lock,
        client._auth_lib.token,
    )
    await login(client)
    assert service._auth_lib is owner
    assert owner.refresh_lock is lock
    assert owner.token is not old
    assert (await service.get_bulbs())[0].nickname == owner.token.access_token
    assert callback.call_count == 2
    calls = cloud.calls.copy()
    with pytest.raises(ValueError, match="different username"):
        await login(client, "A@example.test")
    assert cloud.calls == calls
    assert client._auth_lib is owner


@pytest.mark.asyncio
@pytest.mark.parametrize("authenticated", [False, True])
async def test_failed_and_cancelled_retry_preserves_only_committed_auth(
    cloud, authenticated
):
    client = Wyzeapy()
    if authenticated:
        await login(client)
    old = client._auth_lib.token
    cloud.logins.append("error")
    with pytest.raises(AccessTokenError):
        await login(client)
    assert client._auth_lib.token is old

    cloud.gate = asyncio.Event()
    task = asyncio.create_task(login(client))
    await asyncio.wait_for(cloud.entered.wait(), 2)
    with pytest.raises(RuntimeError, match="Authentication is in progress"):
        await (await client.bulb_service).get_bulbs()
    task.cancel()
    with pytest.raises(asyncio.CancelledError):
        await task
    assert client._auth_lib.token is old
    assert not client._context.login_pending
    assert client._context.mfa is None
    if authenticated:
        assert (await (await client.bulb_service).get_bulbs())[
            0
        ].nickname == old.access_token
    else:
        with pytest.raises(RuntimeError, match="Log in"):
            await (await client.bulb_service).get_bulbs()


@pytest.mark.asyncio
async def test_mfa_retry_invalidation_and_cancellation(cloud):
    client = Wyzeapy()
    await login(client)
    old = client._auth_lib.token
    for _ in range(2):
        cloud.logins.append("mfa")
        with pytest.raises(TwoFactorAuthenticationEnabled):
            await login(client)
        candidate = client._context.mfa
        assert candidate.token is None
        with pytest.raises(RuntimeError, match="Authentication is in progress"):
            await (await client.camera_service).get_cameras()
        # A malformed/rejected continuation leaves this challenge available for retry.
        with pytest.raises(KeyError):
            await client.login_with_2fa("bad")
        assert client._context.mfa is candidate
        assert client._auth_lib.token is old
        await login(client)  # Replaces the pending challenge.
        assert client._context.mfa is None
        with pytest.raises(RuntimeError, match="Start login"):
            await client.login_with_2fa("123456")
        old = client._auth_lib.token

    cloud.logins.append("mfa")
    with pytest.raises(TwoFactorAuthenticationEnabled):
        await login(client)
    await client.login_with_2fa("123456")
    assert client._auth_lib.token.access_token.endswith(":mfa")
    old = client._auth_lib.token
    cloud.logins.append("mfa")
    with pytest.raises(TwoFactorAuthenticationEnabled):
        await login(client)
    cloud.gate = asyncio.Event()
    task = asyncio.create_task(client.login_with_2fa("123456"))
    await asyncio.wait_for(cloud.entered.wait(), 2)
    task.cancel()
    with pytest.raises(asyncio.CancelledError):
        await task
    assert client._context.mfa is None
    assert client._auth_lib.token is old


@pytest.mark.asyncio
async def test_login_serializes_with_refresh_and_other_clients_remain_usable(cloud):
    a, b = Wyzeapy(), Wyzeapy()
    await asyncio.gather(login(a), login(b, "b@example.test"))
    callback_a, callback_b = MagicMock(), MagicMock()
    a.register_for_token_callback(callback_a)
    b.register_for_token_callback(callback_b)
    old_b = b._auth_lib.token.access_token
    a._auth_lib.token.expired = True
    cloud.gate = asyncio.Event()
    refreshes = [asyncio.create_task(a._auth_lib.refresh_if_should()) for _ in range(2)]
    await asyncio.wait_for(cloud.entered.wait(), 2)
    retry = asyncio.create_task(login(a))
    await asyncio.sleep(0)
    assert a._context.login_pending
    assert cloud.calls["/api/user/login"] == 2
    assert (await (await b.bulb_service).get_bulbs())[0].nickname == old_b
    assert b._auth_lib.token.access_token == old_b
    assert not callback_b.called
    cloud.gate.set()
    await asyncio.gather(*refreshes, retry)
    assert cloud.calls["/app/user/refresh_token"] == 1
    assert callback_a.call_count == 2  # One refresh and one committed login.


@pytest.mark.asyncio
async def test_concurrent_logins_are_serial_and_token_input_is_not_mutated(cloud):
    client = Wyzeapy()
    await login(client)
    cloud.gate = asyncio.Event()
    first = asyncio.create_task(login(client))
    await asyncio.wait_for(cloud.entered.wait(), 2)
    second = asyncio.create_task(login(client))
    await asyncio.sleep(0)
    assert cloud.calls["/api/user/login"] == 2
    cloud.gate.set()
    await asyncio.gather(first, second)
    assert cloud.calls["/api/user/login"] == 3
    token = Token("supplied-access", "supplied-refresh")
    await client.login("a@example.test", "fake", "fake", "fake", token)
    assert token.access_token == "supplied-access"
    assert client._auth_lib.token.access_token == "supplied-refresh:refreshed"


@pytest.mark.asyncio
async def test_updater_cancellation_releases_only_its_manager_lock():
    a, b = UpdateManager(), UpdateManager()
    started = asyncio.Event()

    async def update(device):
        started.set()
        await asyncio.Event().wait()

    device = MagicMock()
    updater = DeviceUpdater(SimpleNamespace(update=update), device, 30)
    task = asyncio.create_task(updater.update(a.mutex))
    await asyncio.wait_for(started.wait(), 2)
    assert a.mutex.locked()
    assert not b.mutex.locked()
    task.cancel()
    with pytest.raises(asyncio.CancelledError):
        await task
    assert not a.mutex.locked()
    device.callback_function.assert_not_called()


@pytest.mark.asyncio
async def test_inventory_coordination_cancellation_does_not_block_another_client(cloud):
    a, b = Wyzeapy(), Wyzeapy()
    await asyncio.gather(login(a), login(b, "b@example.test"))
    sa, sb = await a.sensor_service, await b.sensor_service
    da = Sensor({"mac": "overlapping-id", "product_type": "MotionSensor"})
    db = Sensor({"mac": "overlapping-id", "product_type": "MotionSensor"})
    async with a._context.update_lock:
        waiting = asyncio.create_task(sa.update(da))
        await asyncio.sleep(0)
        updated = await asyncio.wait_for(sb.update(db), 2)
        assert updated.device_params["account"].startswith("b@example.test:")
        assert not waiting.done()
        waiting.cancel()
        with pytest.raises(asyncio.CancelledError):
            await waiting
    updated = await asyncio.wait_for(sa.update(da), 2)
    assert updated.device_params["account"].startswith("a@example.test:")
    assert not a._context.update_lock.locked()
    assert a._context.devices is not b._context.devices


def test_client_rejects_another_event_loop_before_auth_io():
    client = Wyzeapy()

    async def bind():
        client._context.bind_loop()

    asyncio.run(bind())
    with pytest.raises(RuntimeError, match="original event loop"):
        asyncio.run(login(client))


@pytest.mark.asyncio
async def test_cancelled_inventory_read_leaves_cache_and_coordination_usable(cloud):
    a, b = Wyzeapy(), Wyzeapy()
    await asyncio.gather(login(a), login(b, "b@example.test"))
    sa, sb = await a.sensor_service, await b.sensor_service
    cloud.inventory_gate = asyncio.Event()
    task = asyncio.create_task(
        sa.update(Sensor({"mac": "overlapping-id", "product_type": "MotionSensor"}))
    )
    await asyncio.wait_for(cloud.inventory_entered.wait(), 2)
    assert a._context.update_lock.locked()
    assert (await sb.get_updated_params("overlapping-id"))["account"].startswith("b@")
    task.cancel()
    with pytest.raises(asyncio.CancelledError):
        await task
    assert a._context.devices is None
    assert a._context.last_updated_time == 0
    assert not a._context.update_lock.locked()
    cloud.inventory_gate.set()
    assert (await sa.get_updated_params("overlapping-id"))["account"].startswith("a@")


@pytest.mark.parametrize(
    "kind,where", [("camera", "events"), ("camera", "update"), ("sensor", "update")]
)
def test_legacy_workers_survive_login_interruption(kind, where):
    service_class = CameraService if kind == "camera" else SensorService
    service = service_class(WyzeAuthLib(token=Token("fake", "fake")))
    device, callback = MagicMock(), MagicMock()
    service._subscribers = [(device, callback)]
    service._get_event_list = MagicMock(return_value="unused")
    service.update = MagicMock(return_value="unused")
    interrupted = MagicMock()
    interrupted.result.side_effect = _AuthenticationInProgress("login pending")
    events = MagicMock()
    events.result.return_value = {"data": {"event_list": []}}
    updated = MagicMock()
    updated.result.return_value = device
    if where == "events":
        futures = [interrupted, events, updated]
    elif kind == "camera":
        futures = [events, interrupted, events, updated]
    else:
        futures = [interrupted, updated]
    with (
        patch(
            f"wyzeapy.services.{kind}_service.asyncio.run_coroutine_threadsafe",
            side_effect=futures,
        ),
        patch(
            f"wyzeapy.services.{kind}_service.time.sleep",
            side_effect=[None, RuntimeError("stop test worker")],
        ) as sleep,
    ):
        with pytest.raises(RuntimeError, match="stop test worker"):
            service.update_worker(loop=MagicMock())
    callback.assert_called_once_with(device)
    assert sleep.call_count == 2
    sleep.assert_called_with(service._worker_loop_interval)
