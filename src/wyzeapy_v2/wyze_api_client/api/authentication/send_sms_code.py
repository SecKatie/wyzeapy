from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.send_sms_code_body import SendSmsCodeBody
from ...models.send_sms_code_response_200 import SendSmsCodeResponse200
from ...types import Response


def _get_kwargs(
    *,
    body: SendSmsCodeBody,
    keyid: str,
    apikey: str,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    headers["keyid"] = keyid

    headers["apikey"] = apikey

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/user/login/sendSmsCode",
    }

    _kwargs["data"] = body.to_dict()

    headers["Content-Type"] = "application/x-www-form-urlencoded"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> SendSmsCodeResponse200 | None:
    if response.status_code == 200:
        response_200 = SendSmsCodeResponse200.from_dict(response.json())

        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[SendSmsCodeResponse200]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,
    body: SendSmsCodeBody,
    keyid: str,
    apikey: str,
) -> Response[SendSmsCodeResponse200]:
    """Send SMS verification code

     Request SMS verification code for 2FA login

    Args:
        keyid (str):
        apikey (str):
        body (SendSmsCodeBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[SendSmsCodeResponse200]
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
    body: SendSmsCodeBody,
    keyid: str,
    apikey: str,
) -> SendSmsCodeResponse200 | None:
    """Send SMS verification code

     Request SMS verification code for 2FA login

    Args:
        keyid (str):
        apikey (str):
        body (SendSmsCodeBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        SendSmsCodeResponse200
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
    body: SendSmsCodeBody,
    keyid: str,
    apikey: str,
) -> Response[SendSmsCodeResponse200]:
    """Send SMS verification code

     Request SMS verification code for 2FA login

    Args:
        keyid (str):
        apikey (str):
        body (SendSmsCodeBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[SendSmsCodeResponse200]
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
    body: SendSmsCodeBody,
    keyid: str,
    apikey: str,
) -> SendSmsCodeResponse200 | None:
    """Send SMS verification code

     Request SMS verification code for 2FA login

    Args:
        keyid (str):
        apikey (str):
        body (SendSmsCodeBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        SendSmsCodeResponse200
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
            keyid=keyid,
            apikey=apikey,
        )
    ).parsed
