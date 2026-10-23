"""Tests must use synthetic responses or explicitly controlled local endpoints."""

from urllib.parse import urlsplit

import aiohttp
import pytest


@pytest.fixture(autouse=True)
def block_external_http(monkeypatch):
    request = aiohttp.ClientSession._request

    async def local_request(self, method, url, **kwargs):
        if urlsplit(str(url)).hostname not in {"localhost", "127.0.0.1", "::1"}:
            raise AssertionError("Tests must not contact external HTTP endpoints")
        return await request(self, method, url, **kwargs)

    monkeypatch.setattr(aiohttp.ClientSession, "_request", local_request)
