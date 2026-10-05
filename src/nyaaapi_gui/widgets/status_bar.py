from __future__ import annotations

from PySide6.QtWidgets import QLabel, QProgressBar, QStatusBar, QWidget


class StatusWidget(QStatusBar):
    """Status bar showing network state, loading indicator, and result count."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.state_label = QLabel("Ready")
        self.count_label = QLabel("0 results")
        self.progress = QProgressBar()
        self.progress.setRange(0, 0)
        self.progress.setMaximumWidth(110)
        self.progress.hide()
        self.addWidget(self.state_label, 1)
        self.addWidget(self.progress)
        self.addPermanentWidget(self.count_label)

    def set_state(self, message: str) -> None:
        self.state_label.setText(message)
        self.progress.setVisible(message.casefold().startswith(("searching", "sending")))

    def set_count(self, count: int) -> None:
        self.count_label.setText(f"{count} results")
