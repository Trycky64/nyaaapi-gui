from __future__ import annotations

from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QDoubleSpinBox,
    QFormLayout,
    QLineEdit,
    QPushButton,
    QSpinBox,
    QWidget,
)

from nyaaapi_gui.models.settings import AppSettings


class SettingsDialog(QDialog):
    """Edit persistent search preferences and reset them to defaults."""

    def __init__(self, settings: AppSettings, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("NyaaAPI GUI settings")
        self.source_combo = QComboBox()
        self.source_combo.addItem("Nyaa", "nyaa")
        self.source_combo.addItem("Sukebei", "sukebei")
        self.source_combo.setCurrentIndex(self.source_combo.findData(settings.source))
        self.resolution_combo = _combo("Any", "2160p", "1080p", "720p", "480p")
        self.resolution_combo.setCurrentText(settings.resolution)
        self.language_combo = _combo("Any", "VOSTFR", "SUBFRENCH", "FRENCH", "MULTi", "RAW")
        self.language_combo.setCurrentText(settings.language)
        self.exclude_multi = QCheckBox()
        self.exclude_multi.setChecked(settings.exclude_multi)
        self.minimum_seeders = QSpinBox()
        self.minimum_seeders.setRange(0, 1_000_000)
        self.minimum_seeders.setValue(settings.minimum_seeders)
        self.favorite_uploader = QLineEdit(settings.favorite_uploader)
        self.max_pages = QSpinBox()
        self.max_pages.setRange(1, 1000)
        self.max_pages.setValue(settings.max_pages)
        self.api_timeout = QDoubleSpinBox()
        self.api_timeout.setRange(0.5, 300)
        self.api_timeout.setSingleStep(0.5)
        self.api_timeout.setValue(settings.api_timeout)
        self.reset_button = QPushButton("Reset Defaults")
        self.reset_button.clicked.connect(self.reset_defaults)
        form = QFormLayout(self)
        form.addRow("Default source", self.source_combo)
        form.addRow("Preferred resolution", self.resolution_combo)
        form.addRow("Preferred language", self.language_combo)
        form.addRow("Exclude MULTi", self.exclude_multi)
        form.addRow("Minimum seeders", self.minimum_seeders)
        form.addRow("Favorite uploader", self.favorite_uploader)
        form.addRow("Maximum pages", self.max_pages)
        form.addRow("API timeout (seconds)", self.api_timeout)
        form.addRow(self.reset_button)
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        form.addRow(buttons)

    def values(self) -> AppSettings:
        """Return the settings currently shown in the form."""
        return AppSettings(
            source=str(self.source_combo.currentData()),
            resolution=self.resolution_combo.currentText(),
            language=self.language_combo.currentText(),
            exclude_multi=self.exclude_multi.isChecked(),
            minimum_seeders=self.minimum_seeders.value(),
            favorite_uploader=self.favorite_uploader.text().strip(),
            max_pages=self.max_pages.value(),
            api_timeout=self.api_timeout.value(),
        )

    def reset_defaults(self) -> None:
        """Reset every form value to the documented application defaults."""
        defaults = AppSettings()
        self.source_combo.setCurrentIndex(self.source_combo.findData(defaults.source))
        self.resolution_combo.setCurrentText(defaults.resolution)
        self.language_combo.setCurrentText(defaults.language)
        self.exclude_multi.setChecked(defaults.exclude_multi)
        self.minimum_seeders.setValue(defaults.minimum_seeders)
        self.favorite_uploader.clear()
        self.max_pages.setValue(defaults.max_pages)
        self.api_timeout.setValue(defaults.api_timeout)


def _combo(*items: str) -> QComboBox:
    combo = QComboBox()
    combo.addItems(list(items))
    return combo
