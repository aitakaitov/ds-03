from http import HTTPStatus
from typing import Any, Dict, List, Optional, Union, cast

import httpx

from ...client import Client
from ...models.code_response import CodeResponse
from ...models.unprocessable_entity import UnprocessableEntity
from ...types import UNSET, Response


def _get_kwargs(
    *,
    client: Client,
    key: str,
    value: str,
) -> Dict[str, Any]:
    url = "{}/key".format(client.base_url)

    headers: Dict[str, str] = client.get_headers()
    cookies: Dict[str, Any] = client.get_cookies()

    params: Dict[str, Any] = {}
    params["key"] = key

    params["value"] = value

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    return {
        "method": "put",
        "url": url,
        "headers": headers,
        "cookies": cookies,
        "timeout": client.get_timeout(),
        "params": params,
    }


def _parse_response(*, response: httpx.Response) -> Optional[Union[Any, CodeResponse, List["UnprocessableEntity"]]]:
    if response.status_code == HTTPStatus.OK:
        response_200 = CodeResponse.from_dict(response.json())

        return response_200
    if response.status_code == HTTPStatus.CREATED:
        response_201 = CodeResponse.from_dict(response.json())

        return response_201
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


def _build_response(*, response: httpx.Response) -> Response[Union[Any, CodeResponse, List["UnprocessableEntity"]]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(response=response),
    )


def sync_detailed(
    *,
    client: Client,
    key: str,
    value: str,
) -> Response[Union[Any, CodeResponse, List["UnprocessableEntity"]]]:
    """Saves the key-value pair. Rewrites the value if the key exists.

     :param query: query</br>:return: 200 if no such key existed, 201 if it was overwritten

    Args:
        key (str):
        value (str):

    Returns:
        Response[Union[Any, CodeResponse, List['UnprocessableEntity']]]
    """

    kwargs = _get_kwargs(
        client=client,
        key=key,
        value=value,
    )

    response = httpx.request(
        verify=client.verify_ssl,
        **kwargs,
    )

    return _build_response(response=response)


def sync(
    *,
    client: Client,
    key: str,
    value: str,
) -> Optional[Union[Any, CodeResponse, List["UnprocessableEntity"]]]:
    """Saves the key-value pair. Rewrites the value if the key exists.

     :param query: query</br>:return: 200 if no such key existed, 201 if it was overwritten

    Args:
        key (str):
        value (str):

    Returns:
        Response[Union[Any, CodeResponse, List['UnprocessableEntity']]]
    """

    return sync_detailed(
        client=client,
        key=key,
        value=value,
    ).parsed


async def asyncio_detailed(
    *,
    client: Client,
    key: str,
    value: str,
) -> Response[Union[Any, CodeResponse, List["UnprocessableEntity"]]]:
    """Saves the key-value pair. Rewrites the value if the key exists.

     :param query: query</br>:return: 200 if no such key existed, 201 if it was overwritten

    Args:
        key (str):
        value (str):

    Returns:
        Response[Union[Any, CodeResponse, List['UnprocessableEntity']]]
    """

    kwargs = _get_kwargs(
        client=client,
        key=key,
        value=value,
    )

    async with httpx.AsyncClient(verify=client.verify_ssl) as _client:
        response = await _client.request(**kwargs)

    return _build_response(response=response)


async def asyncio(
    *,
    client: Client,
    key: str,
    value: str,
) -> Optional[Union[Any, CodeResponse, List["UnprocessableEntity"]]]:
    """Saves the key-value pair. Rewrites the value if the key exists.

     :param query: query</br>:return: 200 if no such key existed, 201 if it was overwritten

    Args:
        key (str):
        value (str):

    Returns:
        Response[Union[Any, CodeResponse, List['UnprocessableEntity']]]
    """

    return (
        await asyncio_detailed(
            client=client,
            key=key,
            value=value,
        )
    ).parsed
