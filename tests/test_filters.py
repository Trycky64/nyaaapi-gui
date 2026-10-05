from __future__ import annotations

from dataclasses import replace

from test_widgets import torrent

from nyaaapi_gui.models.filters import FilterOptions, filter_torrents


def test_resolution_language_codec_and_audio_filters() -> None:
    candidate = torrent("Anime 1080p VOSTFR x265 FLAC")
    for options in (
        FilterOptions(resolution="1080p"),
        FilterOptions(language="VOSTFR"),
        FilterOptions(codec="H.265 / HEVC / x265"),
        FilterOptions(audio="FLAC"),
    ):
        assert filter_torrents([candidate], options) == [candidate]
    assert filter_torrents([candidate], FilterOptions(resolution="720p")) == []


def test_multi_and_minimum_seeders_filters() -> None:
    multi = torrent("Anime 1080p MULTi", 5)
    french = replace(multi, title="Anime 1080p VOSTFR", seeders=12)
    assert filter_torrents([multi, french], FilterOptions(exclude_multi=True)) == [french]
    assert filter_torrents([multi, french], FilterOptions(minimum_seeders=10)) == [french]
    assert filter_torrents([multi, french], FilterOptions(language="MULTi")) == [multi]
