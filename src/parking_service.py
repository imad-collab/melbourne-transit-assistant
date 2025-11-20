"""High-level helpers for TomTom parking availability."""
from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Iterable, List, Optional, Sequence

from config.parking import CITY_PARKING_AREAS, TOMTOM_API_KEY, CityParkingArea

from .tomtom_client import TomTomParkingClient

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
    """Fetch parking availability for the configured area via TomTom."""

    normalised_key = area_key.lower()
    area = CITY_PARKING_AREAS.get(normalised_key)
    if not area:
        raise UnknownParkingAreaError(f"Unknown parking area: {area_key}")

    api_key = TOMTOM_API_KEY
    if not api_key:
        raise MissingApiKeyError(
            "TomTom API key missing. Set TOMTOM_API_KEY in your environment or .env file."
        )

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
