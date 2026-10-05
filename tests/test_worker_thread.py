from __future__ import annotations

from threading import get_ident

from PySide6.QtCore import QThreadPool

from nyaaapi_gui.workers.search_worker import SearchWorker


def test_worker_operation_runs_off_ui_thread(qtbot) -> None:
    ui_thread = get_ident()
    result: list[int] = []
    worker = SearchWorker(lambda: get_ident())
    worker.signals.result.connect(lambda value: result.append(value))
    pool = QThreadPool()
    with qtbot.waitSignal(worker.signals.finished, timeout=3000):
        pool.start(worker)
    assert result
    assert result[0] != ui_thread
