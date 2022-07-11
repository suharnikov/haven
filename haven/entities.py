from __future__ import annotations

from typing import Literal, TypedDict

PurityType = Literal['sfw', 'sketchy', 'nsfw']


class Collection(TypedDict):
    """Collection entity representation."""

    id: int
    label: str
    views: int
    public: int
    count: int


class Wallpapper(TypedDict):
    """Wallpaper data."""

    id: str
    url: str
    short_url: str
    views: int
    favorites: int
    source: str
    purity: PurityType
    category: str
    dimension_x: int
    dimension_y: int
    resolution: str
    ratio: str
    file_size: int
    file_type: str
    created_at: str
    colors: list[str]
    path: str
    thumbs: Thumbs


class Thumbs(TypedDict):
    """Thumbnails url of an wallpaper."""

    small: str
    original: str
    large: str


class UserSettings(TypedDict):
    """User settings."""

    thumb_size: str
    per_page: str
    purity: list[Literal['sfw', 'sketchy', 'nsfw']]
    categories: list[Literal['general', 'anime', 'people']]
    resolutions: list[str]
    aspect_ratios: list[str]
    toplist_range: str
    tag_blacklist: list[str]
    user_blacklist: list[str]
