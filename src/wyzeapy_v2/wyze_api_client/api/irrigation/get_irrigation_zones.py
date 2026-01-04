from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.irrigation_zone_response import IrrigationZoneResponse
from ...types import UNSET, Response


def _get_kwargs(
    *,
    device_id: str,
    nonce: str,
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

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/plugin/irrigation/zone",
        "params": params,
    }

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> IrrigationZoneResponse | None:
    if response.status_code == 200:
        response_200 = IrrigationZoneResponse.from_dict(response.json())

        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[IrrigationZoneResponse]:
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
    appid: str,
    appinfo: str,
    phoneid: str,
    signature2: str,
) -> Response[IrrigationZoneResponse]:
    """Get irrigation zones

     Get zones for an irrigation controller

    Args:
        device_id (str):
        nonce (str):
        appid (str):
        appinfo (str):
        phoneid (str):
        signature2 (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[IrrigationZoneResponse]
    """

    kwargs = _get_kwargs(
        device_id=device_id,
        nonce=nonce,
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
    appid: str,
    appinfo: str,
    phoneid: str,
    signature2: str,
) -> IrrigationZoneResponse | None:
    """Get irrigation zones

     Get zones for an irrigation controller

    Args:
        device_id (str):
        nonce (str):
        appid (str):
        appinfo (str):
        phoneid (str):
        signature2 (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        IrrigationZoneResponse
    """

    return sync_detailed(
        client=client,
        device_id=device_id,
        nonce=nonce,
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
    appid: str,
    appinfo: str,
    phoneid: str,
    signature2: str,
) -> Response[IrrigationZoneResponse]:
    """Get irrigation zones

     Get zones for an irrigation controller

    Args:
        device_id (str):
        nonce (str):
        appid (str):
        appinfo (str):
        phoneid (str):
        signature2 (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[IrrigationZoneResponse]
    """

    kwargs = _get_kwargs(
        device_id=device_id,
        nonce=nonce,
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
    appid: str,
    appinfo: str,
    phoneid: str,
    signature2: str,
) -> IrrigationZoneResponse | None:
    """Get irrigation zones

     Get zones for an irrigation controller

    Args:
        device_id (str):
        nonce (str):
        appid (str):
        appinfo (str):
        phoneid (str):
        signature2 (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        IrrigationZoneResponse
    """

    return (
        await asyncio_detailed(
            client=client,
            device_id=device_id,
            nonce=nonce,
            appid=appid,
            appinfo=appinfo,
            phoneid=phoneid,
            signature2=signature2,
        )
    ).parsed
