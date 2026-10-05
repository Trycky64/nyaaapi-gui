from __future__ import annotations

from nyaaapi_gui.workers.search_worker import SearchWorker


def test_worker_emits_success_lifecycle(qtbot) -> None:
    worker = SearchWorker(lambda **kwargs: kwargs["query"], query="anime")
    events: list[str] = []
    worker.signals.started.connect(lambda: events.append("started"))
    worker.signals.result.connect(lambda value: events.append(str(value)))
    worker.signals.finished.connect(lambda: events.append("finished"))
    worker.run()
    assert events == ["started", "anime", "finished"]


def test_worker_emits_error_and_always_finishes(qtbot) -> None:
    def fail(**_kwargs: object) -> None:
        raise TimeoutError("offline")

    worker = SearchWorker(fail)
    events: list[str] = []
    worker.signals.started.connect(lambda: events.append("started"))
    worker.signals.error.connect(lambda error: events.append(type(error).__name__))
    worker.signals.finished.connect(lambda: events.append("finished"))
    worker.run()
    assert events == ["started", "TimeoutError", "finished"]
