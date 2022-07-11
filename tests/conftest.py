import httpx
from pytest import fixture

from haven.client import HavenClient

TEST_APIKEY = 'BgPSBAOchpqbMBOXkxpIZvXMUDZ5hgfA'


@fixture
async def client():
    async with httpx.AsyncClient() as http_client:
        yield HavenClient(http_client, TEST_APIKEY)


@fixture
async def client_without_apikey():
    async with httpx.AsyncClient() as http_client:
        yield HavenClient(http_client)
