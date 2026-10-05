from __future__ import annotations

from unittest.mock import Mock

from test_widgets import torrent

from nyaaapi_gui.main_window import MainWindow


def test_local_filter_changes_visible_rows_without_network(qtbot) -> None:
    service = Mock()
    service.search.return_value = [torrent("A 1080p VOSTFR"), torrent("B 720p MULTi")]
    window = MainWindow(service)
    qtbot.addWidget(window)
    window.start_search({"query": "A"})
    qtbot.waitUntil(lambda: window._active_worker is None)
    calls = service.search.call_count
    window.search_panel.resolution_filter.setCurrentText("1080p")
    window.search_panel.exclude_multi.setChecked(True)
    assert window.results.rowCount() == 1
    assert window.status.count_label.text() == "1 results"
    assert service.search.call_count == calls
