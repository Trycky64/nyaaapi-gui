from nyaaapi_gui.widgets.qbittorrent_dialog import QBittorrentConfigDialog


def test_qbittorrent_dialog_keeps_password_only_in_memory(qtbot) -> None:
    dialog = QBittorrentConfigDialog()
    qtbot.addWidget(dialog)
    dialog.host_input.setText("http://127.0.0.1")
    dialog.password_input.setText("secret")
    dialog.path_input.setText("D:/Anime")
    config = dialog.config()
    assert config.host == "http://127.0.0.1"
    assert config.password == "secret"
    assert config.download_path == "D:/Anime"
    assert dialog.password_input.echoMode() != dialog.password_input.EchoMode.Normal
