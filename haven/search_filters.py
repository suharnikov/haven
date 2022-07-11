import enum
from dataclasses import dataclass
from typing import Literal


@enum.unique
class CategoryFlags(enum.IntFlag):
    """Category flags for the wallhaven.cc API."""

    PEOPLE = enum.auto()
    ANIME = enum.auto()
    GENERAL = enum.auto()


@enum.unique
class PurityFlags(enum.IntFlag):
    """Purity flags for the wallhaven.cc API."""

    NSFW = enum.auto()
    SKETCHY = enum.auto()
    SFW = enum.auto()


@enum.unique
class TopRange(str, enum.Enum):  # noqa: WPS600: Found subclassing a builtin
    ONE_DAY = '1d'
    THREE_DAYS = '3d'
    ONE_WEEK = '1w'
    ONE_MONTH = '1M'
    THREE_MONTHS = '3M'
    HALF_YEAR = '6M'
    ONE_YEAR = '1y'


@enum.unique
class SortingValue(str, enum.Enum):  # noqa: WPS600: Found subclassing a builtin
    DATA_ADDED = 'date_added'
    RELEVANCE = 'relevance'
    RANDOM = 'random'
    VIEWS = 'views'
    FAVORITES = 'favorites'
    TOPLIST = 'toplist'


@dataclass
class SearchParams:
    """Image search parameters."""

    tags: list[str] | None = None
    """Search fuzzily for a tag/keyword."""

    exclude_tags: list[str] | None = None
    """Exclude a tag/keyword."""

    username: str | None = None
    """User uploads."""

    types: list[str] | None = None
    """Search for file type (jpg = jpeg)."""

    like: int | None = None
    """Find wallpapers with similar tags."""

    categories: CategoryFlags | None = None
    """Turn categories on or off.

    Defaults to all categories.
    """

    purity: PurityFlags | None = None
    """Turn purity on or off.

    NSFW requires a valid API key. Defaults to `PurityFlags.SFW`.
    """

    sorting: SortingValue | None = None
    """Method of sorting results.

    Defaults to date_added.
    """

    order: Literal['desc', 'asc'] | None = None
    """Sorting order."""

    top_range: TopRange | None = None
    """Sorting MUST be set to 'toplist'

    Defaults to 1M.
    """

    atleast: str | None = None
    """Minimum resolution allowed.

    Example: '1920x1080'
    """

    resolutions: list[str] | None = None
    """List of exact wallpaper resolutions."""

    ratios: list[str] | None = None
    """List of aspect ratios."""

    colors: list[str] | None = None
    """Search by colors.

    Example: ['ff0000', 'a1ff00', '0000ff']
    """
