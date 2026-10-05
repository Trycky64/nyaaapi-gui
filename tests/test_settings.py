from __future__ import annotations

from PySide6.QtCore import QSettings

from nyaaapi_gui.models.settings import AppSettings, SettingsStore


def test_settings_roundtrip_and_reset(qtbot) -> None:
    settings = QSettings("test-org", "test-app")
    settings.clear()
    store = SettingsStore(settings)
    desired = AppSettings(
        source="sukebei",
        resolution="1080p",
        language="VOSTFR",
        exclude_multi=True,
        minimum_seeders=12,
        favorite_uploader="Fansub",
        max_pages=4,
        api_timeout=25,
    )
    store.save(desired)
    assert store.load() == desired
    assert store.reset() == AppSettings()
    settings.clear()


def test_settings_clamp_bad_values() -> None:
    settings = QSettings("test-org", "test-invalid")
    settings.clear()
    settings.setValue("source", "invalid")
    settings.setValue("max_pages", 99999)
    settings.setValue("api_timeout", "invalid")
    loaded = SettingsStore(settings).load()
    assert loaded.source == "nyaa"
    assert loaded.max_pages == 1000
    assert loaded.api_timeout == 15.0
    settings.clear()
