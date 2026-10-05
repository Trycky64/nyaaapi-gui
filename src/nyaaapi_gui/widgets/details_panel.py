from __future__ import annotations

from nyaaapi import Torrent
from PySide6.QtCore import QUrl, Signal
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QLabel,
    QPlainTextEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


class DetailsPanel(QWidget):
    """Human-readable preview and user-triggered torrent link actions."""

    actionMessage = Signal(str)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.torrent: Torrent | None = None
        self.heading = QLabel("Select a result to see its details")
        self.text = QPlainTextEdit()
        self.text.setReadOnly(True)
        self.copy_magnet_button = QPushButton("Copy Magnet")
        self.open_magnet_button = QPushButton("Open Magnet")
        self.copy_torrent_button = QPushButton("Copy Torrent URL")
        self.open_torrent_button = QPushButton("Open Torrent URL")
        self.action_buttons = (
            self.copy_magnet_button,
            self.open_magnet_button,
            self.copy_torrent_button,
            self.open_torrent_button,
        )
        actions = QHBoxLayout()
        for button in self.action_buttons:
            button.setEnabled(False)
            actions.addWidget(button)
        self.copy_magnet_button.clicked.connect(self.copy_magnet)
        self.open_magnet_button.clicked.connect(self.open_magnet)
        self.copy_torrent_button.clicked.connect(self.copy_torrent_url)
        self.open_torrent_button.clicked.connect(self.open_torrent_url)
        layout = QVBoxLayout(self)
        layout.addWidget(self.heading)
        layout.addWidget(self.text)
        layout.addLayout(actions)

    def show_torrent(self, torrent: Torrent | None) -> None:
        """Display search fields already available for the selected torrent."""
        self.torrent = torrent
        if torrent is None:
            self.heading.setText("Select a result to see its details")
            self.text.clear()
            for button in self.action_buttons:
                button.setEnabled(False)
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
        for button in self.action_buttons:
            button.setEnabled(True)

    def copy_magnet(self) -> None:
        """Copy the selected magnet only after a user action."""
        if self.torrent is not None:
            QApplication.clipboard().setText(self.torrent.magnet)
            self.actionMessage.emit("Magnet copied")

    def open_magnet(self) -> None:
        """Ask the operating system to open the selected magnet."""
        if self.torrent is not None:
            QDesktopServices.openUrl(QUrl(self.torrent.magnet))

    def copy_torrent_url(self) -> None:
        """Copy the selected .torrent URL."""
        if self.torrent is not None:
            QApplication.clipboard().setText(self.torrent.torrent)
            self.actionMessage.emit("Torrent URL copied")

    def open_torrent_url(self) -> None:
        """Open the .torrent URL in the system's configured handler."""
        if self.torrent is not None:
            QDesktopServices.openUrl(QUrl(self.torrent.torrent))
