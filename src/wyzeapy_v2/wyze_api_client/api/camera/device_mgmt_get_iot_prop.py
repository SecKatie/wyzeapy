from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.device_mgmt_get_iot_prop_request import DeviceMgmtGetIotPropRequest
from ...models.device_mgmt_get_iot_prop_response_200 import (
    DeviceMgmtGetIotPropResponse200,
)
from ...types import Response


def _get_kwargs(
    *,
    body: DeviceMgmtGetIotPropRequest,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/device-management/api/device-property/get_iot_prop",
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> DeviceMgmtGetIotPropResponse200 | None:
    if response.status_code == 200:
        response_200 = DeviceMgmtGetIotPropResponse200.from_dict(response.json())

        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[DeviceMgmtGetIotPropResponse200]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
    body: DeviceMgmtGetIotPropRequest,
) -> Response[DeviceMgmtGetIotPropResponse200]:
    """Get IoT properties (Device Mgmt)

     Get IoT properties for newer camera models

    Args:
        body (DeviceMgmtGetIotPropRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[DeviceMgmtGetIotPropResponse200]
    """

    kwargs = _get_kwargs(
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient,
    body: DeviceMgmtGetIotPropRequest,
) -> DeviceMgmtGetIotPropResponse200 | None:
    """Get IoT properties (Device Mgmt)

     Get IoT properties for newer camera models

    Args:
        body (DeviceMgmtGetIotPropRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        DeviceMgmtGetIotPropResponse200
    """

    return sync_detailed(
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    body: DeviceMgmtGetIotPropRequest,
) -> Response[DeviceMgmtGetIotPropResponse200]:
    """Get IoT properties (Device Mgmt)

     Get IoT properties for newer camera models

    Args:
        body (DeviceMgmtGetIotPropRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[DeviceMgmtGetIotPropResponse200]
    """

    kwargs = _get_kwargs(
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    body: DeviceMgmtGetIotPropRequest,
) -> DeviceMgmtGetIotPropResponse200 | None:
    """Get IoT properties (Device Mgmt)

     Get IoT properties for newer camera models

    Args:
        body (DeviceMgmtGetIotPropRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        DeviceMgmtGetIotPropResponse200
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
        )
    ).parsed
