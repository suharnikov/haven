"""Cli interface for Haven."""

import asyncio

import click

from haven.downloader import HavenDownloader


@click.group()
def cli():
    """Haven Downloader."""


@cli.command()
@click.option(
    '-u',
    '--username',
    required=True,
    help='Username was displayed on the wallhaven.cc profile page.',
)
@click.option(
    '-c',
    '--collection',
    required=True,
    help='Collection name which will be downloaded',
)
@click.option('-o', '--output', required=True, help='Output directory')
@click.option('--apikey', help='wallhaven.cc API key')
def download(username: str, collection: str, output: str, apikey: str | None):
    """Download a image collection."""
    downloader = HavenDownloader(apikey)
    asyncio.run(
        downloader.download(
            username,
            collection,
            output,
        ),
    )
