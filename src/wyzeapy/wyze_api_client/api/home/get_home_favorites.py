from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.get_home_favorites_request import GetHomeFavoritesRequest
from ...models.get_home_favorites_response import GetHomeFavoritesResponse
from ...types import Response


def _get_kwargs(
    *,
    body: GetHomeFavoritesRequest,
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

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/app/v4/home/get-favorites",
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> GetHomeFavoritesResponse | None:
    if response.status_code == 200:
        response_200 = GetHomeFavoritesResponse.from_dict(response.json())

        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[GetHomeFavoritesResponse]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
    body: GetHomeFavoritesRequest,
    appid: str,
    appinfo: str,
    phoneid: str,
    signature2: str,
) -> Response[GetHomeFavoritesResponse]:
    """Get home favorites

     Get favorite devices and device list for a home

    Args:
        appid (str):
        appinfo (str):
        phoneid (str):
        signature2 (str):
        body (GetHomeFavoritesRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[GetHomeFavoritesResponse]
    """

    kwargs = _get_kwargs(
        body=body,
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
    body: GetHomeFavoritesRequest,
    appid: str,
    appinfo: str,
    phoneid: str,
    signature2: str,
) -> GetHomeFavoritesResponse | None:
    """Get home favorites

     Get favorite devices and device list for a home

    Args:
        appid (str):
        appinfo (str):
        phoneid (str):
        signature2 (str):
        body (GetHomeFavoritesRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        GetHomeFavoritesResponse
    """

    return sync_detailed(
        client=client,
        body=body,
        appid=appid,
        appinfo=appinfo,
        phoneid=phoneid,
        signature2=signature2,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    body: GetHomeFavoritesRequest,
    appid: str,
    appinfo: str,
    phoneid: str,
    signature2: str,
) -> Response[GetHomeFavoritesResponse]:
    """Get home favorites

     Get favorite devices and device list for a home

    Args:
        appid (str):
        appinfo (str):
        phoneid (str):
        signature2 (str):
        body (GetHomeFavoritesRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[GetHomeFavoritesResponse]
    """

    kwargs = _get_kwargs(
        body=body,
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
    body: GetHomeFavoritesRequest,
    appid: str,
    appinfo: str,
    phoneid: str,
    signature2: str,
) -> GetHomeFavoritesResponse | None:
    """Get home favorites

     Get favorite devices and device list for a home

    Args:
        appid (str):
        appinfo (str):
        phoneid (str):
        signature2 (str):
        body (GetHomeFavoritesRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        GetHomeFavoritesResponse
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
            appid=appid,
            appinfo=appinfo,
            phoneid=phoneid,
            signature2=signature2,
        )
    ).parsed
