from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QComboBox,
    QFormLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSpinBox,
    QWidget,
)


class SeasonPanel(QWidget):
    """Controls for locating and comparing a season's available releases."""

    searchRequested = Signal(object)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.anime_input = QLineEdit()
        self.season_input = QSpinBox()
        self.season_input.setRange(1, 99)
        self.uploader_input = QLineEdit()
        self.resolution_combo = QComboBox()
        self.resolution_combo.addItems(["1080p", "2160p", "720p", "480p"])
        self.language_combo = QComboBox()
        self.language_combo.addItems(["VOSTFR", "SUBFRENCH", "FRENCH", "MULTi", "RAW"])
        self.start_episode = QSpinBox()
        self.start_episode.setRange(1, 999)
        self.start_episode.setValue(1)
        self.end_episode = QSpinBox()
        self.end_episode.setRange(1, 999)
        self.end_episode.setValue(24)
        self.search_button = QPushButton("Search season")
        self.summary = QLabel("No season search yet")
        self.missing_label = QLabel("")
        self.missing_label.setWordWrap(True)
        form = QFormLayout(self)
        form.addRow("Anime", self.anime_input)
        form.addRow("Season", self.season_input)
        form.addRow("Uploader", self.uploader_input)
        form.addRow("Resolution", self.resolution_combo)
        form.addRow("Language", self.language_combo)
        form.addRow("First episode", self.start_episode)
        form.addRow("Last episode", self.end_episode)
        form.addRow(self.search_button)
        form.addRow(self.summary)
        form.addRow(self.missing_label)
        self.search_button.clicked.connect(self._emit_search)
        self.start_episode.valueChanged.connect(self._keep_valid_range)
        self.end_episode.valueChanged.connect(self._keep_valid_range)

    def values(self) -> dict[str, object]:
        """Return the season search configuration."""
        return {
            "anime": self.anime_input.text().strip(),
            "season": self.season_input.value(),
            "uploader": self.uploader_input.text().strip() or None,
            "resolution": self.resolution_combo.currentText(),
            "language": self.language_combo.currentText(),
            "start_episode": self.start_episode.value(),
            "end_episode": self.end_episode.value(),
        }

    def show_plan(self, found: int, expected: int, season: int, missing: tuple[int, ...]) -> None:
        """Display the discovered episode count without assuming season completion."""
        self.summary.setText(f"Season {season}: {found} / {expected} episodes found so far")
        labels = [f"S{season:02d}E{episode:02d}" for episode in missing]
        self.missing_label.setText(
            "Missing in current results: " + ", ".join(labels)
            if labels
            else "No gaps in selected range"
        )

    def _emit_search(self) -> None:
        self.searchRequested.emit(self.values())

    def _keep_valid_range(self, value: int) -> None:
        source = self.sender()
        if source is self.start_episode and value > self.end_episode.value():
            self.end_episode.setValue(value)
        elif source is self.end_episode and value < self.start_episode.value():
            self.start_episode.setValue(value)
