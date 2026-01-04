from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.hms_state_status_response import HMSStateStatusResponse
from ...types import UNSET, Response


def _get_kwargs(
    *,
    hms_id: str,
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

    params["hms_id"] = hms_id

    params["nonce"] = nonce

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/api/v1/monitoring/v1/profile/state-status",
        "params": params,
    }

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> HMSStateStatusResponse | None:
    if response.status_code == 200:
        response_200 = HMSStateStatusResponse.from_dict(response.json())

        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[HMSStateStatusResponse]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
    hms_id: str,
    nonce: str,
    appid: str,
    appinfo: str,
    phoneid: str,
    signature2: str,
) -> Response[HMSStateStatusResponse]:
    """Get HMS status

     Get current Home Monitoring System status

    Args:
        hms_id (str):
        nonce (str):
        appid (str):
        appinfo (str):
        phoneid (str):
        signature2 (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HMSStateStatusResponse]
    """

    kwargs = _get_kwargs(
        hms_id=hms_id,
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
    hms_id: str,
    nonce: str,
    appid: str,
    appinfo: str,
    phoneid: str,
    signature2: str,
) -> HMSStateStatusResponse | None:
    """Get HMS status

     Get current Home Monitoring System status

    Args:
        hms_id (str):
        nonce (str):
        appid (str):
        appinfo (str):
        phoneid (str):
        signature2 (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HMSStateStatusResponse
    """

    return sync_detailed(
        client=client,
        hms_id=hms_id,
        nonce=nonce,
        appid=appid,
        appinfo=appinfo,
        phoneid=phoneid,
        signature2=signature2,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    hms_id: str,
    nonce: str,
    appid: str,
    appinfo: str,
    phoneid: str,
    signature2: str,
) -> Response[HMSStateStatusResponse]:
    """Get HMS status

     Get current Home Monitoring System status

    Args:
        hms_id (str):
        nonce (str):
        appid (str):
        appinfo (str):
        phoneid (str):
        signature2 (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HMSStateStatusResponse]
    """

    kwargs = _get_kwargs(
        hms_id=hms_id,
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
    hms_id: str,
    nonce: str,
    appid: str,
    appinfo: str,
    phoneid: str,
    signature2: str,
) -> HMSStateStatusResponse | None:
    """Get HMS status

     Get current Home Monitoring System status

    Args:
        hms_id (str):
        nonce (str):
        appid (str):
        appinfo (str):
        phoneid (str):
        signature2 (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HMSStateStatusResponse
    """

    return (
        await asyncio_detailed(
            client=client,
            hms_id=hms_id,
            nonce=nonce,
            appid=appid,
            appinfo=appinfo,
            phoneid=phoneid,
            signature2=signature2,
        )
    ).parsed
