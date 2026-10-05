from nyaaapi_gui.widgets.search_panel import SearchPanel


def test_uploader_mode_is_visible(qtbot) -> None:
    panel = SearchPanel()
    qtbot.addWidget(panel)
    assert panel.mode_label.text() == "Search mode: Global"
    panel.uploader_input.setText(" Tsundere-Raws ")
    assert panel.mode_label.text() == "Search mode: Uploader"
    panel.uploader_input.clear()
    assert panel.mode_label.text() == "Search mode: Global"
