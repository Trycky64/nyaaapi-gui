from __future__ import annotations

from unittest.mock import Mock

from nyaaapi_gui.main_window import MainWindow


def test_search_uses_uploader_api_when_username_is_set(qtbot) -> None:
    service = Mock()
    service.search_user.return_value = []
    window = MainWindow(service)
    qtbot.addWidget(window)
    window.start_search({"query": "Mushoku Tensei", "uploader": "Tsundere-Raws"})
    qtbot.waitUntil(lambda: window._active_worker is None)
    service.search_user.assert_called_once()
    assert service.search_user.call_args.kwargs["user_name"] == "Tsundere-Raws"
    assert service.search_user.call_args.kwargs["query"] == "Mushoku Tensei"
    service.search.assert_not_called()
