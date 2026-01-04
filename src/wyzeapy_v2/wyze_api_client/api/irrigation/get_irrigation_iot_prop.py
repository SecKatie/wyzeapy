from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.get_irrigation_iot_prop_response_200 import (
    GetIrrigationIotPropResponse200,
)
from ...types import UNSET, Response


def _get_kwargs(
    *,
    keys: str,
    did: str,
    nonce: int,
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

    params["keys"] = keys

    params["did"] = did

    params["nonce"] = nonce

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/plugin/irrigation/get_iot_prop",
        "params": params,
    }

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> GetIrrigationIotPropResponse200 | None:
    if response.status_code == 200:
        response_200 = GetIrrigationIotPropResponse200.from_dict(response.json())

        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[GetIrrigationIotPropResponse200]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
    keys: str,
    did: str,
    nonce: int,
    appid: str,
    appinfo: str,
    phoneid: str,
    signature2: str,
) -> Response[GetIrrigationIotPropResponse200]:
    """Get irrigation properties

     Get IoT properties for an irrigation controller

    Args:
        keys (str):
        did (str):
        nonce (int):
        appid (str):
        appinfo (str):
        phoneid (str):
        signature2 (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[GetIrrigationIotPropResponse200]
    """

    kwargs = _get_kwargs(
        keys=keys,
        did=did,
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
    keys: str,
    did: str,
    nonce: int,
    appid: str,
    appinfo: str,
    phoneid: str,
    signature2: str,
) -> GetIrrigationIotPropResponse200 | None:
    """Get irrigation properties

     Get IoT properties for an irrigation controller

    Args:
        keys (str):
        did (str):
        nonce (int):
        appid (str):
        appinfo (str):
        phoneid (str):
        signature2 (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        GetIrrigationIotPropResponse200
    """

    return sync_detailed(
        client=client,
        keys=keys,
        did=did,
        nonce=nonce,
        appid=appid,
        appinfo=appinfo,
        phoneid=phoneid,
        signature2=signature2,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    keys: str,
    did: str,
    nonce: int,
    appid: str,
    appinfo: str,
    phoneid: str,
    signature2: str,
) -> Response[GetIrrigationIotPropResponse200]:
    """Get irrigation properties

     Get IoT properties for an irrigation controller

    Args:
        keys (str):
        did (str):
        nonce (int):
        appid (str):
        appinfo (str):
        phoneid (str):
        signature2 (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[GetIrrigationIotPropResponse200]
    """

    kwargs = _get_kwargs(
        keys=keys,
        did=did,
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
    keys: str,
    did: str,
    nonce: int,
    appid: str,
    appinfo: str,
    phoneid: str,
    signature2: str,
) -> GetIrrigationIotPropResponse200 | None:
    """Get irrigation properties

     Get IoT properties for an irrigation controller

    Args:
        keys (str):
        did (str):
        nonce (int):
        appid (str):
        appinfo (str):
        phoneid (str):
        signature2 (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        GetIrrigationIotPropResponse200
    """

    return (
        await asyncio_detailed(
            client=client,
            keys=keys,
            did=did,
            nonce=nonce,
            appid=appid,
            appinfo=appinfo,
            phoneid=phoneid,
            signature2=signature2,
        )
    ).parsed
