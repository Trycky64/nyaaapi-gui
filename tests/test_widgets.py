from __future__ import annotations

from datetime import UTC, datetime

from nyaaapi import Torrent
from PySide6.QtCore import Qt


def torrent(title: str = "Show S03E02 1080p VOSTFR", seeders: int = 5) -> Torrent:
    return Torrent(
        category="Anime - English-translated", title=title, link="https://nyaa.si/view/1",
        torrent="https://nyaa.si/download/1.torrent", magnet="magnet:?xt=urn:btih:abc",
        size="1.5 GiB", time=datetime(2025, 1, 1, tzinfo=UTC), seeders=seeders,
        leechers=2, downloads=10, uploader="Fansub",
    )


def test_search_panel_emits_and_resets(qtbot) -> None:
    from nyaaapi_gui.widgets.search_panel import SearchPanel

    panel = SearchPanel()
    qtbot.addWidget(panel)
    panel.query_input.setText(" Mushoku Tensei ")
    panel.uploader_input.setText("Tsundere-Raws")
    panel.source_combo.setCurrentIndex(1)
    with qtbot.waitSignal(panel.searchRequested) as captured:
        panel.search_button.click()
    assert captured.args[0]["query"] == "Mushoku Tensei"
    assert captured.args[0]["uploader"] == "Tsundere-Raws"
    assert captured.args[0]["source"] == "sukebei"
    with qtbot.waitSignal(panel.resetRequested):
        panel.reset_button.click()
    assert panel.values()["query"] is None
    assert panel.values()["page"] == 1


def test_search_panel_return_submits(qtbot) -> None:
    from nyaaapi_gui.widgets.search_panel import SearchPanel

    panel = SearchPanel()
    qtbot.addWidget(panel)
    with qtbot.waitSignal(panel.searchRequested):
        panel.query_input.returnPressed.emit()


def test_results_table_stores_selects_and_sorts(qtbot) -> None:
    from nyaaapi_gui.widgets.results_table import ResultsTable

    table = ResultsTable()
    qtbot.addWidget(table)
    low, high = torrent("A", 1), torrent("B", 20)
    table.set_torrents([low, high])
    low_row = next(row for row in range(table.rowCount()) if table.torrent_at(row) == low)
    table.table.selectRow(low_row)
    assert table.selected_torrents() == [low]
    assert table.copy_title() == "A"
    assert set(table.visible_torrents()) == {low, high}
    table.table.sortItems(3, Qt.SortOrder.AscendingOrder)
    assert table.visible_torrents()[0] == low
    table.table.clearSelection()
    assert table.copy_title() is None


def test_details_and_status_widgets(qtbot) -> None:
    from nyaaapi_gui.widgets.details_panel import DetailsPanel
    from nyaaapi_gui.widgets.status_bar import StatusWidget

    details = DetailsPanel()
    status = StatusWidget()
    qtbot.addWidget(details)
    qtbot.addWidget(status)
    details.show_torrent(torrent())
    assert details.heading.text().startswith("Show")
    assert "Seeders: 5" in details.text.toPlainText()
    details.show_torrent(None)
    assert not details.text.toPlainText()
    status.set_state("Connected")
    status.set_count(2)
    assert status.state_label.text() == "Connected"
    assert status.count_label.text() == "2 results"
