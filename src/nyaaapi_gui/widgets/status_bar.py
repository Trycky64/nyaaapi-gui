from __future__ import annotations

from PySide6.QtWidgets import QLabel, QStatusBar


class StatusWidget(QStatusBar):
    """Status bar showing network state and result count."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.state_label = QLabel("Ready")
        self.count_label = QLabel("0 results")
        self.addWidget(self.state_label, 1)
        self.addPermanentWidget(self.count_label)

    def set_state(self, message: str) -> None:
        self.state_label.setText(message)

    def set_count(self, count: int) -> None:
        self.count_label.setText(f"{count} results")
