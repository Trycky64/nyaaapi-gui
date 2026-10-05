from __future__ import annotations

from datetime import UTC, datetime
from unittest.mock import Mock

from nyaaapi import Torrent

from nyaaapi_gui.main_window import MainWindow


def torrent(title: str) -> Torrent:
    return Torrent(
        category="Anime",
        title=title,
        link="https://nyaa.si/view/1",
        torrent="https://nyaa.si/download/1.torrent",
        magnet="magnet:?xt=urn:btih:abc",
        size="1 GiB",
        time=datetime(2025, 1, 1, tzinfo=UTC),
        seeders=10,
        leechers=2,
        downloads=5,
        uploader="Uploader",
    )


def test_main_window_search_runs_in_background_and_renders(qtbot) -> None:
    service = Mock()
    service.search.return_value = [torrent("First"), torrent("Second")]
    window = MainWindow(service)
    qtbot.addWidget(window)
    window.show()
    window.start_search({"query": "anime", "source": "nyaa", "page": 1})
    assert not window.search_button.isEnabled()
    qtbot.waitUntil(lambda: window._active_worker is None)
    assert window.results.rowCount() == 2
    assert window.status.count_label.text() == "2 results"
    assert window.search_button.isEnabled()
    assert window.status.state_label.text() == "Search complete"
    assert service.search.call_args.kwargs["query"] == "anime"


def test_main_window_reports_request_error_and_resets(qtbot) -> None:
    service = Mock()
    service.search.side_effect = TimeoutError("request timed out")
    window = MainWindow(service)
    qtbot.addWidget(window)
    window.start_search({"query": "anime"})
    qtbot.waitUntil(lambda: window._active_worker is None)
    assert window.search_button.isEnabled()
    assert window.status.state_label.text() == "request timed out"
    window.results.set_torrents([torrent("Sample")])
    window.reset_results()
    assert window.results.rowCount() == 0
    assert window.status.count_label.text() == "0 results"
