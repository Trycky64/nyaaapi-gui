from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass
from typing import Literal

from nyaaapi import (
    NyaaAPI,
    NyaaAPIError,
    NyaaAPIHTTPError,
    NyaaAPINotFoundError,
    NyaaAPIRateLimitError,
    NyaaAPIResponseError,
    NyaaAPITimeoutError,
    SearchResults,
    Torrent,
    TorrentDetails,
)

Source = Literal["nyaa", "sukebei"]


@dataclass(frozen=True, slots=True)
class ServiceError(Exception):
    """Safe-to-display representation of a backend API error."""

    kind: str
    message: str
    status_code: int | None = None
    endpoint: str | None = None

    def __str__(self) -> str:
        return self.message


def _friendly_error(error: NyaaAPIError) -> ServiceError:
    if isinstance(error, NyaaAPIRateLimitError):
        kind, message = "rate_limit", "The API is receiving too many requests. Try again shortly."
    elif isinstance(error, NyaaAPINotFoundError):
        kind, message = "not_found", "The requested torrent was not found."
    elif isinstance(error, NyaaAPITimeoutError):
        kind, message = "timeout", "The API request timed out. Check your connection and retry."
    elif isinstance(error, NyaaAPIResponseError):
        kind, message = "response", "The API returned a response the application could not read."
    elif isinstance(error, NyaaAPIHTTPError):
        kind, message = "http", "The API request failed. Please retry later."
    else:
        kind, message = "api", "The API request could not be completed."
    return ServiceError(kind, message, error.status_code, error.endpoint)


class NyaaService:
    """Application service that routes all remote requests through nyaaapi-client."""

    def __init__(self, api: NyaaAPI | None = None, *, timeout: float = 15.0) -> None:
        self._api = api or NyaaAPI(timeout=timeout)

    def close(self) -> None:
        """Release the backend HTTP session."""
        self._api.close()

    def __enter__(self) -> NyaaService:
        return self

    def __exit__(self, *_args: object) -> None:
        self.close()

    def search(
        self,
        query: str | None = None,
        *,
        source: Source = "nyaa",
        category: str | None = None,
        sub_category: str | None = None,
        sort: str | None = None,
        order: str | None = None,
        page: int = 1,
    ) -> SearchResults:
        """Search Nyaa or Sukebei and normalize backend exceptions."""
        try:
            return self._api.search(
                query,
                source=source,
                category=category,
                sub_category=sub_category,
                sort=sort,
                order=order,
                page=page,
            )
        except NyaaAPIError as error:
            raise _friendly_error(error) from error

    def search_user(
        self,
        user_name: str,
        query: str | None = None,
        *,
        source: Source = "nyaa",
        category: str | None = None,
        sub_category: str | None = None,
        sort: str | None = None,
        order: str | None = None,
        page: int = 1,
    ) -> SearchResults:
        """Search a user's uploads, optionally filtered by query."""
        try:
            return self._api.user(
                user_name,
                query,
                source=source,
                category=category,
                sub_category=sub_category,
                sort=sort,
                order=order,
                page=page,
            )
        except NyaaAPIError as error:
            raise _friendly_error(error) from error

    def get_torrent(self, torrent_id: int, *, source: Source = "nyaa") -> TorrentDetails:
        """Load full details for one torrent."""
        try:
            return self._api.get(torrent_id, source=source)
        except NyaaAPIError as error:
            raise _friendly_error(error) from error

    def iter_search(
        self,
        query: str | None = None,
        *,
        source: Source = "nyaa",
        max_pages: int | None = None,
        category: str | None = None,
        sub_category: str | None = None,
        sort: str | None = None,
        order: str | None = None,
    ) -> Iterator[Torrent]:
        """Iterate unique search results via the backend pagination helper."""
        try:
            return self._api.iter_search(
                query,
                source=source,
                max_pages=max_pages,
                category=category,
                sub_category=sub_category,
                sort=sort,
                order=order,
            )
        except NyaaAPIError as error:
            raise _friendly_error(error) from error

    def iter_user(
        self,
        user_name: str,
        query: str | None = None,
        *,
        source: Source = "nyaa",
        max_pages: int | None = None,
        category: str | None = None,
        sub_category: str | None = None,
        sort: str | None = None,
        order: str | None = None,
    ) -> Iterator[Torrent]:
        """Iterate unique uploads from one user via backend pagination."""
        try:
            return self._api.iter_user(
                user_name,
                query,
                source=source,
                max_pages=max_pages,
                category=category,
                sub_category=sub_category,
                sort=sort,
                order=order,
            )
        except NyaaAPIError as error:
            raise _friendly_error(error) from error
