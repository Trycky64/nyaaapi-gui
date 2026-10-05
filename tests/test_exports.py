from __future__ import annotations

import csv
import json
from io import StringIO

from test_widgets import torrent

from nyaaapi_gui.services.exports import export_csv, export_json, export_magnets


def test_export_json_includes_full_torrent_fields() -> None:
    candidate = torrent("Anime")
    data = json.loads(export_json([candidate]))
    assert data[0]["title"] == "Anime"
    assert data[0]["seeders"] == 5
    assert data[0]["magnet"] == candidate.magnet
    assert data[0]["time"].startswith("2025-")


def test_export_csv_and_magnets_preserve_order() -> None:
    first, second = torrent("First"), torrent("Second")
    magnets = export_magnets([first, second]).splitlines()
    assert magnets == [first.magnet, second.magnet]
    parsed = list(csv.DictReader(StringIO(export_csv([first, second]))))
    assert [row["title"] for row in parsed] == ["First", "Second"]
    assert parsed[0]["seeders"] == "5"
