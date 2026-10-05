from unittest.mock import Mock

import pytest

from nyaaapi_gui.integrations.qbittorrent import (
    QBittorrentConfig,
    QBittorrentError,
    QBittorrentService,
)


def test_qbittorrent_empty_batch_and_single_send() -> None:
    client = Mock()
    service = QBittorrentService(QBittorrentConfig(), client_factory=lambda **_: client)
    assert service.send_many([]) == 0
    service.send("magnet:abc")
    client.torrents_add.assert_called_once_with(urls="magnet:abc")


def test_optional_dependency_missing_is_explained(monkeypatch) -> None:
    import builtins

    original = builtins.__import__

    def import_without_qbit(name, *args, **kwargs):
        if name == "qbittorrentapi":
            raise ImportError("missing optional package")
        return original(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", import_without_qbit)
    with pytest.raises(QBittorrentError, match="optional release extra"):
        QBittorrentService(QBittorrentConfig()).send("magnet:x")
