from __future__ import annotations

from unittest.mock import patch

from PySide6.QtCore import QUrl
from PySide6.QtWidgets import QApplication
from test_widgets import torrent

from nyaaapi_gui.widgets.details_panel import DetailsPanel


def test_link_actions_require_selection(qtbot) -> None:
    panel = DetailsPanel()
    qtbot.addWidget(panel)
    panel.open_magnet()
    panel.copy_magnet()
    assert not panel.copy_magnet_button.isEnabled()


def test_copy_and_open_links_are_explicit_user_actions(qtbot) -> None:
    panel = DetailsPanel()
    qtbot.addWidget(panel)
    selected = torrent()
    panel.show_torrent(selected)
    with patch.object(QApplication.clipboard(), "setText") as clipboard, patch(
        "nyaaapi_gui.widgets.details_panel.QDesktopServices.openUrl", return_value=True
    ) as opener:
        panel.copy_magnet_button.click()
        clipboard.assert_called_once_with(selected.magnet)
        panel.open_magnet_button.click()
        opener.assert_called_once_with(QUrl(selected.magnet))
        panel.copy_torrent_button.click()
        assert clipboard.call_args.args == (selected.torrent,)
        panel.open_torrent_button.click()
        assert opener.call_args.args == (QUrl(selected.torrent),)
