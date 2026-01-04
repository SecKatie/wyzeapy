from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.user_profile_response import UserProfileResponse
from ...types import UNSET, Response


def _get_kwargs(
    *,
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

    params["nonce"] = nonce

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/app/v2/platform/get_user_profile",
        "params": params,
    }

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> UserProfileResponse | None:
    if response.status_code == 200:
        response_200 = UserProfileResponse.from_dict(response.json())

        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[UserProfileResponse]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
    nonce: str,
    appid: str,
    appinfo: str,
    phoneid: str,
    signature2: str,
) -> Response[UserProfileResponse]:
    """Get user profile

     Get user profile information including notification settings

    Args:
        nonce (str):
        appid (str):
        appinfo (str):
        phoneid (str):
        signature2 (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[UserProfileResponse]
    """

    kwargs = _get_kwargs(
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
    nonce: str,
    appid: str,
    appinfo: str,
    phoneid: str,
    signature2: str,
) -> UserProfileResponse | None:
    """Get user profile

     Get user profile information including notification settings

    Args:
        nonce (str):
        appid (str):
        appinfo (str):
        phoneid (str):
        signature2 (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        UserProfileResponse
    """

    return sync_detailed(
        client=client,
        nonce=nonce,
        appid=appid,
        appinfo=appinfo,
        phoneid=phoneid,
        signature2=signature2,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    nonce: str,
    appid: str,
    appinfo: str,
    phoneid: str,
    signature2: str,
) -> Response[UserProfileResponse]:
    """Get user profile

     Get user profile information including notification settings

    Args:
        nonce (str):
        appid (str):
        appinfo (str):
        phoneid (str):
        signature2 (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[UserProfileResponse]
    """

    kwargs = _get_kwargs(
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
    nonce: str,
    appid: str,
    appinfo: str,
    phoneid: str,
    signature2: str,
) -> UserProfileResponse | None:
    """Get user profile

     Get user profile information including notification settings

    Args:
        nonce (str):
        appid (str):
        appinfo (str):
        phoneid (str):
        signature2 (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        UserProfileResponse
    """

    return (
        await asyncio_detailed(
            client=client,
            nonce=nonce,
            appid=appid,
            appinfo=appinfo,
            phoneid=phoneid,
            signature2=signature2,
        )
    ).parsed
