"""Core python interface for the wallhaven.cc (https://wallhaven.cc) API."""
from __future__ import annotations

from typing import Any, Union, cast

from httpx import AsyncClient, Response
from yarl import URL

from haven import errors
from haven.entities import Collection, UserSettings, Wallpapper
from haven.search_filters import SearchParams

JsonObjType = dict[str, Union['JsonType', int, str]]
JsonObjListType = list[JsonObjType]
JsonType = JsonObjType | list['JsonType']


class HavenClient():
    """HavenClient provides a simple interface to the wallhaven API.

    Typical usage::

        APIKEY = '<your_api_key>'

        async with httpx.AsyncClient() as http_client:
            client = HavenClient(http_client, APIKEY)
            print(await client.get_collections())

    See https://wallhaven.cc/help/api for more information.
    """

    def __init__(
        self,
        http_client: AsyncClient,
        apikey: str | None = None,
        apihost: str = 'https://wallhaven.cc',
    ):
        """Create a new HavenClient.

        Arguments:
            http_client(AsyncClient): An AsyncClient instance.
            apikey(str): Your wallhaven.cc API key.
            apihost(str): The wallhaven.cc API host. Default to 'https://wallhaven.cc'.
        """
        self.apiurl = URL(apihost) / 'api/v1'
        self.apikey = apikey

        self._client = http_client
        if apikey:
            self._client.headers['X-API-Key'] = apikey

    async def get_collections(self, username: str | None = None) -> list[Collection]:
        """Get a list of collections.

        Arguments:
            username(str): The username of the user. Defaults to None.
                If not specified, the current user collections(by apikey) will be returned.

        Returns:
            list[Collection]: A list of collections.

        Raises:
            UserOrApikeyNotSetError: If user and api key both aren't set.
        """
        if not username and not self.apikey:
            raise errors.UserOrApikeyNotSetError()

        url = self.apiurl / 'collections'
        if username:
            url /= username

        resp = await self._client.get(str(url))
        return cast(list[Collection], self._get_resp_data(resp))

    async def get_wallpapper_list(self, username: str, id_: int) -> list[Wallpapper]:
        """Get an image collection.

        Arguments:
            username(str): The username of the user.
            id_(int): The id of the collection.

        Returns:
            Collection: The image collection data.
        """
        url = self.apiurl / f'collections/{username}/{id_}'

        resp = await self._client.get(str(url))
        return cast(list[Wallpapper], self._get_resp_data(resp))

    async def find_wallpapers(self, filters: SearchParams) -> list[Wallpapper]:
        """Find wallpapers using the filters.

        Arguments:
            filters(SearchParams): The filters to use.

        Returns:
            list[Wallpapper]: A list of wallpapers.
        """
        query_params = {}

        q_values = self._build_query_param(filters)
        if q_values:
            query_params['q'] = q_values

        if filters.categories:
            query_params['categories'] = f'{filters.categories:03b}'  # 3-bit binary (like 010)

        if filters.purity:
            query_params['purity'] = f'{filters.purity:03b}'

        if filters.sorting:
            query_params['sorting'] = filters.sorting

        if filters.order:
            query_params['order'] = filters.order

        if filters.top_range:
            query_params['topRange'] = filters.top_range

        if filters.atleast:
            query_params['atleast'] = filters.atleast

        if filters.resolutions:
            query_params['resolutions'] = filters.resolutions

        if filters.ratios:
            query_params['ratios'] = filters.ratios

        if filters.colors:
            query_params['colors'] = filters.colors

        url = self.apiurl / 'search' % query_params

        resp = await self._client.get(str(url))
        return cast(list[Wallpapper], self._get_resp_data(resp))

    async def get_user_settings(self) -> UserSettings:
        """Get the user settings.

        Returns:
            UserSettings: The user settings.

        Raises:
            ApikeyNotSetError: If api key isn't set.
        """
        if not self.apikey:
            raise errors.ApikeyNotSetError

        url = self.apiurl / 'settings'
        resp = await self._client.get(str(url))
        return cast(UserSettings, self._get_resp_data(resp))

    def _build_query_param(self, filters: SearchParams) -> str | None:
        query_parts = []

        if filters.tags:
            query_parts.append(' '.join(filters.tags))

        if filters.exclude_tags:
            query_parts.append(
                ' '.join(f'-{tag}' for tag in filters.exclude_tags),
            )

        if filters.username:
            query_parts.append(f'@{filters.username}')

        if filters.types:
            types = '/'.join(filters.types)
            query_parts.append(f'type:{types}')

        if filters.like:
            query_parts.append(f'like:{filters.like}')

        if not query_parts:
            return None
        return ' '.join(query_parts)

    def _get_resp_data(self, resp: Response) -> JsonType:
        """Get the data from a response.

        Arguments:
            resp(Response): The web response to get the data from.

        Returns:
            JsonType: The data from the response or an error message.

        Raises:
            ClientRequestError: If the response is not Ok.
        """
        json_resp: dict[str, Any] = resp.json()

        resp_data = json_resp.get('data')
        if resp_data is not None:
            return resp_data

        if isinstance(resp_data, str):
            raise errors.ClientRequestError(resp, resp_data)

        # Ignore `Found implicit `.get()` dict usage` because I want to be
        # confident that 'error' field exists or not
        if 'error' in json_resp:
            raise errors.ClientRequestError(resp, json_resp['error'])  # noqa:WPS529

        return json_resp
