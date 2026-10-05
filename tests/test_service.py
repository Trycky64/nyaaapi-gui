from __future__ import annotations

from unittest.mock import Mock

import pytest
from nyaaapi import NyaaAPIHTTPError, NyaaAPINotFoundError, NyaaAPIRateLimitError

from nyaaapi_gui.services.nyaa_service import NyaaService, ServiceError


def test_search_routes_through_backend() -> None:
    api = Mock()
    expected = Mock()
    api.search.return_value = expected
    service = NyaaService(api)
    assert service.search("Mushoku Tensei", source="sukebei", page=3) is expected
    api.search.assert_called_once_with(
        "Mushoku Tensei", source="sukebei", category=None, sub_category=None,
        sort=None, order=None, page=3,
    )


def test_user_and_details_route_through_backend() -> None:
    api = Mock()
    service = NyaaService(api)
    service.search_user("Tsundere-Raws", "Mushoku Tensei")
    service.get_torrent(1234567, source="sukebei")
    api.user.assert_called_once()
    api.get.assert_called_once_with(1234567, source="sukebei")


def test_iterators_route_through_backend() -> None:
    api = Mock()
    service = NyaaService(api)
    service.iter_search("Anime", max_pages=2)
    service.iter_user("uploader", max_pages=3)
    api.iter_search.assert_called_once()
    api.iter_user.assert_called_once()


@pytest.mark.parametrize(
    ("error_type", "kind"),
    [(NyaaAPIRateLimitError, "rate_limit"), (NyaaAPINotFoundError, "not_found"),
     (NyaaAPIHTTPError, "http")],
)
def test_api_errors_are_safe_and_typed(error_type, kind: str) -> None:
    api = Mock()
    api.search.side_effect = error_type("raw details", status_code=429, endpoint="/nyaa")
    with pytest.raises(ServiceError) as captured:
        NyaaService(api).search("query")
    assert captured.value.kind == kind
    assert captured.value.status_code == 429
    assert "raw details" not in str(captured.value)
