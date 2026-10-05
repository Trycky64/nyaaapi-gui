from __future__ import annotations

from unittest.mock import Mock

from test_widgets import torrent

from nyaaapi_gui.main_window import MainWindow


def test_season_search_uses_uploader_and_displays_found_and_missing(qtbot) -> None:
    service = Mock()
    service.iter_user.return_value = [
        torrent("Show S03E01 1080p VOSTFR"),
        torrent("Show S03E03 1080p VOSTFR"),
    ]
    window = MainWindow(service)
    qtbot.addWidget(window)
    window.season_panel.anime_input.setText("Show")
    window.season_panel.uploader_input.setText("Fansub")
    window.season_panel.season_input.setValue(3)
    window.start_season_search(window.season_panel.values())
    qtbot.waitUntil(lambda: window._active_worker is None)
    assert service.iter_user.call_args.args[:2] == ("Fansub", "Show")
    assert window.season_panel.summary.text() == "Season 3: 2 / 24 episodes found so far"
    assert "S03E02" in window.season_panel.missing_label.text()
    assert window.results.rowCount() == 2
