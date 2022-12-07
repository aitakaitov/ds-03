from http import HTTPStatus
from typing import Any, Dict, List, Optional, Union, cast

import httpx

from ...client import Client
from ...models.code_response import CodeResponse
from ...models.get_response import GetResponse
from ...models.unprocessable_entity import UnprocessableEntity
from ...types import UNSET, Response


def _get_kwargs(
    *,
    client: Client,
    key: str,
) -> Dict[str, Any]:
    url = "{}/key".format(client.base_url)

    headers: Dict[str, str] = client.get_headers()
    cookies: Dict[str, Any] = client.get_cookies()

    params: Dict[str, Any] = {}
    params["key"] = key

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    return {
        "method": "get",
        "url": url,
        "headers": headers,
        "cookies": cookies,
        "timeout": client.get_timeout(),
        "params": params,
    }


def _parse_response(
    *, response: httpx.Response
) -> Optional[Union[Any, CodeResponse, GetResponse, List["UnprocessableEntity"]]]:
    if response.status_code == HTTPStatus.OK:
        response_200 = GetResponse.from_dict(response.json())

        return response_200
    if response.status_code == HTTPStatus.NOT_FOUND:
        response_404 = CodeResponse.from_dict(response.json())

        return response_404
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


def _build_response(
    *, response: httpx.Response
) -> Response[Union[Any, CodeResponse, GetResponse, List["UnprocessableEntity"]]]:
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
) -> Response[Union[Any, CodeResponse, GetResponse, List["UnprocessableEntity"]]]:
    """Returns the value for a given key if it exists, otherwise returns error 404

     :param query: query</br>:return: 200 and value if OK else 404

    Args:
        key (str):

    Returns:
        Response[Union[Any, CodeResponse, GetResponse, List['UnprocessableEntity']]]
    """

    kwargs = _get_kwargs(
        client=client,
        key=key,
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
) -> Optional[Union[Any, CodeResponse, GetResponse, List["UnprocessableEntity"]]]:
    """Returns the value for a given key if it exists, otherwise returns error 404

     :param query: query</br>:return: 200 and value if OK else 404

    Args:
        key (str):

    Returns:
        Response[Union[Any, CodeResponse, GetResponse, List['UnprocessableEntity']]]
    """

    return sync_detailed(
        client=client,
        key=key,
    ).parsed


async def asyncio_detailed(
    *,
    client: Client,
    key: str,
) -> Response[Union[Any, CodeResponse, GetResponse, List["UnprocessableEntity"]]]:
    """Returns the value for a given key if it exists, otherwise returns error 404

     :param query: query</br>:return: 200 and value if OK else 404

    Args:
        key (str):

    Returns:
        Response[Union[Any, CodeResponse, GetResponse, List['UnprocessableEntity']]]
    """

    kwargs = _get_kwargs(
        client=client,
        key=key,
    )

    async with httpx.AsyncClient(verify=client.verify_ssl) as _client:
        response = await _client.request(**kwargs)

    return _build_response(response=response)


async def asyncio(
    *,
    client: Client,
    key: str,
) -> Optional[Union[Any, CodeResponse, GetResponse, List["UnprocessableEntity"]]]:
    """Returns the value for a given key if it exists, otherwise returns error 404

     :param query: query</br>:return: 200 and value if OK else 404

    Args:
        key (str):

    Returns:
        Response[Union[Any, CodeResponse, GetResponse, List['UnprocessableEntity']]]
    """

    return (
        await asyncio_detailed(
            client=client,
            key=key,
        )
    ).parsed
