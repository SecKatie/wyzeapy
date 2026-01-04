from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.get_irrigation_schedule_runs_response_200 import (
    GetIrrigationScheduleRunsResponse200,
)
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    device_id: str,
    nonce: str,
    limit: int | Unset = 2,
    appid: str,
    appinfo: str,
    phoneid: str,
    signature2: str,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    headers["appid"] = appid

    headers["appinfo"] = appinfo

    headers["phoneid"] = phoneid

    headers["signature2"] = signature2

    params: dict[str, Any] = {}

    params["device_id"] = device_id

    params["nonce"] = nonce

    params["limit"] = limit

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/plugin/irrigation/schedule_runs",
        "params": params,
    }

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> GetIrrigationScheduleRunsResponse200 | None:
    if response.status_code == 200:
        response_200 = GetIrrigationScheduleRunsResponse200.from_dict(response.json())

        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[GetIrrigationScheduleRunsResponse200]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
    device_id: str,
    nonce: str,
    limit: int | Unset = 2,
    appid: str,
    appinfo: str,
    phoneid: str,
    signature2: str,
) -> Response[GetIrrigationScheduleRunsResponse200]:
    """Get schedule runs

     Get recent schedule runs for an irrigation controller

    Args:
        device_id (str):
        nonce (str):
        limit (int | Unset):  Default: 2.
        appid (str):
        appinfo (str):
        phoneid (str):
        signature2 (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[GetIrrigationScheduleRunsResponse200]
    """

    kwargs = _get_kwargs(
        device_id=device_id,
        nonce=nonce,
        limit=limit,
        appid=appid,
        appinfo=appinfo,
        phoneid=phoneid,
        signature2=signature2,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient,
    device_id: str,
    nonce: str,
    limit: int | Unset = 2,
    appid: str,
    appinfo: str,
    phoneid: str,
    signature2: str,
) -> GetIrrigationScheduleRunsResponse200 | None:
    """Get schedule runs

     Get recent schedule runs for an irrigation controller

    Args:
        device_id (str):
        nonce (str):
        limit (int | Unset):  Default: 2.
        appid (str):
        appinfo (str):
        phoneid (str):
        signature2 (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        GetIrrigationScheduleRunsResponse200
    """

    return sync_detailed(
        client=client,
        device_id=device_id,
        nonce=nonce,
        limit=limit,
        appid=appid,
        appinfo=appinfo,
        phoneid=phoneid,
        signature2=signature2,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    device_id: str,
    nonce: str,
    limit: int | Unset = 2,
    appid: str,
    appinfo: str,
    phoneid: str,
    signature2: str,
) -> Response[GetIrrigationScheduleRunsResponse200]:
    """Get schedule runs

     Get recent schedule runs for an irrigation controller

    Args:
        device_id (str):
        nonce (str):
        limit (int | Unset):  Default: 2.
        appid (str):
        appinfo (str):
        phoneid (str):
        signature2 (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[GetIrrigationScheduleRunsResponse200]
    """

    kwargs = _get_kwargs(
        device_id=device_id,
        nonce=nonce,
        limit=limit,
        appid=appid,
        appinfo=appinfo,
        phoneid=phoneid,
        signature2=signature2,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    device_id: str,
    nonce: str,
    limit: int | Unset = 2,
    appid: str,
    appinfo: str,
    phoneid: str,
    signature2: str,
) -> GetIrrigationScheduleRunsResponse200 | None:
    """Get schedule runs

     Get recent schedule runs for an irrigation controller

    Args:
        device_id (str):
        nonce (str):
        limit (int | Unset):  Default: 2.
        appid (str):
        appinfo (str):
        phoneid (str):
        signature2 (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        GetIrrigationScheduleRunsResponse200
    """

    return (
        await asyncio_detailed(
            client=client,
            device_id=device_id,
            nonce=nonce,
            limit=limit,
            appid=appid,
            appinfo=appinfo,
            phoneid=phoneid,
            signature2=signature2,
        )
    ).parsed
