from __future__ import annotations

import os

import pytest
from nyaaapi import NyaaAPI

from nyaaapi_gui.services.nyaa_service import NyaaService


@pytest.mark.integration
def test_live_search_optional() -> None:
    if os.getenv("NYAAGUI_RUN_INTEGRATION") != "1":
        pytest.skip("Set NYAAGUI_RUN_INTEGRATION=1 to contact the unofficial API")
    with NyaaService(NyaaAPI(timeout=20)) as service:
        results = service.search("Mushoku Tensei")
    assert results.count >= 0
