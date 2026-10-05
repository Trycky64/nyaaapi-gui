from __future__ import annotations

import csv
import io
import json
from datetime import datetime
from typing import Any

from nyaaapi import Torrent


def torrent_record(torrent: Torrent) -> dict[str, Any]:
    """Convert a backend model into a JSON-ready record."""
    record: dict[str, Any] = {
        "category": torrent.category,
        "title": torrent.title,
        "link": torrent.link,
        "torrent": torrent.torrent,
        "magnet": torrent.magnet,
        "size": torrent.size,
        "time": _iso(torrent.time),
        "seeders": torrent.seeders,
        "leechers": torrent.leechers,
        "downloads": torrent.downloads,
        "uploader": torrent.uploader,
        "information": torrent.information,
        "infohash": torrent.infohash,
    }
    if torrent.comments is not None:
        record["comments"] = [
            {
                "user": comment.user,
                "profile_url": comment.profile_url,
                "avatar": comment.avatar,
                "comment_body": comment.comment_body,
                "time": _iso(comment.time),
                "link": comment.link,
            }
            for comment in torrent.comments
        ]
    return record


def export_json(torrents: list[Torrent]) -> str:
    """Serialize selected torrents as formatted JSON."""
    return json.dumps(
        [torrent_record(torrent) for torrent in torrents], ensure_ascii=False, indent=2
    )


def export_csv(torrents: list[Torrent]) -> str:
    """Serialize selected torrents as a UTF-8-compatible CSV string."""
    records = [torrent_record(torrent) for torrent in torrents]
    fields = [
        "title",
        "category",
        "size",
        "seeders",
        "leechers",
        "downloads",
        "time",
        "uploader",
        "magnet",
        "torrent",
        "link",
        "infohash",
        "information",
    ]
    output = io.StringIO(newline="")
    writer = csv.DictWriter(output, fieldnames=fields, extrasaction="ignore")
    writer.writeheader()
    writer.writerows(records)
    return output.getvalue()


def export_magnets(torrents: list[Torrent]) -> str:
    """Return one magnet URI per line, preserving input order."""
    return "\n".join(torrent.magnet for torrent in torrents)


def _iso(value: datetime | None) -> str | None:
    return value.isoformat() if value is not None else None
