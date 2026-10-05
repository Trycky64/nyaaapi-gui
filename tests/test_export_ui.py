from __future__ import annotations

from unittest.mock import Mock

from PySide6.QtWidgets import QApplication
from test_widgets import torrent

from nyaaapi_gui.main_window import MainWindow


def test_copy_selected_and_visible_magnets(qtbot) -> None:
    window = MainWindow(Mock())
    qtbot.addWidget(window)
    first, second = torrent("A"), torrent("B")
    window.results.set_torrents([first, second])
    row = next(
        row for row in range(window.results.rowCount()) if window.results.torrent_at(row) == first
    )
    window.results.table.selectRow(row)
    assert window.copy_selected_magnets() == 1
    assert QApplication.clipboard().text() == first.magnet
    assert window.copy_visible_magnets() == 2
    assert len(QApplication.clipboard().text().splitlines()) == 2
