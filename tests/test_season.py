from __future__ import annotations

import pytest
from test_widgets import torrent

from nyaaapi_gui.models.ranking import RankingPreferences
from nyaaapi_gui.models.season import build_season_plan


def test_season_plan_picks_best_release_and_reports_gaps() -> None:
    candidates = [
        torrent("Show S03E01 720p", 80),
        torrent("Show S03E01 1080p VOSTFR", 10),
        torrent("Show S03E03 1080p VOSTFR", 9),
        torrent("Show S02E02 1080p VOSTFR", 40),
        torrent("unparsed show", 30),
    ]
    plan = build_season_plan(
        candidates,
        season=3,
        start_episode=1,
        end_episode=4,
        preferences=RankingPreferences(),
    )
    assert [episode for episode, _ in plan.episodes] == [1, 3]
    assert "1080p" in plan.torrents[0].title
    assert plan.missing_episodes == (2, 4)
    assert plan.expected_count == 4


def test_season_plan_rejects_invalid_range() -> None:
    with pytest.raises(ValueError):
        build_season_plan([], season=1, start_episode=0, end_episode=2)
    with pytest.raises(ValueError):
        build_season_plan([], season=1, start_episode=4, end_episode=2)
