from __future__ import annotations

from collections.abc import Callable, Iterable
from dataclasses import dataclass
from typing import Any, cast


@dataclass(frozen=True, slots=True)
class QBittorrentConfig:
    """Connection settings; the password is kept in memory only."""

    host: str = "http://localhost"
    port: int = 8080
    username: str = ""
    password: str = ""
    download_path: str | None = None


class QBittorrentError(RuntimeError):
    """Connection, authentication, or add-torrent failure."""


class QBittorrentService:
    """Optional adapter for qBittorrent Web API."""

    def __init__(
        self,
        config: QBittorrentConfig,
        *,
        client_factory: Callable[..., Any] | None = None,
    ) -> None:
        self.config = config
        self._client_factory = client_factory

    def send(self, magnet: str) -> None:
        """Send one magnet URI to qBittorrent after explicit user action."""
        self.send_many([magnet])

    def send_many(self, magnets: Iterable[str]) -> int:
        """Send magnets and return their count; failures include no credentials."""
        try:
            factory = self._client_factory or _default_client_factory
            client = factory(
                host=self.config.host,
                port=self.config.port,
                username=self.config.username,
                password=self.config.password,
            )
            sent = 0
            for magnet in magnets:
                kwargs: dict[str, object] = {"urls": magnet}
                if self.config.download_path:
                    kwargs["save_path"] = self.config.download_path
                client.torrents_add(**kwargs)
                sent += 1
            return sent
        except Exception as error:
            raise QBittorrentError(_safe_message(error, self.config.password)) from error


def _default_client_factory(**kwargs: object) -> Any:
    try:
        from qbittorrentapi import Client
    except ImportError as error:
        raise QBittorrentError(
            "Install the optional release extra to enable qBittorrent support."
        ) from error
    return cast(Any, Client)(**kwargs)


def _safe_message(error: Exception, password: str = "") -> str:
    message = str(error)
    if password:
        message = message.replace(password, "[redacted]")
    return message or "Could not connect to qBittorrent. Check the host and credentials."
