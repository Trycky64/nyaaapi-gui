from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QMainWindow, QSplitter, QVBoxLayout, QWidget

from .widgets.details_panel import DetailsPanel
from .widgets.results_table import ResultsTable
from .widgets.search_panel import SearchPanel
from .widgets.status_bar import StatusWidget


class MainWindow(QMainWindow):
    """Main application window."""

    def __init__(self) -> None:
        super().__init__()
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
