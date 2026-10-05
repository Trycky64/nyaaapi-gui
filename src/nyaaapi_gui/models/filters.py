from __future__ import annotations

import re
from dataclasses import dataclass

from nyaaapi import Torrent


@dataclass(frozen=True, slots=True)
class FilterOptions:
    """Client-side release filters applied without another network request."""

    resolution: str = "Any"
    language: str = "Any"
    codec: str = "Any"
    audio: str = "Any"
    exclude_multi: bool = False
    minimum_seeders: int = 0


def filter_torrents(torrents: list[Torrent], options: FilterOptions) -> list[Torrent]:
    """Return torrents that satisfy every selected local filter."""
    filtered: list[Torrent] = []
    for torrent in torrents:
        title = torrent.title.casefold()
        if options.resolution != "Any" and not _has_token(title, options.resolution):
            continue
        if options.language != "Any" and not _has_token(title, options.language):
            continue
        if options.codec != "Any" and not _has_alias(title, _CODECS[options.codec]):
            continue
        if options.audio != "Any" and not _has_token(title, options.audio):
            continue
        if options.exclude_multi and _has_token(title, "multi"):
            continue
        if torrent.seeders < options.minimum_seeders:
            continue
        filtered.append(torrent)
    return filtered


def _has_token(title: str, token: str) -> bool:
    return re.search(rf"(?<![a-z0-9]){re.escape(token.casefold())}(?![a-z0-9])", title) is not None


_CODECS: dict[str, tuple[str, ...]] = {
    "H.264 / x264": ("h.264", "h264", "x264", "avc"),
    "H.265 / HEVC / x265": ("h.265", "h265", "hevc", "x265"),
    "AV1": ("av1",),
}


def _has_alias(title: str, aliases: tuple[str, ...]) -> bool:
    return any(_has_token(title, alias) for alias in aliases)
