from __future__ import annotations

from collections.abc import Callable
from typing import Any

from PySide6.QtCore import QObject, QRunnable, Signal, Slot


class WorkerSignals(QObject):
    """Signals emitted by a background operation."""

    started = Signal()
    result = Signal(object)
    error = Signal(object)
    finished = Signal()


class SearchWorker(QRunnable):
    """Run a service operation on the Qt thread pool."""

    def __init__(self, operation: Callable[..., Any], **kwargs: object) -> None:
        super().__init__()
        self.operation = operation
        self.kwargs = kwargs
        self.signals = WorkerSignals()
        self.setAutoDelete(False)

    @Slot()
    def run(self) -> None:
        """Execute the operation and notify listeners of every outcome."""
        self.signals.started.emit()
        try:
            result = self.operation(**self.kwargs)
            self.signals.result.emit(result)
        except Exception as error:
            self.signals.error.emit(error)
        finally:
            self.signals.finished.emit()
