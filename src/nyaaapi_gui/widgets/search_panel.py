from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFormLayout,
    QGroupBox,
    QLabel,
    QLineEdit,
    QPushButton,
    QSpinBox,
    QWidget,
)

from nyaaapi_gui.models.filters import FilterOptions


class SearchPanel(QWidget):
    """Reusable controls for Nyaa and Sukebei searches."""

    searchRequested = Signal(object)
    resetRequested = Signal()
    filtersChanged = Signal()

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
        self.uploader_input.setPlaceholderText("Optional; searches this uploader")
        self.mode_label = QLabel("Search mode: Global")
        self.uploader_input.textChanged.connect(self._update_mode)
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
        self.resolution_filter = _combo("Any", "2160p", "1080p", "720p", "480p")
        self.language_filter = _combo("Any", "VOSTFR", "SUBFRENCH", "FRENCH", "MULTi", "RAW")
        self.codec_filter = _combo("Any", "H.264 / x264", "H.265 / HEVC / x265", "AV1")
        self.audio_filter = _combo("Any", "AAC", "Opus", "FLAC")
        self.exclude_multi = QCheckBox("Exclude MULTi")
        self.minimum_seeders = QSpinBox()
        self.minimum_seeders.setRange(0, 1_000_000)
        self.minimum_seeders.setPrefix("Min seeders: ")
        self.season_filter = QSpinBox()
        self.season_filter.setRange(0, 99)
        self.season_filter.setPrefix("Season: ")
        self.episode_filter = QSpinBox()
        self.episode_filter.setRange(0, 999)
        self.episode_filter.setPrefix("Episode: ")
        form = QFormLayout()
        form.addRow("Query", self.query_input)
        form.addRow("Source", self.source_combo)
        form.addRow("Uploader", self.uploader_input)
        form.addRow(self.mode_label)
        form.addRow("Category", self.category_input)
        form.addRow("Sub-category", self.subcategory_input)
        form.addRow("Sort", self.sort_combo)
        form.addRow("Order", self.order_combo)
        form.addRow("Page", self.page_input)
        form.addRow(self.search_button, self.reset_button)
        filters = QFormLayout()
        filters.addRow("Resolution", self.resolution_filter)
        filters.addRow("Language / tag", self.language_filter)
        filters.addRow("Codec", self.codec_filter)
        filters.addRow("Audio", self.audio_filter)
        filters.addRow(self.exclude_multi)
        filters.addRow(self.minimum_seeders)
        filters.addRow(self.season_filter)
        filters.addRow(self.episode_filter)
        filters_box = QGroupBox("Local filters")
        filters_box.setLayout(filters)
        layout = QFormLayout(self)
        self.form_layout = layout
        layout.addRow(_form_container(form))
        layout.addRow(filters_box)
        self.search_button.clicked.connect(self._emit_search)
        self.query_input.returnPressed.connect(self._emit_search)
        self.reset_button.clicked.connect(self._reset)
        for combo in (
            self.resolution_filter,
            self.language_filter,
            self.codec_filter,
            self.audio_filter,
        ):
            combo.currentIndexChanged.connect(self.filtersChanged)
        self.exclude_multi.stateChanged.connect(self.filtersChanged)
        self.minimum_seeders.valueChanged.connect(self.filtersChanged)
        self.season_filter.valueChanged.connect(self.filtersChanged)
        self.episode_filter.valueChanged.connect(self.filtersChanged)

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

    def filter_options(self) -> FilterOptions:
        """Return the current local-only filter selection."""
        return FilterOptions(
            resolution=self.resolution_filter.currentData(),
            language=self.language_filter.currentData(),
            codec=self.codec_filter.currentData(),
            audio=self.audio_filter.currentData(),
            exclude_multi=self.exclude_multi.isChecked(),
            minimum_seeders=self.minimum_seeders.value(),
            season=self.season_filter.value(),
            episode=self.episode_filter.value(),
        )

    def _update_mode(self, uploader: str) -> None:
        self.mode_label.setText(
            "Search mode: Uploader" if uploader.strip() else "Search mode: Global"
        )

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
        self.resolution_filter.setCurrentIndex(0)
        self.language_filter.setCurrentIndex(0)
        self.codec_filter.setCurrentIndex(0)
        self.audio_filter.setCurrentIndex(0)
        self.exclude_multi.setChecked(False)
        self.minimum_seeders.setValue(0)
        self.season_filter.setValue(0)
        self.episode_filter.setValue(0)
        self.resetRequested.emit()


def _combo(*values: str) -> QComboBox:
    combo = QComboBox()
    for value in values:
        combo.addItem(value, value)
    return combo


def _form_container(form: QFormLayout) -> QWidget:
    widget = QWidget()
    widget.setLayout(form)
    return widget
