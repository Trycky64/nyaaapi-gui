from __future__ import annotations

from nyaaapi_gui import app as app_module
from nyaaapi_gui.main_window import MainWindow


def test_application_window_starts(qtbot) -> None:
    window = MainWindow()
    qtbot.addWidget(window)
    window.show()
    assert window.windowTitle() == "NyaaAPI GUI"
    assert window.query_input.placeholderText() == "Search torrents?"
    assert window.results.rowCount() == 0


def test_main_constructs_and_runs_app(monkeypatch) -> None:
    seen: dict[str, object] = {}

    class FakeApplication:
        def __init__(self, args: list[str]) -> None:
            seen["args"] = args

        def setApplicationName(self, name: str) -> None:
            seen["name"] = name

        def setApplicationVersion(self, version: str) -> None:
            seen["version"] = version

        def exec(self) -> int:
            return 7

    class FakeWindow:
        def show(self) -> None:
            seen["shown"] = True

    monkeypatch.setattr(app_module.QApplication, "instance", lambda: None)
    monkeypatch.setattr(app_module, "QApplication", FakeApplication)
    monkeypatch.setattr(app_module, "MainWindow", FakeWindow)
    assert app_module.main() == 7
    assert seen["name"] == "NyaaAPI GUI"
    assert seen["shown"] is True
