from __future__ import annotations

from pathlib import Path
from unittest.mock import Mock

from nyaaapi import NyaaAPIHTTPError, TorrentDetails
from PySide6.QtCore import QSettings
from PySide6.QtWidgets import QDialog, QFileDialog
from test_widgets import torrent

from nyaaapi_gui.integrations.qbittorrent import QBittorrentConfig
from nyaaapi_gui.main_window import MainWindow
from nyaaapi_gui.models.season import build_season_plan
from nyaaapi_gui.models.settings import AppSettings, SettingsStore


def make_window(service: Mock | None = None) -> MainWindow:
    settings = QSettings("gui-tests", "main-window")
    settings.clear()
    store = SettingsStore(settings)
    window = MainWindow(service or Mock(), store)
    window.service.get_torrent.return_value = TorrentDetails(torrent("Show S01E01 1080p"))
    return window


def test_search_duplicate_and_refresh_paths(qtbot) -> None:
    service = Mock()
    service.search.return_value = []
    window = make_window(service)
    qtbot.addWidget(window)
    window.start_search({"query": "Show"})
    active = window._active_worker
    window.start_search({"query": "ignored"})
    assert window._active_worker is active
    qtbot.waitUntil(lambda: window._active_worker is None)
    window.refresh_search()
    qtbot.waitUntil(lambda: window._active_worker is None)
    assert service.clear_cache.call_count == 1
    assert service.search.call_count == 2


def test_refresh_without_prior_search_reports_hint(qtbot) -> None:
    window = make_window()
    qtbot.addWidget(window)
    window.refresh_search()
    assert window.status.state_label.text() == "Search before refreshing"


def test_season_empty_search_and_load_routes(qtbot) -> None:
    service = Mock()
    service.iter_search.return_value = [torrent("Show S02E01 1080p VOSTFR")]
    window = make_window(service)
    qtbot.addWidget(window)
    window.start_season_search({"anime": "  "})
    assert window.status.state_label.text() == "Enter an anime title"
    plan = window._load_season("Show", 2, None, "1080p", "VOSTFR", 1, 2)
    service.iter_search.assert_called_once_with("Show", max_pages=10)
    assert plan.episodes[0][0] == 1
    service.iter_user.return_value = [torrent("Show S02E02 1080p VOSTFR")]
    plan = window._load_season("Show", 2, "Fansub", "1080p", "VOSTFR", 1, 2)
    service.iter_user.assert_called_once_with("Fansub", "Show", max_pages=10)
    assert plan.episodes[0][0] == 2


def test_season_result_displays_episode_order(qtbot) -> None:
    window = make_window()
    qtbot.addWidget(window)
    plan = build_season_plan(
        [torrent("Show S02E02"), torrent("Show S02E01")], season=2, end_episode=2
    )
    window._search_succeeded(plan)
    assert window.results.visible_torrents()[0].title.endswith("E01")
    assert window.season_panel.summary.text().startswith("Season 2: 2 / 2")


def test_local_filter_empty_and_best_empty(qtbot) -> None:
    window = make_window()
    qtbot.addWidget(window)
    window._all_torrents = [torrent("Show 720p")]
    window.search_panel.resolution_filter.setCurrentText("1080p")
    assert window.status.state_label.text() == "No results match the local filters"
    window.select_best_release()
    assert window.results._recommended_title is None


def test_copy_paths_without_selection(qtbot) -> None:
    window = make_window()
    qtbot.addWidget(window)
    assert window.copy_selected_magnets() == 0
    assert window.copy_current_title() is False
    window.copy_selected_magnets_or_title()
    assert window.copy_visible_magnets() == 0


