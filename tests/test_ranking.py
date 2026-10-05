from __future__ import annotations

from dataclasses import replace

from test_widgets import torrent

from nyaaapi_gui.models.ranking import RankingPreferences, best_release, rank_releases


def test_best_release_prefers_quality_tags_then_seeders() -> None:
    poor = torrent("[GroupA] Anime 720p MULTi", 100)
    preferred_low = replace(poor, title="[GroupB] Anime 1080p VOSTFR", seeders=4)
    preferred_high = replace(preferred_low, seeders=30)
    ranked = rank_releases([poor, preferred_low, preferred_high])
    assert ranked[0] == preferred_high
    assert best_release([poor, preferred_low]) == preferred_low
    assert best_release([]) is None


def test_ranking_preferences_are_configurable_and_deterministic() -> None:
    english = torrent("[Studio] Anime 1080p SUBFRENCH", 8)
    multi = torrent("[Studio] Anime 1080p MULTi", 500)
    preferences = RankingPreferences(language="SUBFRENCH", resolution="1080p")
    assert best_release([multi, english], preferences) == english
