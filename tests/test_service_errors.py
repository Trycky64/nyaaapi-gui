from __future__ import annotations

from unittest.mock import Mock

import pytest
from nyaaapi import NyaaAPIResponseError, NyaaAPITimeoutError

from nyaaapi_gui.services.nyaa_service import NyaaService, ServiceError


@pytest.mark.parametrize(
    ("backend_error", "kind"),
    [
        (NyaaAPITimeoutError("late", endpoint="/nyaa"), "timeout"),
        (NyaaAPIResponseError("bad JSON", endpoint="/nyaa"), "response"),
    ],
)
def test_timeout_and_response_errors_are_mapped(backend_error, kind: str) -> None:
    api = Mock()
    api.search.side_effect = backend_error
    with pytest.raises(ServiceError) as caught:
        NyaaService(api).search("Show")
    assert caught.value.kind == kind
    assert caught.value.endpoint == "/nyaa"
