from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import cast

from PySide6.QtCore import QSettings


@dataclass(frozen=True, slots=True)
class AppSettings:
    """Persisted application preferences; never contains qBittorrent secrets."""

    source: str = "nyaa"
    resolution: str = "Any"
    language: str = "Any"
    exclude_multi: bool = False
    minimum_seeders: int = 0
    favorite_uploader: str = ""
    max_pages: int = 10
    api_timeout: float = 15.0


class SettingsStore:
    """Typed wrapper around QSettings."""

    def __init__(self, settings: QSettings | None = None) -> None:
        self._settings = settings or QSettings("Trycky64", "NyaaAPI GUI")

    def load(self) -> AppSettings:
        """Read preferences, falling back safely when stored values are invalid."""
        return AppSettings(
            source=self._choice("source", "nyaa", {"nyaa", "sukebei"}),
            resolution=self._choice("resolution", "Any", {"Any", "2160p", "1080p", "720p", "480p"}),
            language=self._choice(
                "language", "Any", {"Any", "VOSTFR", "SUBFRENCH", "FRENCH", "MULTi", "RAW"}
            ),
            exclude_multi=cast(bool, self._settings.value("exclude_multi", False, type=bool)),
            minimum_seeders=self._bounded_int("minimum_seeders", 0, 0, 1_000_000),
            favorite_uploader=str(self._settings.value("favorite_uploader", "")),
            max_pages=self._bounded_int("max_pages", 10, 1, 1000),
            api_timeout=self._bounded_float("api_timeout", 15.0, 0.5, 300.0),
        )

    def save(self, settings: AppSettings) -> None:
        """Store user preferences, excluding integration passwords."""
        for key, value in asdict(settings).items():
            self._settings.setValue(key, value)
        self._settings.sync()

    def reset(self) -> AppSettings:
        """Remove stored preferences and return defaults."""
        self._settings.clear()
        self._settings.sync()
        return AppSettings()

    def _choice(self, key: str, default: str, allowed: set[str]) -> str:
        value = str(self._settings.value(key, default))
        return value if value in allowed else default

    def _bounded_int(self, key: str, default: int, minimum: int, maximum: int) -> int:
        try:
            value = int(str(self._settings.value(key, default)))
        except (TypeError, ValueError):
            return default
        return min(maximum, max(minimum, value))

    def _bounded_float(self, key: str, default: float, minimum: float, maximum: float) -> float:
        try:
            value = float(str(self._settings.value(key, default)))
        except (TypeError, ValueError):
            return default
        return min(maximum, max(minimum, value))
