from nyaaapi_gui.models.settings import AppSettings
from nyaaapi_gui.widgets.settings_dialog import SettingsDialog


def test_settings_dialog_reset_defaults(qtbot) -> None:
    dialog = SettingsDialog(AppSettings(source="sukebei", max_pages=20, exclude_multi=True))
    qtbot.addWidget(dialog)
    dialog.reset_button.click()
    assert dialog.values() == AppSettings()
