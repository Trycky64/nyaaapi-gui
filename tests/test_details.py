from __future__ import annotations

from dataclasses import replace
from unittest.mock import Mock

from test_widgets import torrent

from nyaaapi_gui.main_window import MainWindow
from nyaaapi_gui.widgets.details_panel import DetailsPanel


def test_full_detail_panel_shows_api_fields(qtbot) -> None:
    from nyaaapi import TorrentDetails

    full = replace(torrent(), information="https://example.org", infohash="deadbeef")
    panel = DetailsPanel()
    qtbot.addWidget(panel)
    panel.show_full_details(TorrentDetails(full))
    text = panel.text.toPlainText()
    assert "Info hash: deadbeef" in text
    assert "Information: https://example.org" in text
    assert "Magnet: magnet:" in text


def test_details_are_fetched_only_after_selecting_a_result(qtbot) -> None:
    service = Mock()
    from nyaaapi import TorrentDetails

    service.search.return_value = [torrent("Show S01E01 1080p")]
    service.get_torrent.return_value = TorrentDetails(torrent("Show S01E01 1080p"))
    window = MainWindow(service)
    qtbot.addWidget(window)
    window.start_search({"query": "Show", "source": "sukebei"})
    qtbot.waitUntil(lambda: window._active_worker is None)
    service.get_torrent.assert_not_called()
    window.results.table.selectRow(0)
    qtbot.waitUntil(lambda: window._detail_worker is None)
    service.get_torrent.assert_called_once_with(torrent_id=1, source="sukebei")


def test_unparseable_link_does_not_request_details(qtbot) -> None:
    service = Mock()
    window = MainWindow(service)
    qtbot.addWidget(window)
    window._on_torrent_selected(replace(torrent(), link="https://example.org/item"))
    service.get_torrent.assert_not_called()
    assert "not available" in window.status.state_label.text()
