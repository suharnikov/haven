from contextlib import suppress as do_not_raise
from typing import ContextManager

import pytest

from haven import errors
from haven.client import HavenClient
from haven.search_filters import CategoryFlags, PurityFlags, SearchParams, SortingValue, TopRange

TEST_USER = 'deterok'
TEST_COLLECTION = 1200574
TEST_HIDDEN_COLLECTION = 1247158


@pytest.mark.parametrize('username', [None, TEST_USER])
async def test_get_collections(client: HavenClient, username):
    collections = await client.get_collections(username)
    assert isinstance(collections, list)


@pytest.mark.parametrize('username,expectation', [
    (None, pytest.raises(errors.UserOrApikeyNotSetError)),
    (TEST_USER, do_not_raise()),
])
async def test_get_collections_without_apikey(
    client_without_apikey: HavenClient,
    username: str | None,
    expectation: ContextManager,
):
    with expectation:
        collections = await client_without_apikey.get_collections(username=username)
        assert isinstance(collections, list)


@pytest.mark.parametrize('collection_id', [TEST_COLLECTION, TEST_HIDDEN_COLLECTION])
async def test_get_wallpappers_list(client: HavenClient, collection_id: int):
    wallpappers = await client.get_wallpapper_list(TEST_USER, collection_id)
    assert wallpappers


@pytest.mark.parametrize(
    'collection_id,expectation', [
        (TEST_COLLECTION, do_not_raise()),
        (TEST_HIDDEN_COLLECTION, pytest.raises(errors.ClientRequestError, match='Nothing here')),
    ])
async def test_get_wallpappers_list_without_apikey(
    client_without_apikey: HavenClient,
    collection_id: int,
    expectation: ContextManager,
):
    with expectation:
        wallpappers = await client_without_apikey.get_wallpapper_list(TEST_USER, collection_id)
        assert wallpappers


async def test_find_wallpapers(client: HavenClient):
    filters = SearchParams(
        tags=['cars'],
        exclude_tags=['girl'],
        types=['png'],
        categories=CategoryFlags.GENERAL | CategoryFlags.PEOPLE,
        purity=PurityFlags.SFW,
        sorting=SortingValue.RANDOM,
        order='asc',
        top_range=TopRange.HALF_YEAR,
        atleast='800x600',
        resolutions=['800x600', '1024x768', '1280x1024', '1600x1200', '1920x1440'],
        ratios=['16:9', '4:3', '3:2', '1:1'],
        colors=['000000', '424153', '999999', 'cccccc', 'abbcda'],
    )
    wallpapers = await client.find_wallpapers(filters)
    assert wallpapers


@pytest.mark.parametrize('client_type,expectation', [
    ('client', do_not_raise()),
    ('client_without_apikey', pytest.raises(errors.ApikeyNotSetError)),
])
async def test_get_user_settings(
    client_type, expectation, client: HavenClient, client_without_apikey: HavenClient,
):
    # request.getfixturevalue doesn't work with asyncio
    if client_type == 'client':
        cl = client
    else:
        cl = client_without_apikey

    with expectation:
        settings = await cl.get_user_settings()
        assert settings
