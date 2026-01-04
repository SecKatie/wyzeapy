from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.get_plan_binding_list_group_id import GetPlanBindingListGroupId
from ...models.get_plan_binding_list_response_200 import GetPlanBindingListResponse200
from ...types import UNSET, Response


def _get_kwargs(
    *,
    group_id: GetPlanBindingListGroupId,
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

    json_group_id = group_id.value
    params["group_id"] = json_group_id

    params["nonce"] = nonce

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/platform/v2/membership/get_plan_binding_list_by_user",
        "params": params,
    }

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> GetPlanBindingListResponse200 | None:
    if response.status_code == 200:
        response_200 = GetPlanBindingListResponse200.from_dict(response.json())

        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[GetPlanBindingListResponse200]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
    group_id: GetPlanBindingListGroupId,
    nonce: str,
    appid: str,
    appinfo: str,
    phoneid: str,
    signature2: str,
) -> Response[GetPlanBindingListResponse200]:
    """Get membership plan

     Get HMS subscription plan for the user

    Args:
        group_id (GetPlanBindingListGroupId):
        nonce (str):
        appid (str):
        appinfo (str):
        phoneid (str):
        signature2 (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[GetPlanBindingListResponse200]
    """

    kwargs = _get_kwargs(
        group_id=group_id,
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
    group_id: GetPlanBindingListGroupId,
    nonce: str,
    appid: str,
    appinfo: str,
    phoneid: str,
    signature2: str,
) -> GetPlanBindingListResponse200 | None:
    """Get membership plan

     Get HMS subscription plan for the user

    Args:
        group_id (GetPlanBindingListGroupId):
        nonce (str):
        appid (str):
        appinfo (str):
        phoneid (str):
        signature2 (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        GetPlanBindingListResponse200
    """

    return sync_detailed(
        client=client,
        group_id=group_id,
        nonce=nonce,
        appid=appid,
        appinfo=appinfo,
        phoneid=phoneid,
        signature2=signature2,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    group_id: GetPlanBindingListGroupId,
    nonce: str,
    appid: str,
    appinfo: str,
    phoneid: str,
    signature2: str,
) -> Response[GetPlanBindingListResponse200]:
    """Get membership plan

     Get HMS subscription plan for the user

    Args:
        group_id (GetPlanBindingListGroupId):
        nonce (str):
        appid (str):
        appinfo (str):
        phoneid (str):
        signature2 (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[GetPlanBindingListResponse200]
    """

    kwargs = _get_kwargs(
        group_id=group_id,
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
    group_id: GetPlanBindingListGroupId,
    nonce: str,
    appid: str,
    appinfo: str,
    phoneid: str,
    signature2: str,
) -> GetPlanBindingListResponse200 | None:
    """Get membership plan

     Get HMS subscription plan for the user

    Args:
        group_id (GetPlanBindingListGroupId):
        nonce (str):
        appid (str):
        appinfo (str):
        phoneid (str):
        signature2 (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        GetPlanBindingListResponse200
    """

    return (
        await asyncio_detailed(
            client=client,
            group_id=group_id,
            nonce=nonce,
            appid=appid,
            appinfo=appinfo,
            phoneid=phoneid,
            signature2=signature2,
        )
    ).parsed
