from http import HTTPStatus
from typing import Any, Dict, List, Optional, Union, cast

import httpx

from ...client import Client
from ...models.all_keys_response import AllKeysResponse
from ...models.unprocessable_entity import UnprocessableEntity
from ...types import Response


def _get_kwargs(
    *,
    client: Client,
) -> Dict[str, Any]:
    url = "{}/keys".format(client.base_url)

    headers: Dict[str, str] = client.get_headers()
    cookies: Dict[str, Any] = client.get_cookies()

    return {
        "method": "get",
        "url": url,
        "headers": headers,
        "cookies": cookies,
        "timeout": client.get_timeout(),
    }


def _parse_response(*, response: httpx.Response) -> Optional[Union[AllKeysResponse, Any, List["UnprocessableEntity"]]]:
    if response.status_code == HTTPStatus.OK:
        response_200 = AllKeysResponse.from_dict(response.json())

        return response_200
    if response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY:
        response_422 = []
        _response_422 = response.json()
        for response_422_item_data in _response_422:
            response_422_item = UnprocessableEntity.from_dict(response_422_item_data)

            response_422.append(response_422_item)

        return response_422
    if response.status_code == HTTPStatus.INTERNAL_SERVER_ERROR:
        response_500 = cast(Any, None)
        return response_500
    return None


def _build_response(*, response: httpx.Response) -> Response[Union[AllKeysResponse, Any, List["UnprocessableEntity"]]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(response=response),
    )


def sync_detailed(
    *,
    client: Client,
) -> Response[Union[AllKeysResponse, Any, List["UnprocessableEntity"]]]:
    """
    Returns:
        Response[Union[AllKeysResponse, Any, List['UnprocessableEntity']]]
    """

    kwargs = _get_kwargs(
        client=client,
    )

    response = httpx.request(
        verify=client.verify_ssl,
        **kwargs,
    )

    return _build_response(response=response)


def sync(
    *,
    client: Client,
) -> Optional[Union[AllKeysResponse, Any, List["UnprocessableEntity"]]]:
    """
    Returns:
        Response[Union[AllKeysResponse, Any, List['UnprocessableEntity']]]
    """

    return sync_detailed(
        client=client,
    ).parsed


async def asyncio_detailed(
    *,
    client: Client,
) -> Response[Union[AllKeysResponse, Any, List["UnprocessableEntity"]]]:
    """
    Returns:
        Response[Union[AllKeysResponse, Any, List['UnprocessableEntity']]]
    """

    kwargs = _get_kwargs(
        client=client,
    )

    async with httpx.AsyncClient(verify=client.verify_ssl) as _client:
        response = await _client.request(**kwargs)

    return _build_response(response=response)


async def asyncio(
    *,
    client: Client,
) -> Optional[Union[AllKeysResponse, Any, List["UnprocessableEntity"]]]:
    """
    Returns:
        Response[Union[AllKeysResponse, Any, List['UnprocessableEntity']]]
    """

    return (
        await asyncio_detailed(
            client=client,
        )
    ).parsed
