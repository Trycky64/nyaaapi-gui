from __future__ import annotations

from dataclasses import dataclass

from nyaaapi import Torrent

from .ranking import RankingPreferences, rank_releases
from .release_info import parse_release_title


@dataclass(frozen=True, slots=True)
class SeasonPlan:
    """Best release selected per parsed episode in the requested range."""

    season: int
    start_episode: int
    end_episode: int
    episodes: tuple[tuple[int, Torrent], ...]

    @property
    def missing_episodes(self) -> tuple[int, ...]:
        """Episode numbers with no matching torrent in the current results."""
        found = {episode for episode, _torrent in self.episodes}
        return tuple(
            number
            for number in range(self.start_episode, self.end_episode + 1)
            if number not in found
        )

    @property
    def expected_count(self) -> int:
        return self.end_episode - self.start_episode + 1

    @property
    def torrents(self) -> tuple[Torrent, ...]:
        return tuple(torrent for _episode, torrent in self.episodes)


def build_season_plan(
    torrents: list[Torrent],
    *,
    season: int,
    start_episode: int = 1,
    end_episode: int = 24,
    preferences: RankingPreferences | None = None,
) -> SeasonPlan:
    """Group results by season and episode and keep the best release per episode."""
    if start_episode < 1 or end_episode < start_episode:
        raise ValueError("Episode range must satisfy 1 <= start <= end")
    grouped: dict[int, list[Torrent]] = {}
    for torrent in torrents:
        info = parse_release_title(torrent.title)
        if info.season != season or info.episode is None:
            continue
        if start_episode <= info.episode <= end_episode:
            grouped.setdefault(info.episode, []).append(torrent)
    selected = tuple(
        (episode, rank_releases(candidates, preferences)[0])
        for episode, candidates in sorted(grouped.items())
    )
    return SeasonPlan(season, start_episode, end_episode, selected)
