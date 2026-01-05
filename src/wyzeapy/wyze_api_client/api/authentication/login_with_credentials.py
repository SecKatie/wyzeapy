from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.login_request import LoginRequest
from ...models.login_response import LoginResponse
from ...types import Response


def _get_kwargs(
    *,
    body: LoginRequest,
    keyid: str,
    apikey: str,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    headers["keyid"] = keyid

    headers["apikey"] = apikey

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/api/user/login",
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> LoginResponse | None:
    if response.status_code == 200:
        response_200 = LoginResponse.from_dict(response.json())

        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Response[LoginResponse]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,
    body: LoginRequest,
    keyid: str,
    apikey: str,
) -> Response[LoginResponse]:
    """Login with email and password

     Authenticate user with email and password. May return MFA options if 2FA is enabled.

    Args:
        keyid (str):
        apikey (str):
        body (LoginRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[LoginResponse]
    """

    kwargs = _get_kwargs(
        body=body,
        keyid=keyid,
        apikey=apikey,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient | Client,
    body: LoginRequest,
    keyid: str,
    apikey: str,
) -> LoginResponse | None:
    """Login with email and password

     Authenticate user with email and password. May return MFA options if 2FA is enabled.

    Args:
        keyid (str):
        apikey (str):
        body (LoginRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        LoginResponse
    """

    return sync_detailed(
        client=client,
        body=body,
        keyid=keyid,
        apikey=apikey,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    body: LoginRequest,
    keyid: str,
    apikey: str,
) -> Response[LoginResponse]:
    """Login with email and password

     Authenticate user with email and password. May return MFA options if 2FA is enabled.

    Args:
        keyid (str):
        apikey (str):
        body (LoginRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[LoginResponse]
    """

    kwargs = _get_kwargs(
        body=body,
        keyid=keyid,
        apikey=apikey,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    body: LoginRequest,
    keyid: str,
    apikey: str,
) -> LoginResponse | None:
    """Login with email and password

     Authenticate user with email and password. May return MFA options if 2FA is enabled.

    Args:
        keyid (str):
        apikey (str):
        body (LoginRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        LoginResponse
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
            keyid=keyid,
            apikey=apikey,
        )
    ).parsed
