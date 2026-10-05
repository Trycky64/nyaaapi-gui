from __future__ import annotations

from PySide6.QtWidgets import (
    QLineEdit,
    QMainWindow,
    QPushButton,
    QTableWidget,
    QVBoxLayout,
    QWidget,
)


class MainWindow(QMainWindow):
    """Main application window."""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("NyaaAPI GUI")
        self.setMinimumSize(760, 480)
        self.query_input = QLineEdit()
        self.query_input.setPlaceholderText("Search torrents...")
        self.query_input.setObjectName("queryInput")
        self.search_button = QPushButton("Search")
        self.search_button.setObjectName("searchButton")
        self.results = QTableWidget(0, 1)
        self.results.setHorizontalHeaderLabels(["Results"])
        layout = QVBoxLayout()
        layout.addWidget(self.query_input)
        layout.addWidget(self.search_button)
        layout.addWidget(self.results)
        central = QWidget()
        central.setLayout(layout)
        self.setCentralWidget(central)
