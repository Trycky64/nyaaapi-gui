from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QComboBox,
    QFormLayout,
    QLineEdit,
    QPushButton,
    QSpinBox,
    QWidget,
)


class SearchPanel(QWidget):
    """Reusable controls for Nyaa and Sukebei searches."""

    searchRequested = Signal(object)
    resetRequested = Signal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.query_input = QLineEdit()
        self.query_input.setPlaceholderText("Search torrents...")
        self.query_input.setObjectName("queryInput")
        self.source_combo = QComboBox()
        self.source_combo.addItem("Nyaa", "nyaa")
        self.source_combo.addItem("Sukebei", "sukebei")
        self.uploader_input = QLineEdit()
        self.uploader_input.setObjectName("uploaderInput")
        self.category_input = QLineEdit()
        self.subcategory_input = QLineEdit()
        self.sort_combo = QComboBox()
        self.sort_combo.addItem("Default", "")
        for value in ("seeders", "leechers", "downloads", "size", "date"):
            self.sort_combo.addItem(value.title(), value)
        self.order_combo = QComboBox()
        self.order_combo.addItem("Descending", "desc")
        self.order_combo.addItem("Ascending", "asc")
        self.page_input = QSpinBox()
        self.page_input.setRange(1, 9999)
        self.page_input.setValue(1)
        self.search_button = QPushButton("Search")
        self.search_button.setObjectName("searchButton")
        self.reset_button = QPushButton("Reset")
        form = QFormLayout(self)
        form.addRow("Query", self.query_input)
        form.addRow("Source", self.source_combo)
        form.addRow("Uploader", self.uploader_input)
        form.addRow("Category", self.category_input)
        form.addRow("Sub-category", self.subcategory_input)
        form.addRow("Sort", self.sort_combo)
        form.addRow("Order", self.order_combo)
        form.addRow("Page", self.page_input)
        form.addRow(self.search_button, self.reset_button)
        self.search_button.clicked.connect(self._emit_search)
        self.query_input.returnPressed.connect(self._emit_search)
        self.reset_button.clicked.connect(self._reset)

    def values(self) -> dict[str, object]:
        """Return only meaningful API search options."""
        return {
            "query": self.query_input.text().strip() or None,
            "source": self.source_combo.currentData(),
            "uploader": self.uploader_input.text().strip() or None,
            "category": self.category_input.text().strip() or None,
            "sub_category": self.subcategory_input.text().strip() or None,
            "sort": self.sort_combo.currentData() or None,
            "order": self.order_combo.currentData(),
            "page": self.page_input.value(),
        }

    def _emit_search(self) -> None:
        self.searchRequested.emit(self.values())

    def _reset(self) -> None:
        self.query_input.clear()
        self.source_combo.setCurrentIndex(0)
        self.uploader_input.clear()
        self.category_input.clear()
        self.subcategory_input.clear()
        self.sort_combo.setCurrentIndex(0)
        self.order_combo.setCurrentIndex(0)
        self.page_input.setValue(1)
        self.resetRequested.emit()
