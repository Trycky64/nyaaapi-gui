from __future__ import annotations

from unittest.mock import Mock

from test_widgets import torrent

from nyaaapi_gui.main_window import MainWindow
from nyaaapi_gui.widgets.results_table import ResultsTable


def test_results_empty_state_switches_to_and_from_table(qtbot) -> None:
    results = ResultsTable()
    qtbot.addWidget(results)
    results.set_empty_message("Search to begin")
    assert results.empty_label.text() == "Search to begin"
    results.set_torrents([torrent()])
    assert results.stack.currentWidget() is results.table
    results.set_torrents([])
    assert results.stack.currentWidget() is results.empty_label


def test_shortcut_handlers_and_context_menu(qtbot) -> None:
    window = MainWindow(Mock())
    qtbot.addWidget(window)
    window.show()
    window.focus_search()
    qtbot.waitUntil(window.query_input.hasFocus)
    assert window.create_results_context_menu().actions()[0].text() == "Copy selected magnets"
    window.search_panel.query_input.setText("query")
    window.clear_or_cancel()
    assert window.query_input.text() == ""
