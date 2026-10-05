from unittest.mock import Mock

from test_widgets import torrent

from nyaaapi_gui.services.nyaa_service import NyaaService


def test_search_and_detail_cache_and_clear() -> None:
    api = Mock()
    result = Mock()
    from nyaaapi import SearchResults, TorrentDetails

    result = SearchResults(1, (torrent(),))
    detail = TorrentDetails(torrent())
    api.search.return_value = result
    api.get.return_value = detail
    service = NyaaService(api)
    assert service.search("a") is result
    assert service.search("a") is result
    api.search.assert_called_once()
    assert service.get_torrent(1) is detail
    assert service.get_torrent(1) is detail
    api.get.assert_called_once()
    service.clear_cache()
    service.search("a")
    assert api.search.call_count == 2


def test_refresh_forces_search() -> None:
    from nyaaapi import SearchResults

    api = Mock()
    api.search.return_value = SearchResults(0, ())
    service = NyaaService(api)
    service.search("a")
    service.search("a", refresh=True)
    assert api.search.call_count == 2
