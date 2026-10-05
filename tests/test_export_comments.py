from __future__ import annotations

from datetime import UTC, datetime

from nyaaapi import Torrent, TorrentComment

from nyaaapi_gui.services.exports import export_json


def test_export_includes_comments_when_present() -> None:
    comment = TorrentComment(
        user="person",
        profile_url="https://example.org/user",
        avatar="",
        comment_body="Thanks",
        time=datetime(2025, 1, 1, tzinfo=UTC),
        link="https://example.org/comment",
    )
    candidate = Torrent(
        category="Anime",
        title="Title",
        link="https://nyaa.si/view/1",
        torrent="download",
        magnet="magnet:1",
        size="1 GiB",
        time=None,
        seeders=1,
        leechers=0,
        downloads=2,
        comments=(comment,),
    )
    import json

    record = json.loads(export_json([candidate]))[0]
    assert record["comments"][0]["comment_body"] == "Thanks"
