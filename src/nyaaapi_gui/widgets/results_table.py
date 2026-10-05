from __future__ import annotations

from nyaaapi import Torrent
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QLabel,
    QStackedWidget,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from nyaaapi_gui.models.release_info import parse_release_title


class SortableItem(QTableWidgetItem):
    """Table item that sorts on its underlying value when provided."""

    def __lt__(self, other: QTableWidgetItem) -> bool:
        left = self.data(Qt.ItemDataRole.UserRole)
        right = other.data(Qt.ItemDataRole.UserRole)
        if left is not None and right is not None:
            return left < right
        return super().__lt__(other)


class ResultsTable(QWidget):
    """Resizable, sortable table of torrents with multi-row selection."""

    torrentSelected = Signal(object)

    COLUMNS = (
        "Title",
        "Category",
        "Size",
        "Seeders",
        "Leechers",
        "Downloads",
        "Date/Time",
        "Uploader",
        "Season",
        "Episode",
    )

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._recommended_title: str | None = None
        self.table = QTableWidget(0, len(self.COLUMNS))
        self.table.setHorizontalHeaderLabels(list(self.COLUMNS))
        self.table.setSortingEnabled(True)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableWidget.SelectionMode.ExtendedSelection)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.empty_label = QLabel("No results")
        self.empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.stack = QStackedWidget()
        self.stack.addWidget(self.empty_label)
        self.stack.addWidget(self.table)
        self.table.itemSelectionChanged.connect(self._selection_changed)
        self.table.cellDoubleClicked.connect(self._double_clicked)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.stack)

    def set_empty_message(self, message: str) -> None:
        """Set the empty-state text shown when there are no rows."""
        self.empty_label.setText(message)

    def set_recommended(self, torrent: Torrent | None) -> None:
        """Highlight the recommended release row."""
        self._recommended_title = torrent.title if torrent else None
        for row in range(self.table.rowCount()):
            item = self.table.item(row, 0)
            if item is not None:
                font = item.font()
                font.setBold(item.text() == self._recommended_title)
                item.setFont(font)

    def rowCount(self) -> int:
        """Return the number of visible result rows."""
        return self.table.rowCount()

    def set_torrents(self, torrents: tuple[Torrent, ...] | list[Torrent]) -> None:
        """Replace table rows with torrent objects."""
        self.table.setSortingEnabled(False)
        self.table.setRowCount(len(torrents))
        self.stack.setCurrentWidget(self.table if torrents else self.empty_label)
        for row, torrent in enumerate(torrents):
            date_text = torrent.time.isoformat(sep=" ") if torrent.time else ""
            release = parse_release_title(torrent.title)
            values: tuple[tuple[str, object], ...] = (
                (torrent.title, torrent.title.casefold()),
                (torrent.category, torrent.category.casefold()),
                (torrent.size, _size_bytes(torrent.size)),
                (str(torrent.seeders), torrent.seeders),
                (str(torrent.leechers), torrent.leechers),
                (str(torrent.downloads), torrent.downloads),
                (date_text, torrent.time.timestamp() if torrent.time else 0),
                (torrent.uploader or "", (torrent.uploader or "").casefold()),
                (str(release.season or ""), release.season or 0),
                (str(release.episode or ""), release.episode or 0),
            )
            for column, (display, sort_value) in enumerate(values):
                item = SortableItem(display)
                item.setData(Qt.ItemDataRole.UserRole, sort_value)
                item.setData(Qt.ItemDataRole.UserRole + 1, torrent)
                if column == 0 and torrent.title == self._recommended_title:
                    font = item.font()
                    font.setBold(True)
                    item.setFont(font)
                self.table.setItem(row, column, item)
        self.table.setSortingEnabled(True)

    def selected_torrents(self) -> list[Torrent]:
        """Return selected torrents in their visible row order."""
        rows = sorted({index.row() for index in self.table.selectionModel().selectedRows()})
        return [self.torrent_at(row) for row in rows if self.torrent_at(row) is not None]

    def visible_torrents(self) -> list[Torrent]:
        """Return torrents in the current visible sort order."""
        return [
            torrent
            for row in range(self.table.rowCount())
            if (torrent := self.torrent_at(row)) is not None
        ]

    def torrent_at(self, row: int) -> Torrent | None:
        item = self.table.item(row, 0)
        torrent = item.data(Qt.ItemDataRole.UserRole + 1) if item else None
        return torrent if isinstance(torrent, Torrent) else None

    def copy_title(self) -> str | None:
        """Return the title from the current row for clipboard handling."""
        rows = self.table.selectionModel().selectedRows()
        torrent = self.torrent_at(rows[0].row()) if rows else None
        return torrent.title if torrent else None

    def _selection_changed(self) -> None:
        rows = self.table.selectionModel().selectedRows()
        self.torrentSelected.emit(self.torrent_at(rows[0].row()) if rows else None)

    def _double_clicked(self, row: int, _column: int) -> None:
        self.torrentSelected.emit(self.torrent_at(row))


def _size_bytes(text: str) -> float:
    """Parse human-readable binary file sizes for sorting."""
    parts = text.strip().split()
    if not parts:
        return 0
    try:
        amount = float(parts[0])
    except ValueError:
        return 0
    units = {"B": 0, "KB": 1, "MB": 2, "GB": 3, "TB": 4, "KiB": 1, "MiB": 2, "GiB": 3, "TiB": 4}
    unit = parts[1] if len(parts) > 1 else "B"
    return amount * (1024 ** units.get(unit.upper(), 0))
