from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.get_lock_info_with_keypad import GetLockInfoWithKeypad
from ...models.lock_info_response import LockInfoResponse
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    uuid: str,
    with_keypad: GetLockInfoWithKeypad | Unset = UNSET,
    access_token: str,
    key: str,
    timestamp: str,
    sign: str,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["uuid"] = uuid

    json_with_keypad: str | Unset = UNSET
    if not isinstance(with_keypad, Unset):
        json_with_keypad = with_keypad.value

    params["with_keypad"] = json_with_keypad

    params["access_token"] = access_token

    params["key"] = key

    params["timestamp"] = timestamp

    params["sign"] = sign

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/openapi/lock/v1/info",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> LockInfoResponse | None:
    if response.status_code == 200:
        response_200 = LockInfoResponse.from_dict(response.json())

        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[LockInfoResponse]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,
    uuid: str,
    with_keypad: GetLockInfoWithKeypad | Unset = UNSET,
    access_token: str,
    key: str,
    timestamp: str,
    sign: str,
) -> Response[LockInfoResponse]:
    """Get lock info

     Get lock status and information

    Args:
        uuid (str):
        with_keypad (GetLockInfoWithKeypad | Unset):
        access_token (str):
        key (str):
        timestamp (str):
        sign (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[LockInfoResponse]
    """

    kwargs = _get_kwargs(
        uuid=uuid,
        with_keypad=with_keypad,
        access_token=access_token,
        key=key,
        timestamp=timestamp,
        sign=sign,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient | Client,
    uuid: str,
    with_keypad: GetLockInfoWithKeypad | Unset = UNSET,
    access_token: str,
    key: str,
    timestamp: str,
    sign: str,
) -> LockInfoResponse | None:
    """Get lock info

     Get lock status and information

    Args:
        uuid (str):
        with_keypad (GetLockInfoWithKeypad | Unset):
        access_token (str):
        key (str):
        timestamp (str):
        sign (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        LockInfoResponse
    """

    return sync_detailed(
        client=client,
        uuid=uuid,
        with_keypad=with_keypad,
        access_token=access_token,
        key=key,
        timestamp=timestamp,
        sign=sign,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    uuid: str,
    with_keypad: GetLockInfoWithKeypad | Unset = UNSET,
    access_token: str,
    key: str,
    timestamp: str,
    sign: str,
) -> Response[LockInfoResponse]:
    """Get lock info

     Get lock status and information

    Args:
        uuid (str):
        with_keypad (GetLockInfoWithKeypad | Unset):
        access_token (str):
        key (str):
        timestamp (str):
        sign (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[LockInfoResponse]
    """

    kwargs = _get_kwargs(
        uuid=uuid,
        with_keypad=with_keypad,
        access_token=access_token,
        key=key,
        timestamp=timestamp,
        sign=sign,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    uuid: str,
    with_keypad: GetLockInfoWithKeypad | Unset = UNSET,
    access_token: str,
    key: str,
    timestamp: str,
    sign: str,
) -> LockInfoResponse | None:
    """Get lock info

     Get lock status and information

    Args:
        uuid (str):
        with_keypad (GetLockInfoWithKeypad | Unset):
        access_token (str):
        key (str):
        timestamp (str):
        sign (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        LockInfoResponse
    """

    return (
        await asyncio_detailed(
            client=client,
            uuid=uuid,
            with_keypad=with_keypad,
            access_token=access_token,
            key=key,
            timestamp=timestamp,
            sign=sign,
        )
    ).parsed
