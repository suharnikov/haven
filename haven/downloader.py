"""Set of file downloader functions and classes."""

import asyncio
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Final, cast

import httpx
from rich.progress import Progress
from rich.progress import TaskID as ProgressTaskID

from haven.client import HavenClient

#: Base reqest timeout before downloader will raise an exception.
REQUEST_TIMEOUT: Final[int] = 10


@dataclass
class FileData():
    """File information."""

    name: str
    size: int
    url: str


class HavenDownloader():
    """HavenDownloader provides a set of functions for downloading files from wallhvaen."""

    def __init__(self, apikey: str | None = None, parallel_requests: int = 4):
        """Initialize HavenDownloader.

        Arguments:
            apikey (str): wallhaven API key.
            parallel_requests (int): maximum number of parallel requests.
        """
        self.apikey = apikey

        self._sem = asyncio.Semaphore(parallel_requests)

    async def download(
        self,
        user_name: str,
        collection_name: str,
        dest_dir: str | Path,
    ):
        """Download all images from a collection.

        It does not return anything, just downloads the files and prints progress.

        Arguments:
            user_name (str): wallhaven user name.
            collection_name (str): collection name.
            dest_dir (str | Path): destination directory.
        """
        if isinstance(dest_dir, str):
            dest_dir = Path(dest_dir)

        async with httpx.AsyncClient() as http_client:
            file_data_list = await self._get_image_data(http_client, user_name, collection_name)

            with Progress() as progress:
                total_progress = progress.add_task(
                    description='Total',
                    total=sum(fdata.size for fdata in file_data_list),
                )
                tasks = [
                    self._download_file(http_client, file_data, dest_dir, progress, total_progress)
                    for file_data in file_data_list
                ]
                await asyncio.gather(*tasks)

    async def _download_file(  # noqa: WPS211 Found too many arguments
        self,
        http_client: httpx.AsyncClient,
        file_data: FileData,
        dest_dir: Path,
        progress: Progress,
        total_progress: ProgressTaskID,
    ):
        """Download a single file.

        Arguments:
            http_client (AsyncClient): HTTP client.
            file_data (FileData): file information.
            dest_dir (Path): destination directory.
            progress (Progress): progress bars view.
            total_progress (ProgressTaskID): total progress bar.
        """
        await self._sem.acquire()

        task_progress = progress.add_task(file_data.name, total=file_data.size)
        filepath = dest_dir / file_data.name

        async with http_client.stream('GET', file_data.url, timeout=REQUEST_TIMEOUT) as resp:
            with open(filepath.expanduser(), 'wb') as image_file:

                async for image_data in resp.aiter_bytes():
                    image_file.write(image_data)
                    progress.advance(task_progress, len(image_data))
                    progress.advance(total_progress, len(image_data))

        progress.update(task_progress, description=f':white_check_mark: {file_data.name}')
        # to show check mark on screen before task is removed
        await asyncio.sleep(0.5)
        progress.update(task_progress, visible=False)

        self._sem.release()

    async def _get_image_data(
        self,
        http_client: httpx.AsyncClient,
        user_name: str,
        collection_name: str,
    ) -> list[FileData]:
        """Get image data list from a wallhaven collection.

        Arguments:
            http_client (AsyncClient): HTTP client.
            user_name (str): wallhaven user name.
            collection_name (str): collection name.

        Returns:
            list[FileData]: list of image data.

        Raises:
            RuntimeError: if collection is not found.
        """
        client = HavenClient(http_client, self.apikey)

        collections = cast(
            list[dict[str, Any]],
            await client.get_collections(user_name),
        )
        collection_id = next(
            (
                collection['id']
                for collection in collections
                if collection['label'] == collection_name
            ),
            None,
        )
        if not collection_id:
            raise RuntimeError(f'Collection "{collection_name}" not found')

        collection = await client.get_collection(user_name, collection_id)
        return [
            FileData(
                name=cast(str, image['path']).rsplit('/', 1)[-1],
                url=cast(str, image['path']),
                size=cast(int, image['file_size']),
            )
            for image in collection
        ]


def _make_chanks(sequence: list, size: int) -> list:
    return [
        sequence[left_value:left_value + size]
        for left_value in range(0, len(sequence), size)
    ]
