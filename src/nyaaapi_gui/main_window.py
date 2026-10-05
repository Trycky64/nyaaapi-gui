from __future__ import annotations

from PySide6.QtCore import Qt, QThreadPool
from PySide6.QtWidgets import QMainWindow, QSplitter, QVBoxLayout, QWidget

from .services.nyaa_service import NyaaService
from .widgets.details_panel import DetailsPanel
from .widgets.results_table import ResultsTable
from .widgets.search_panel import SearchPanel
from .widgets.status_bar import StatusWidget
from .workers.search_worker import SearchWorker


class MainWindow(QMainWindow):
    """Main application window and coordinator for search widgets."""

    def __init__(self, service: NyaaService | None = None) -> None:
        super().__init__()
        self.service = service or NyaaService()
        self._owns_service = service is None
        self._active_worker: SearchWorker | None = None
        self.thread_pool = QThreadPool.globalInstance()
        self.setWindowTitle("NyaaAPI GUI")
        self.setMinimumSize(1024, 680)
        self.search_panel = SearchPanel()
        self.query_input = self.search_panel.query_input
        self.search_button = self.search_panel.search_button
        self.results = ResultsTable()
        self.details = DetailsPanel()
        splitter = QSplitter()
        splitter.setOrientation(Qt.Orientation.Vertical)
        splitter.addWidget(self.results)
        splitter.addWidget(self.details)
        splitter.setSizes([440, 180])
        layout = QVBoxLayout()
        layout.addWidget(self.search_panel)
        layout.addWidget(splitter, 1)
        central = QWidget()
        central.setLayout(layout)
        self.setCentralWidget(central)
        self.status = StatusWidget(self)
        self.setStatusBar(self.status)
        self.results.torrentSelected.connect(self.details.show_torrent)
        self.search_panel.searchRequested.connect(self.start_search)
        self.search_panel.resetRequested.connect(self.reset_results)

    def start_search(self, values: dict[str, object] | None = None) -> None:
        """Run the current search in the global Qt thread pool."""
        if self._active_worker is not None:
            return
        options = values or self.search_panel.values()
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
            kwargs["user_name"] = uploader
            operation = self.service.search_user
        else:
            operation = self.service.search
        worker = SearchWorker(operation, **kwargs)
        self._active_worker = worker
        worker.signals.started.connect(self._search_started)
        worker.signals.result.connect(self._search_succeeded)
        worker.signals.error.connect(self._search_failed)
        worker.signals.finished.connect(self._search_finished)
        self.search_button.setEnabled(False)
        self.status.set_state("Searching...")
        self.thread_pool.start(worker)

    def reset_results(self) -> None:
        """Clear search rows and details after the search form resets."""
        self.results.set_torrents([])
        self.details.show_torrent(None)
        self.status.set_count(0)
        self.status.set_state("Ready")

    def copy_current_title(self) -> bool:
        """Copy the selected torrent title to the system clipboard."""
        title = self.results.copy_title()
        if title is None:
            return False
        from PySide6.QtWidgets import QApplication

        QApplication.clipboard().setText(title)
        self.status.set_state("Title copied")
        return True

    def closeEvent(self, event) -> None:  # noqa: N802
        if self._owns_service:
            self.service.close()
        super().closeEvent(event)

    def _search_started(self) -> None:
        self.status.set_state("Searching...")

    def _search_succeeded(self, results: object) -> None:
        torrents = list(results)
        self.results.set_torrents(torrents)
        self.status.set_count(len(torrents))
        self.status.set_state("Search complete" if torrents else "No results")

    def _search_failed(self, error: object) -> None:
        self.status.set_state(str(error))

    def _search_finished(self) -> None:
        self.search_button.setEnabled(True)
        self._active_worker = None
