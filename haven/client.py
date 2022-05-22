"""Core python interface for the wallhaven.cc (https://wallhaven.cc) API."""
from __future__ import annotations

from typing import Union, cast

from httpx import AsyncClient, QueryParams, Response
from yarl import URL

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
            http_client (AsyncClient): An AsyncClient instance.
            apikey (str): Your wallhaven.cc API key.
            apihost (str): The wallhaven.cc API host. Default to 'https://wallhaven.cc'.
        """
        self.apiurl = URL(apihost) / 'api/v1'

        self._client = http_client
        if apikey:
            self._client.params = QueryParams(**http_client.params, apikey=apikey)

    async def get_collections(self, username: str | None = None) -> JsonObjListType:
        """Get a list of collections.

        Arguments:
            username (str): The username of the user. Defaults to None.

            If not specified, the current user collections (by apikey) will be returned.

        Returns:
            JsonObjListType: A list of collections.

        Raises:
            RuntimeError: If the user is not found or something else went wrong.
        """
        url = self.apiurl / 'collections'
        if username:
            url /= username

        resp = await self._client.get(str(url))
        resp_data = self._get_resp_data(resp)

        if isinstance(resp_data, str):
            raise RuntimeError(resp_data)

        return cast(JsonObjListType, resp_data)

    async def get_collection(self, username: str, id_: int) -> JsonObjListType:
        """Get an image collection.

        Arguments:
            username (str): The username of the user.
            id_ (int): The id of the collection.

        Returns:
            JsonObjListType: The image collection data.

        Raises:
            RuntimeError: If the collection is not found or the user is not found
                or something else went wrong :).
        """
        url = self.apiurl / 'collections' / username / str(id_)

        resp = await self._client.get(str(url))
        resp_data = self._get_resp_data(resp)

        if isinstance(resp_data, str):
            raise RuntimeError(resp_data)

        return cast(JsonObjListType, resp_data)

    def _get_resp_data(self, resp: Response) -> JsonType | str:
        """Get the data from a response.

        Arguments:
            resp (Response): The web response to get the data from.

        Returns:
            JsonType | str: The data from the response or an error message.
        """
        json_resp = resp.json()

        resp_data = json_resp.get('data')
        if resp_data is not None:
            return resp_data

        resp_error = json_resp.get('error')
        if resp_error is not None:
            return resp_error

        return json_resp
