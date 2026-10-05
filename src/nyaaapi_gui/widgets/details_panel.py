from __future__ import annotations

from nyaaapi import Torrent
from PySide6.QtWidgets import QLabel, QPlainTextEdit, QVBoxLayout, QWidget


class DetailsPanel(QWidget):
    """Human-readable preview of a selected torrent."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.heading = QLabel("Select a result to see its details")
        self.text = QPlainTextEdit()
        self.text.setReadOnly(True)
        layout = QVBoxLayout(self)
        layout.addWidget(self.heading)
        layout.addWidget(self.text)

    def show_torrent(self, torrent: Torrent | None) -> None:
        """Display fields already available in the search response."""
        if torrent is None:
            self.heading.setText("Select a result to see its details")
            self.text.clear()
            return
        self.heading.setText(torrent.title)
        fields = {
            "Uploader": torrent.uploader or "Unknown",
            "Category": torrent.category,
            "Size": torrent.size,
            "Seeders": str(torrent.seeders),
            "Leechers": str(torrent.leechers),
            "Downloads": str(torrent.downloads),
            "Date": torrent.time.isoformat(sep=" ") if torrent.time else "Unknown",
            "Info hash": torrent.infohash or "Not loaded",
        }
        self.text.setPlainText("\n".join(f"{key}: {value}" for key, value in fields.items()))
