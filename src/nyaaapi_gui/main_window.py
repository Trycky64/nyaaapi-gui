from __future__ import annotations

import re
from collections.abc import Sequence

from nyaaapi import SearchResults, Torrent
from PySide6.QtCore import QPoint, Qt, QThreadPool
from PySide6.QtGui import QCloseEvent, QKeySequence, QShortcut
from PySide6.QtWidgets import (
    QApplication,
    QFileDialog,
    QMainWindow,
    QMenu,
    QPushButton,
    QSplitter,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from .integrations.qbittorrent import QBittorrentConfig, QBittorrentService
from .models.filters import filter_torrents
from .models.ranking import RankingPreferences, best_release, preferences_from_filters
from .models.season import SeasonPlan, build_season_plan
from .models.settings import AppSettings, SettingsStore
from .services.exports import export_csv, export_json, export_magnets
from .services.nyaa_service import NyaaService
from .widgets.details_panel import DetailsPanel
from .widgets.qbittorrent_dialog import QBittorrentConfigDialog
from .widgets.results_table import ResultsTable
from .widgets.search_panel import SearchPanel
from .widgets.season_panel import SeasonPanel
from .widgets.settings_dialog import SettingsDialog
from .widgets.status_bar import StatusWidget
from .workers.search_worker import SearchWorker


class MainWindow(QMainWindow):
    """Main application window and coordinator for search widgets."""

    def __init__(
        self, service: NyaaService | None = None, settings: SettingsStore | None = None
    ) -> None:
        super().__init__()
        self.settings_store = settings or SettingsStore()
        self.app_settings = self.settings_store.load()
        self.service = service or NyaaService(timeout=self.app_settings.api_timeout)
        self._owns_service = service is None
        self._active_worker: SearchWorker | None = None
        self._detail_worker: SearchWorker | None = None
        self._current_source = self.app_settings.source
        self._last_search_values: dict[str, object] | None = None
        self.thread_pool = QThreadPool.globalInstance()
        self._all_torrents: list[Torrent] = []
        self._qbit_config: QBittorrentConfig | None = None
        self.setWindowTitle("NyaaAPI GUI")
        from importlib.resources import files

        from PySide6.QtGui import QIcon

        self.setWindowIcon(QIcon(str(files("nyaaapi_gui").joinpath("resources/icon.svg"))))
        self.setMinimumSize(1024, 680)
        self.search_panel = SearchPanel()
        self._apply_settings_to_controls(self.app_settings)
        self.season_panel = SeasonPanel()
        self.search_tabs = QTabWidget()
        self.search_tabs.addTab(self.search_panel, "Search")
        self.search_tabs.addTab(self.season_panel, "Season mode")
        self.query_input = self.search_panel.query_input
        self.search_button = self.search_panel.search_button
        self.best_release_button = QPushButton("Best Release")
        self.search_panel.form_layout.addRow(self.best_release_button)
        self.results = ResultsTable()
        self.details = DetailsPanel()
        splitter = QSplitter()
        splitter.setOrientation(Qt.Orientation.Vertical)
        splitter.addWidget(self.results)
        splitter.addWidget(self.details)
        splitter.setSizes([440, 180])
        layout = QVBoxLayout()
        layout.addWidget(self.search_tabs)
        layout.addWidget(splitter, 1)
        central = QWidget()
        central.setLayout(layout)
        self.setCentralWidget(central)
        self.status = StatusWidget(self)
        self.setStatusBar(self.status)
        toolbar = self.addToolBar("Export")
        toolbar.setMovable(False)
        self.copy_selected_action = toolbar.addAction("Copy selected magnets")
        self.copy_visible_action = toolbar.addAction("Copy all visible magnets")
        self.export_magnets_action = toolbar.addAction("Export magnets TXT")
        self.export_json_action = toolbar.addAction("Export selected JSON")
        self.export_csv_action = toolbar.addAction("Export selected CSV")
        self.settings_action = toolbar.addAction("Settings")
        self.settings_action.triggered.connect(self.show_settings)
        self.refresh_action = toolbar.addAction("Refresh")
        self.refresh_action.triggered.connect(self.refresh_search)
        self.qbit_config_action = toolbar.addAction("Configure qBittorrent")
        self.qbit_send_action = toolbar.addAction("Send selected to qBittorrent")
        self.qbit_send_action.setEnabled(False)
        self.copy_selected_action.triggered.connect(self.copy_selected_magnets)
        self.copy_visible_action.triggered.connect(self.copy_visible_magnets)
        self.export_magnets_action.triggered.connect(self.save_magnets)
        self.export_json_action.triggered.connect(self.save_json)
        self.export_csv_action.triggered.connect(self.save_csv)
        self.qbit_config_action.triggered.connect(self.configure_qbittorrent)
        self.qbit_send_action.triggered.connect(self.send_selected_to_qbittorrent)
        self.results.table.itemSelectionChanged.connect(
            lambda: self.qbit_send_action.setEnabled(
                bool(self.results.selected_torrents()) and self._qbit_config is not None
            )
        )
        self.results.torrentSelected.connect(self._on_torrent_selected)
        self.results.table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.results.table.customContextMenuRequested.connect(self.show_results_context_menu)
        self._install_shortcuts()
        self.search_panel.searchRequested.connect(self.start_search)
        self.season_panel.searchRequested.connect(self.start_season_search)
        self.search_panel.resetRequested.connect(self.reset_results)
        self.search_panel.filtersChanged.connect(self.apply_local_filters)
        self.best_release_button.clicked.connect(self.select_best_release)

    def _on_torrent_selected(self, torrent: Torrent | None) -> None:
        self.details.show_torrent(torrent)
        if torrent is None:
            return
        match = re.search(r"/view/(\d+)(?:$|[/?#])", torrent.link)
        if match is None:
            self.status.set_state("Full details are not available for this result")
            return
        if self._detail_worker is not None:
            return
        worker = SearchWorker(
            self.service.get_torrent,
            torrent_id=int(match.group(1)),
            source=self._current_source,
        )
        self._detail_worker = worker
        worker.signals.result.connect(self.details.show_full_details)
        worker.signals.error.connect(lambda error: self.status.set_state(str(error)))
        worker.signals.started.connect(lambda: self.status.set_state("Loading torrent details..."))
        worker.signals.finished.connect(self._detail_finished)
        self.thread_pool.start(worker)

    def _detail_finished(self) -> None:
        self._detail_worker = None

    def start_search(self, values: dict[str, object] | None = None) -> None:
        """Run the current search in the global Qt thread pool."""
        if self._active_worker is not None:
            return
        options = values or self.search_panel.values()
        self._last_search_values = dict(options)
        self._current_source = str(options.get("source", "nyaa"))
        kwargs = {
            "query": options.get("query"),
            "source": options.get("source", "nyaa"),
            "category": options.get("category"),
            "sub_category": options.get("sub_category"),
            "sort": options.get("sort"),
            "order": options.get("order"),
            "page": options.get("page", 1),
        }
        uploader = str(options.get("uploader") or "").strip()
        if uploader:
            worker = SearchWorker(
                self.service.search_user,
                user_name=uploader,
                query=kwargs["query"],
                source=kwargs["source"],
                category=kwargs["category"],
                sub_category=kwargs["sub_category"],
                sort=kwargs["sort"],
                order=kwargs["order"],
                page=kwargs["page"],
            )
        else:
            worker = SearchWorker(self.service.search, **kwargs)
        self._active_worker = worker
        worker.signals.started.connect(self._search_started)
        worker.signals.result.connect(self._search_succeeded)
        worker.signals.error.connect(self._search_failed)
        worker.signals.finished.connect(self._search_finished)
        self.search_button.setEnabled(False)
        self.status.set_state("Searching...")
        self.thread_pool.start(worker)

    def start_season_search(self, values: dict[str, object]) -> None:
        """Search multiple pages for one season without blocking the UI."""
        if self._active_worker is not None:
            return
        if not str(values.get("anime", "")).strip():
            self.status.set_state("Enter an anime title")
            return
        kwargs = dict(values)
        worker = SearchWorker(self._load_season, **kwargs)
        self._active_worker = worker
        worker.signals.started.connect(self._search_started)
        worker.signals.result.connect(self._search_succeeded)
        worker.signals.error.connect(self._search_failed)
        worker.signals.finished.connect(self._search_finished)
        self.search_button.setEnabled(False)
        self.season_panel.search_button.setEnabled(False)
        self.status.set_state("Searching season...")
        self.thread_pool.start(worker)

    def _load_season(
        self,
        anime: str,
        season: int,
        uploader: str | None,
        resolution: str,
        language: str,
        start_episode: int,
        end_episode: int,
    ) -> SeasonPlan:
        preferences = RankingPreferences(resolution=resolution, language=language)
        if uploader:
            torrents = list(
                self.service.iter_user(uploader, anime, max_pages=self.app_settings.max_pages)
            )
        else:
            torrents = list(self.service.iter_search(anime, max_pages=self.app_settings.max_pages))
        return build_season_plan(
            torrents,
            season=season,
            start_episode=start_episode,
            end_episode=end_episode,
            preferences=preferences,
        )

    def _install_shortcuts(self) -> None:
        search_shortcut = QShortcut(QKeySequence("Ctrl+F"), self)
        search_shortcut.activated.connect(self.focus_search)
        copy_shortcut = QShortcut(QKeySequence.StandardKey.Copy, self)
        copy_shortcut.activated.connect(self.copy_selected_magnets_or_title)
        escape_shortcut = QShortcut(QKeySequence("Escape"), self)
        escape_shortcut.activated.connect(self.clear_or_cancel)

    def focus_search(self) -> None:
        """Focus the query field and select its existing text."""
        self.search_tabs.setCurrentWidget(self.search_panel)
        self.query_input.setFocus()
        self.query_input.selectAll()

    def copy_selected_magnets_or_title(self) -> None:
        """Copy selected magnets, falling back to the current selected title."""
        if self.results.selected_torrents():
            self.copy_selected_magnets()
        else:
            self.copy_current_title()

    def clear_or_cancel(self) -> None:
        """Clear the current query and filters when no request is in flight."""
        if self._active_worker is None:
            self.search_panel._reset()
            self.search_tabs.setCurrentWidget(self.search_panel)
        else:
            self.status.set_state("The current request cannot be cancelled safely")

    def create_results_context_menu(self) -> QMenu:
        """Build context actions for selected result rows."""
        menu = QMenu(self)
        copy_magnets = menu.addAction("Copy selected magnets")
        copy_magnets.triggered.connect(self.copy_selected_magnets)
        copy_title = menu.addAction("Copy title")
        copy_title.triggered.connect(self.copy_current_title)
        menu.addSeparator()
        open_magnet = menu.addAction("Open magnet")
        open_magnet.triggered.connect(self.details.open_magnet)
        open_torrent = menu.addAction("Open torrent URL")
        open_torrent.triggered.connect(self.details.open_torrent_url)
        return menu

    def show_results_context_menu(self, position: QPoint) -> None:
        self.create_results_context_menu().exec(self.results.table.viewport().mapToGlobal(position))

    def refresh_search(self) -> None:
        """Clear the service cache and repeat the last search against the API."""
        if self._last_search_values is None:
            self.status.set_state("Search before refreshing")
            return
        self.service.clear_cache()
        self.start_search(self._last_search_values)

    def reset_results(self) -> None:
        """Clear search rows and details after the search form resets."""
        self._all_torrents = []
        self.results.set_torrents([])
        self.details.show_torrent(None)
        self.status.set_count(0)
        self.status.set_state("Ready")

    def apply_local_filters(self) -> list[Torrent]:
        """Filter fetched rows immediately, without a new API call."""
        visible = filter_torrents(self._all_torrents, self.search_panel.filter_options())
        self.results.set_torrents(visible)
        self.status.set_count(len(visible))
        if self._all_torrents and not visible:
            self.status.set_state("No results match the local filters")
        return visible

    def select_best_release(self) -> None:
        """Rank the current local results and highlight the recommended row."""
        candidates = filter_torrents(self._all_torrents, self.search_panel.filter_options())
        selected = best_release(
            candidates, preferences_from_filters(self.search_panel.filter_options())
        )
        self.results.set_recommended(selected)
        if selected is not None:
            self.status.set_state(f"Best release: {selected.title}")

    def copy_selected_magnets(self) -> int:
        """Copy selected magnets to the clipboard in visible row order."""
        torrents = self.results.selected_torrents()
        if torrents:
            QApplication.clipboard().setText(export_magnets(torrents))
            self.status.set_state(f"Copied {len(torrents)} magnets")
        return len(torrents)

    def copy_visible_magnets(self) -> int:
        """Copy every currently visible magnet to the clipboard."""
        torrents = self.results.visible_torrents()
        if torrents:
            QApplication.clipboard().setText(export_magnets(torrents))
            self.status.set_state(f"Copied {len(torrents)} magnets")
        return len(torrents)

    def save_magnets(self) -> bool:
        """Choose a path and export all visible magnets as a text file."""
        path, _filter = QFileDialog.getSaveFileName(
            self, "Export magnets", "magnets.txt", "Text files (*.txt)"
        )
        return self._save_text(path, export_magnets(self.results.visible_torrents()))

    def save_json(self) -> bool:
        """Choose a path and export selected results as JSON."""
        path, _filter = QFileDialog.getSaveFileName(
            self, "Export results", "torrents.json", "JSON files (*.json)"
        )
        if not path:
            return False
        return self._save_text(path, export_json(self.results.selected_torrents()))

    def save_csv(self) -> bool:
        """Choose a path and export selected results as CSV."""
        path, _filter = QFileDialog.getSaveFileName(
            self, "Export results", "torrents.csv", "CSV files (*.csv)"
        )
        if not path:
            return False
        return self._save_text(path, export_csv(self.results.selected_torrents()))

    def _save_text(self, path: str, content: str) -> bool:
        if not path:
            return False
        try:
            with open(path, "w", encoding="utf-8", newline="") as output:
                output.write(content)
        except OSError as error:
            self.status.set_state(f"Export failed: {error}")
            return False
        self.status.set_state(f"Exported to {path}")
        return True

    def show_settings(self) -> bool:
        """Open preferences, persist accepted values and apply search defaults."""
        dialog = SettingsDialog(self.app_settings, self)
        if not dialog.exec():
            return False
        previous_timeout = self.app_settings.api_timeout
        self.app_settings = dialog.values()
        self.settings_store.save(self.app_settings)
        self._apply_settings_to_controls(self.app_settings)
        if self._owns_service and previous_timeout != self.app_settings.api_timeout:
            self.service.close()
            self.service = NyaaService(timeout=self.app_settings.api_timeout)
        self.status.set_state("Settings saved")
        return True

    def _apply_settings_to_controls(self, settings: AppSettings) -> None:
        if not hasattr(self, "search_panel"):
            return
        panel = self.search_panel
        panel.source_combo.setCurrentIndex(panel.source_combo.findData(settings.source))
        panel.resolution_filter.setCurrentText(settings.resolution)
        panel.language_filter.setCurrentText(settings.language)
        panel.exclude_multi.setChecked(settings.exclude_multi)
        panel.minimum_seeders.setValue(settings.minimum_seeders)
        panel.uploader_input.setText(settings.favorite_uploader)

    def configure_qbittorrent(self) -> bool:
        """Collect optional connection settings; password remains in memory."""
        dialog = QBittorrentConfigDialog(self._qbit_config, self)
        if not dialog.exec():
            return False
        self._qbit_config = dialog.config()
        self.qbit_send_action.setEnabled(bool(self.results.selected_torrents()))
        self.status.set_state("qBittorrent configured for this session")
        return True

    def send_selected_to_qbittorrent(self) -> None:
        """Send selected magnets to qBittorrent in a worker thread."""
        if self._qbit_config is None:
            self.status.set_state("Configure qBittorrent first")
            return
        magnets = [torrent.magnet for torrent in self.results.selected_torrents()]
        if not magnets:
            self.status.set_state("Select at least one result")
            return
        service = QBittorrentService(self._qbit_config)
        self.qbit_send_action.setEnabled(False)
        worker = SearchWorker(service.send_many, magnets=magnets)
        self._active_worker = worker
        worker.signals.result.connect(
            lambda count: self.status.set_state(f"Sent {count} torrent(s) to qBittorrent")
        )
        worker.signals.error.connect(lambda error: self.status.set_state(str(error)))
        worker.signals.finished.connect(self._search_finished)
        self.status.set_state("Sending to qBittorrent...")
        self.thread_pool.start(worker)

    def copy_current_title(self) -> bool:
        """Copy the selected torrent title to the system clipboard."""
        title = self.results.copy_title()
        if title is None:
            return False
        from PySide6.QtWidgets import QApplication

        QApplication.clipboard().setText(title)
        self.status.set_state("Title copied")
        return True

    def closeEvent(self, event: QCloseEvent) -> None:  # noqa: N802
        if self._owns_service:
            self.service.close()
        super().closeEvent(event)

    def _search_started(self) -> None:
        self.status.set_state("Searching...")

    def _search_succeeded(self, results: object) -> None:
        if isinstance(results, SeasonPlan):
            self._all_torrents = list(results.torrents)
            self.results.set_torrents(list(results.torrents))
            self.results.table.sortItems(9, Qt.SortOrder.AscendingOrder)
            self.season_panel.show_plan(
                len(results.episodes),
                results.expected_count,
                results.season,
                results.missing_episodes,
            )
            self.status.set_count(len(results.episodes))
            self.status.set_state("Season results updated")
            return
        if isinstance(results, SearchResults):
            self._all_torrents = list(results.data)
        elif isinstance(results, Sequence) and all(isinstance(item, Torrent) for item in results):
            self._all_torrents = list(results)
        else:
            self._search_failed(TypeError("The search service returned unexpected results"))
            return
        torrents = self.apply_local_filters()
        self.status.set_count(len(torrents))
        self.status.set_state("Search complete" if torrents else "No results")

    def _search_failed(self, error: object) -> None:
        self.status.set_state(str(error))

    def _search_finished(self) -> None:
        self.search_button.setEnabled(True)
        self.season_panel.search_button.setEnabled(True)
        self._active_worker = None
