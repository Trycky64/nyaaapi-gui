from unittest.mock import Mock

import pytest

from nyaaapi_gui.integrations.qbittorrent import (
    QBittorrentConfig,
    QBittorrentError,
    QBittorrentService,
)


def test_qbittorrent_receives_magnets_and_optional_path() -> None:
    client = Mock()
    service = QBittorrentService(
        QBittorrentConfig("http://host", 9090, "user", "secret", "D:/Anime"),
        client_factory=lambda **_kwargs: client,
    )
    assert service.send_many(["magnet:one", "magnet:two"]) == 2
    assert client.torrents_add.call_args_list[0].kwargs == {
        "urls": "magnet:one",
        "save_path": "D:/Anime",
    }
    assert client.torrents_add.call_count == 2


def test_qbittorrent_errors_are_wrapped_without_secret() -> None:
    client = Mock()
    client.torrents_add.side_effect = RuntimeError("private unauthorized")
    service = QBittorrentService(
        QBittorrentConfig(password="private"), client_factory=lambda **_kwargs: client
    )
    with pytest.raises(QBittorrentError, match="unauthorized") as error:
        service.send("magnet:test")
    assert "private" not in str(error.value)
    assert "[redacted]" in str(error.value)