def test_save_export_dialog_cancel_and_file_write(qtbot, monkeypatch, tmp_path: Path) -> None:
    window = make_window()
    qtbot.addWidget(window)
    monkeypatch.setattr(QFileDialog, "getSaveFileName", lambda *_args: ("", ""))
    assert window.save_json() is False
    assert window.save_csv() is False
    assert window.save_magnets() is False
    target = tmp_path / "magnets.txt"
    monkeypatch.setattr(QFileDialog, "getSaveFileName", lambda *_args: (str(target), ""))
    assert window._save_text(str(target), "magnet:test")
    assert target.read_text(encoding="utf-8") == "magnet:test"
    assert "Exported to" in window.status.state_label.text()


def test_save_error_is_reported(qtbot, monkeypatch) -> None:
    window = make_window()
    qtbot.addWidget(window)
    monkeypatch.setattr("builtins.open", Mock(side_effect=OSError("disk full")))
    assert not window._save_text("C:/nope", "x")
    assert "Export failed" in window.status.state_label.text()


def test_settings_apply_and_cancel(qtbot, monkeypatch) -> None:
    store_settings = QSettings("gui-tests", "settings-apply")
    store_settings.clear()
    store = SettingsStore(store_settings)
    service = Mock()
    window = MainWindow(service, store)
    qtbot.addWidget(window)

    class CancelDialog:
        def __init__(self, *_args) -> None: ...
        def exec(self) -> int:
            return int(QDialog.DialogCode.Rejected)

    monkeypatch.setattr("nyaaapi_gui.main_window.SettingsDialog", CancelDialog)
    assert window.show_settings() is False

    class AcceptDialog:
        def __init__(self, *_args) -> None: ...
        def exec(self) -> int:
            return int(QDialog.DialogCode.Accepted)

        def values(self) -> AppSettings:
            return AppSettings(source="sukebei", favorite_uploader="Fansub")

    monkeypatch.setattr("nyaaapi_gui.main_window.SettingsDialog", AcceptDialog)
    assert window.show_settings() is True
    assert store.load().source == "sukebei"
    assert window.search_panel.source_combo.currentData() == "sukebei"


def test_qbittorrent_config_and_send_error_paths(qtbot, monkeypatch) -> None:
    window = make_window()
    qtbot.addWidget(window)
    window.send_selected_to_qbittorrent()
    assert window.status.state_label.text() == "Configure qBittorrent first"
    window._qbit_config = QBittorrentConfig()
    window.send_selected_to_qbittorrent()
    assert window.status.state_label.text() == "Select at least one result"
    window.results.set_torrents([torrent("Show")])
    window.results.table.selectRow(0)
    qtbot.waitUntil(lambda: window._detail_worker is None)
    assert window.qbit_send_action.isEnabled()

    class CancelQbitDialog:
        def __init__(self, *_args) -> None: ...
        def exec(self) -> int:
            return int(QDialog.DialogCode.Rejected)

    monkeypatch.setattr("nyaaapi_gui.main_window.QBittorrentConfigDialog", CancelQbitDialog)
    assert not window.configure_qbittorrent()

    class AcceptQbitDialog(CancelQbitDialog):
        def exec(self) -> int:
            return int(QDialog.DialogCode.Accepted)

        def config(self) -> QBittorrentConfig:
            return QBittorrentConfig(password="session-only")

    monkeypatch.setattr("nyaaapi_gui.main_window.QBittorrentConfigDialog", AcceptQbitDialog)
    assert window.configure_qbittorrent()
    assert window._qbit_config.password == "session-only"


def test_search_error_status_and_search_finished(qtbot) -> None:
    service = Mock()
    service.search.side_effect = NyaaAPIHTTPError("network failed")
    window = make_window(service)
    qtbot.addWidget(window)
    window.start_search({"query": "Show"})
    qtbot.waitUntil(lambda: window._active_worker is None)
    assert window.status.state_label.text() == "network failed"
    assert window.search_button.isEnabled()


def test_owned_service_closes_on_window_close(qtbot) -> None:
    window = MainWindow()
    qtbot.addWidget(window)
    window.show()
    window.close()
    assert window.service._api._client.is_closed
