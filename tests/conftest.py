"""Pytest configuration and fixtures for Wyzeapy tests."""

import os
import pytest
import pytest_asyncio

from wyzeapy import Wyzeapy


def pytest_configure(config):
    """Register custom markers."""
    config.addinivalue_line(
        "markers", "integration: mark test as integration test (requires credentials)"
    )


@pytest.fixture(scope="module")
def wyze_credentials():
    """Get Wyze credentials from environment variables."""
    email = os.environ.get("WYZE_EMAIL")
    password = os.environ.get("WYZE_PASSWORD")
    key_id = os.environ.get("WYZE_KEY_ID")
    api_key = os.environ.get("WYZE_API_KEY")

    if not all([email, password, key_id, api_key]):
        pytest.skip(
            "Missing credentials. Set WYZE_EMAIL, WYZE_PASSWORD, WYZE_KEY_ID, WYZE_API_KEY"
        )

    return {
        "email": email,
        "password": password,
        "key_id": key_id,
        "api_key": api_key,
    }


@pytest_asyncio.fixture(loop_scope="module", scope="module")
async def wyze_client(wyze_credentials):
    """
    Create a shared authenticated Wyzeapy client for integration tests.

    This fixture is module-scoped to avoid rate limiting from logging in
    multiple times.
    """
    client = await Wyzeapy.create(
        wyze_credentials["email"],
        wyze_credentials["password"],
        wyze_credentials["key_id"],
        wyze_credentials["api_key"],
    )
    yield client
    await client.close()