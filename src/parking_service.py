"""High-level helpers for TomTom parking availability with mock fallback."""
from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Iterable, List, Optional, Sequence

from config.parking import CITY_PARKING_AREAS, TOMTOM_API_KEY, CityParkingArea

from .tomtom_client import TomTomParkingClient
from .mock_parking import get_mock_parking

LOGGER = logging.getLogger(__name__)

DEFAULT_STATUS_FILTER: Sequence[str] = (
    "AVAILABLE",
    "LIMITED",
)
DEFAULT_LIMIT = 25


class ParkingServiceError(RuntimeError):
    """Base error raised by parking service helpers."""


class MissingApiKeyError(ParkingServiceError):
    """Raised when the TomTom API key is not configured."""


class UnknownParkingAreaError(ParkingServiceError):
    """Raised when a requested parking area key is unknown."""


@dataclass(frozen=True)
class ParkingAreaInfo:
    """Serializable representation of a parking area."""

    key: str
    display_name: str
    latitude: float
    longitude: float
    radius_m: int


def list_parking_areas() -> List[ParkingAreaInfo]:
    """Return known parking areas configured for TomTom."""

    return [
        ParkingAreaInfo(
            key=key,
            display_name=area.display_name,
            latitude=area.latitude,
            longitude=area.longitude,
            radius_m=area.radius_m,
        )
        for key, area in CITY_PARKING_AREAS.items()
    ]


def fetch_parking_availability(
    area_key: str,
    *,
    limit: int = DEFAULT_LIMIT,
    status_filter: Optional[Iterable[str]] = DEFAULT_STATUS_FILTER,
    timeout: int = 10,
) -> List[dict]:
    """Fetch parking availability for the configured area via TomTom.
    
    Falls back to mock data if TomTom API is unavailable or not configured.
    """

    normalised_key = area_key.lower()
    area = CITY_PARKING_AREAS.get(normalised_key)
    if not area:
        raise UnknownParkingAreaError(f"Unknown parking area: {area_key}")

    api_key = TOMTOM_API_KEY
    
    # Try real TomTom API if key is configured
    if api_key:
        try:
            LOGGER.debug(
                "Fetching TomTom parking availability for %s (lat=%s, lon=%s, radius=%s)",
                area.display_name,
                area.latitude,
                area.longitude,
                area.radius_m,
            )
            with TomTomParkingClient(api_key) as client:
                return client.get_within_circle(
                    latitude=area.latitude,
                    longitude=area.longitude,
                    radius_m=area.radius_m,
                    limit=limit,
                    status_filter=status_filter,
                    timeout=timeout,
                )
        except Exception as e:
            LOGGER.warning(
                "TomTom API failed (%s), falling back to mock data for %s",
                type(e).__name__,
                area.display_name,
            )
    else:
        LOGGER.info("No TomTom API key configured, using mock parking data for %s", area.display_name)
    
    # Fall back to mock data
    return get_mock_parking(normalised_key)[:limit]


__all__ = [
    "DEFAULT_LIMIT",
    "DEFAULT_STATUS_FILTER",
    "MissingApiKeyError",
    "ParkingAreaInfo",
    "ParkingServiceError",
    "UnknownParkingAreaError",
    "fetch_parking_availability",
    "list_parking_areas",
]
