from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.standard_response import StandardResponse
from ...models.toggle_management_request import ToggleManagementRequest
from ...types import Response


def _get_kwargs(
    *,
    body: ToggleManagementRequest,
    timestamp: str,
    appid: str,
    source: str,
    signature2: str,
    appplatform: str,
    appversion: str,
    requestid: str,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    headers["timestamp"] = timestamp

    headers["appid"] = appid

    headers["source"] = source

    headers["signature2"] = signature2

    headers["appplatform"] = appplatform

    headers["appversion"] = appversion

    headers["requestid"] = requestid

    _kwargs: dict[str, Any] = {
        "method": "put",
        "url": "/v4/subscription-service/toggle-management",
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> StandardResponse | None:
    if response.status_code == 200:
        response_200 = StandardResponse.from_dict(response.json())

        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[StandardResponse]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
    body: ToggleManagementRequest,
    timestamp: str,
    appid: str,
    source: str,
    signature2: str,
    appplatform: str,
    appversion: str,
    requestid: str,
) -> Response[StandardResponse]:
    """Set toggle state

     Set camera toggles like event recording and notifications

    Args:
        timestamp (str):
        appid (str):
        source (str):
        signature2 (str):
        appplatform (str):
        appversion (str):
        requestid (str):
        body (ToggleManagementRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[StandardResponse]
    """

    kwargs = _get_kwargs(
        body=body,
        timestamp=timestamp,
        appid=appid,
        source=source,
        signature2=signature2,
        appplatform=appplatform,
        appversion=appversion,
        requestid=requestid,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient,
    body: ToggleManagementRequest,
    timestamp: str,
    appid: str,
    source: str,
    signature2: str,
    appplatform: str,
    appversion: str,
    requestid: str,
) -> StandardResponse | None:
    """Set toggle state

     Set camera toggles like event recording and notifications

    Args:
        timestamp (str):
        appid (str):
        source (str):
        signature2 (str):
        appplatform (str):
        appversion (str):
        requestid (str):
        body (ToggleManagementRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        StandardResponse
    """

    return sync_detailed(
        client=client,
        body=body,
        timestamp=timestamp,
        appid=appid,
        source=source,
        signature2=signature2,
        appplatform=appplatform,
        appversion=appversion,
        requestid=requestid,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    body: ToggleManagementRequest,
    timestamp: str,
    appid: str,
    source: str,
    signature2: str,
    appplatform: str,
    appversion: str,
    requestid: str,
) -> Response[StandardResponse]:
    """Set toggle state

     Set camera toggles like event recording and notifications

    Args:
        timestamp (str):
        appid (str):
        source (str):
        signature2 (str):
        appplatform (str):
        appversion (str):
        requestid (str):
        body (ToggleManagementRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[StandardResponse]
    """

    kwargs = _get_kwargs(
        body=body,
        timestamp=timestamp,
        appid=appid,
        source=source,
        signature2=signature2,
        appplatform=appplatform,
        appversion=appversion,
        requestid=requestid,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    body: ToggleManagementRequest,
    timestamp: str,
    appid: str,
    source: str,
    signature2: str,
    appplatform: str,
    appversion: str,
    requestid: str,
) -> StandardResponse | None:
    """Set toggle state

     Set camera toggles like event recording and notifications

    Args:
        timestamp (str):
        appid (str):
        source (str):
        signature2 (str):
        appplatform (str):
        appversion (str):
        requestid (str):
        body (ToggleManagementRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        StandardResponse
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
            timestamp=timestamp,
            appid=appid,
            source=source,
            signature2=signature2,
            appplatform=appplatform,
            appversion=appversion,
            requestid=requestid,
        )
    ).parsed
