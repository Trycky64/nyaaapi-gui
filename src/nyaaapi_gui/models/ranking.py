from __future__ import annotations

from collections import Counter
from dataclasses import dataclass

from nyaaapi import Torrent

from .filters import FilterOptions
from .release_info import parse_release_title


@dataclass(frozen=True, slots=True)
class RankingPreferences:
    """Preference weights used to choose the most suitable release."""

    resolution: str = "1080p"
    language: str = "VOSTFR"
    exclude_multi: bool = True


def rank_releases(
    torrents: list[Torrent], preferences: RankingPreferences | None = None
) -> list[Torrent]:
    """Sort torrents best-first with deterministic preference and swarm tie-breakers."""
    preferences = preferences or RankingPreferences()
    groups = Counter(
        info.release_group.casefold()
        for torrent in torrents
        if (info := parse_release_title(torrent.title)).release_group
    )

    def score(torrent: Torrent) -> tuple[int, int, int, int, int, int, str]:
        info = parse_release_title(torrent.title)
        resolution = info.resolution == preferences.resolution
        language = info.language == preferences.language
        non_multi = not (info.language == "MULTi" or "multi" in torrent.title.casefold())
        group_score = groups[info.release_group.casefold()] if info.release_group else 0
        return (
            int(resolution),
            int(language),
            int(non_multi or not preferences.exclude_multi),
            torrent.seeders,
            torrent.downloads,
            group_score,
            torrent.title.casefold(),
        )

    return sorted(torrents, key=score, reverse=True)


def best_release(
    torrents: list[Torrent], preferences: RankingPreferences | None = None
) -> Torrent | None:
    """Return the top ranked torrent, or None when there are no candidates."""
    ranked = rank_releases(torrents, preferences)
    return ranked[0] if ranked else None


def preferences_from_filters(options: FilterOptions) -> RankingPreferences:
    """Build ranking preferences from the current UI filter controls."""
    return RankingPreferences(
        resolution=options.resolution if options.resolution != "Any" else "1080p",
        language=options.language if options.language != "Any" else "VOSTFR",
        exclude_multi=options.exclude_multi,
    )
