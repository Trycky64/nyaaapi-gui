from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class AnimeRelease:
    """Best-effort metadata parsed from an anime release title."""

    season: int | None = None
    episode: int | None = None
    resolution: str | None = None
    language: str | None = None
    release_group: str | None = None


_EPISODE_PATTERNS = (
    re.compile(r"\bS(?P<season>\d{1,2})\s*E(?P<episode>\d{1,3})\b", re.IGNORECASE),
    re.compile(r"\bSeason\s*(?P<season>\d{1,2})\b", re.IGNORECASE),
)
_EPISODE_WORD = re.compile(r"\bEpisode\s*(?P<episode>\d{1,3})\b", re.IGNORECASE)
_RESOLUTION = re.compile(r"\b(2160|1440|1080|720|480|360)p\b", re.IGNORECASE)
_LANGUAGES = ("VOSTFR", "SUBFRENCH", "FRENCH", "MULTi", "RAW")
_GROUP = re.compile(r"\[([^\]]{1,40})\]")


def parse_release_title(title: str) -> AnimeRelease:
    """Extract common season, episode, resolution and tag patterns safely."""
    season: int | None = None
    episode: int | None = None
    for pattern in _EPISODE_PATTERNS:
        match = pattern.search(title)
        if match:
            if match.groupdict().get("season"):
                season = int(match.group("season"))
            if match.groupdict().get("episode"):
                episode = int(match.group("episode"))
            if season is not None and episode is not None:
                break
    if episode is None:
        match = _EPISODE_WORD.search(title)
        if match:
            episode = int(match.group("episode"))
    resolution_match = _RESOLUTION.search(title)
    resolution = f"{resolution_match.group(1)}p" if resolution_match else None
    folded = title.casefold()
    language = next((tag for tag in _LANGUAGES if tag.casefold() in folded), None)
    group = next(
        (
            match.group(1).strip()
            for match in _GROUP.finditer(title)
            if not _RESOLUTION.fullmatch(match.group(1).strip())
            and match.group(1).strip().casefold() not in {tag.casefold() for tag in _LANGUAGES}
        ),
        None,
    )
    return AnimeRelease(season, episode, resolution, language, group)
