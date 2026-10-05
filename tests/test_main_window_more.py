from __future__ import annotations

from unittest.mock import Mock

from nyaaapi import TorrentDetails
from test_widgets import torrent

from nyaaapi_gui.main_window import MainWindow
from nyaaapi_gui.models.settings import AppSettings


def test_detail_selection_guard_and_api_error(qtbot) -> None:
    service = Mock()
    service.get_torrent.side_effect = RuntimeError("not found")
    window = MainWindow(service)
    qtbot.addWidget(window)
    window._current_source = "nyaa"
    selected = torrent("Show")
    window._on_torrent_selected(selected)
    first = window._detail_worker
    window._on_torrent_selected(selected)
    assert window._detail_worker is first
    qtbot.waitUntil(lambda: window._detail_worker is None)
    assert window.status.state_label.text() == "not found"
    window._on_torrent_selected(None)
    assert window.details.heading.text() == "Select a result to see its details"


def test_settings_apply_no_panel_guard(qtbot) -> None:
    window = MainWindow(Mock())
    qtbot.addWidget(window)
    del window.search_panel
    window._apply_settings_to_controls(AppSettings())


def test_copy_title_after_selection(qtbot) -> None:
    from PySide6.QtWidgets import QApplication

    service = Mock()
    service.get_torrent.return_value = TorrentDetails(torrent("Copy me"))
    window = MainWindow(service)
    qtbot.addWidget(window)
    window.results.set_torrents([torrent("Copy me")])
    window.results.table.selectRow(0)
    assert window.copy_current_title()
    assert QApplication.clipboard().text() == "Copy me"
