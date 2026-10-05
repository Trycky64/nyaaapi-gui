from __future__ import annotations

from unittest.mock import Mock

from test_widgets import torrent

from nyaaapi_gui.main_window import MainWindow


def test_best_release_button_highlights_recommendation(qtbot) -> None:
    service = Mock()
    service.search.return_value = [
        torrent("Show 720p MULTi", 100),
        torrent("Show 1080p VOSTFR", 10),
    ]
    service.get_torrent.return_value = torrent("Show 1080p VOSTFR", 10)
    window = MainWindow(service)
    qtbot.addWidget(window)
    window.start_search({"query": "show"})
    qtbot.waitUntil(lambda: window._active_worker is None)
    window.select_best_release()
    assert window.status.state_label.text().startswith("Best release:")
    recommended = next(
        window.results.torrent_at(row)
        for row in range(window.results.rowCount())
        if window.results.table.item(row, 0).font().bold()
    )
    assert recommended is not None and "1080p" in recommended.title
    assert window.results.selected_torrents() == [recommended]
