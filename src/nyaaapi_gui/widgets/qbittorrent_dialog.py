from __future__ import annotations

from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QLineEdit,
    QSpinBox,
)

from nyaaapi_gui.integrations.qbittorrent import QBittorrentConfig


class QBittorrentConfigDialog(QDialog):
    """Collect qBittorrent settings without persisting the password."""

    def __init__(self, config: QBittorrentConfig | None = None, parent=None) -> None:
        super().__init__(parent)
        config = config or QBittorrentConfig()
        self.setWindowTitle("qBittorrent connection")
        self.host_input = QLineEdit(config.host)
        self.port_input = QSpinBox()
        self.port_input.setRange(1, 65535)
        self.port_input.setValue(config.port)
        self.username_input = QLineEdit(config.username)
        self.password_input = QLineEdit(config.password)
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.path_input = QLineEdit(config.download_path or "")
        form = QFormLayout(self)
        form.addRow("Host", self.host_input)
        form.addRow("Port", self.port_input)
        form.addRow("Username", self.username_input)
        form.addRow("Password (not saved)", self.password_input)
        form.addRow("Download path", self.path_input)
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        form.addRow(buttons)

    def config(self) -> QBittorrentConfig:
        """Return entered settings, including password only for this session."""
        return QBittorrentConfig(
            host=self.host_input.text().strip(),
            port=self.port_input.value(),
            username=self.username_input.text(),
            password=self.password_input.text(),
            download_path=self.path_input.text().strip() or None,
        )
