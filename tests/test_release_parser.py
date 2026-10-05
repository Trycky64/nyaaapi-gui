from nyaaapi_gui.models.release_info import AnimeRelease, parse_release_title


def test_parse_compact_season_episode_and_release_tags() -> None:
    parsed = parse_release_title("[Tsundere-Raws] Mushoku Tensei S03E14 1080p VOSTFR")
    assert parsed == AnimeRelease(3, 14, "1080p", "VOSTFR", "Tsundere-Raws")
    assert parse_release_title("Title S3E4 720p").season == 3
    assert parse_release_title("Title S3E4 720p").episode == 4


def test_parse_season_and_episode_words_and_unknown_title() -> None:
    parsed = parse_release_title("A show Season 3 Episode 14 2160p SUBFRENCH")
    assert parsed.season == 3
    assert parsed.episode == 14
    assert parsed.resolution == "2160p"
    assert parsed.language == "SUBFRENCH"
    assert parse_release_title("unrecognized title") == AnimeRelease()


def test_parser_ignores_bracketed_resolution_as_release_group() -> None:
    assert parse_release_title("Show [1080p]").release_group is None
