"""Client wrapper for TomTom Parking Availability API."""
from __future__ import annotations

import logging
import math
from datetime import datetime, timezone
from typing import Iterable, List, Optional

import requests

LOGGER = logging.getLogger(__name__)


class TomTomParkingClient:
    """Simple wrapper around TomTom's parking availability endpoints."""

    WITHIN_CIRCLE_URL = "https://api.tomtom.com/parking/1/availability/withinCircle.json"

    def __init__(self, api_key: str, session: Optional[requests.Session] = None) -> None:
        if not api_key:
            raise ValueError("TomTom API key is required")
        self.api_key = api_key
        self.session = session or requests.Session()

    def get_within_circle(
        self,
        latitude: float,
        longitude: float,
        radius_m: int,
        limit: int = 50,
        status_filter: Optional[Iterable[str]] = None,
        timeout: int = 10,
    ) -> List[dict]:
        """Return parking availability within a circle centred at the given location."""

        params = {
            "key": self.api_key,
            "center": f"{latitude:.6f},{longitude:.6f}",
            "radius": int(radius_m),
            "limit": limit,
        }
        LOGGER.debug("Requesting TomTom availability: %s", params)
        response = self.session.get(self.WITHIN_CIRCLE_URL, params=params, timeout=timeout)
        response.raise_for_status()
        payload = response.json()
        parking_list = payload.get("parkingList", [])

        results: List[dict] = []
        for entry in parking_list:
            occupancy = entry.get("occupancy", {})
            status = occupancy.get("status") or entry.get("occupancyStatus")

            if status_filter and status and status not in status_filter:
                continue

            available = self._first_of(
                occupancy.get("availableCapacity"), entry.get("availableCapacity")
            )
            total = self._first_of(occupancy.get("totalCapacity"), entry.get("totalCapacity"))

            last_updated_raw = self._first_of(
                occupancy.get("lastUpdated"),
                entry.get("lastUpdated"),
            )
            last_updated = self._parse_timestamp(last_updated_raw)

            position = entry.get("position", {})
            address = entry.get("address", {})

            results.append(
                {
                    "id": entry.get("id"),
                    "name": entry.get("name"),
                    "address": self._format_address(address),
                    "latitude": position.get("latitude") or position.get("lat"),
                    "longitude": position.get("longitude") or position.get("lon"),
                    "status": status,
                    "available": available,
                    "total": total,
                    "occupancy_percentage": occupancy.get("percentage")
                    or entry.get("occupancyPercentage"),
                    "last_updated": last_updated,
                }
            )

        # Sort by availability (descending) then by latest update
        results.sort(
            key=lambda item: (
                self._sortable_available(item.get("available")),
                self._sortable_timestamp(item.get("last_updated")),
            ),
            reverse=True,
        )
        return results

    @staticmethod
    def _first_of(*values):
        for value in values:
            if value is not None:
                return value
        return None

    @staticmethod
    def _parse_timestamp(timestamp: Optional[str]) -> Optional[datetime]:
        if not timestamp:
            return None
        try:
            if timestamp.endswith("Z"):
                return datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
            return datetime.fromisoformat(timestamp)
        except ValueError:
            LOGGER.debug("Unable to parse timestamp from TomTom response: %s", timestamp)
            return None

    @staticmethod
    def _format_address(address: dict) -> Optional[str]:
        if not address:
            return None
        parts = [
            address.get("streetName"),
            address.get("streetNumber"),
            address.get("municipality"),
        ]
        formatted = " ".join(part for part in parts if part)
        return formatted or address.get("freeformAddress")

    @staticmethod
    def _sortable_available(value: Optional[int]) -> float:
        if value is None:
            return -math.inf
        return float(value)

    @staticmethod
    def _sortable_timestamp(value: Optional[datetime]) -> float:
        if not value:
            return -math.inf
        if value.tzinfo is None:
            value = value.replace(tzinfo=timezone.utc)
        return value.timestamp()

    def close(self) -> None:
        self.session.close()

    def __enter__(self) -> "TomTomParkingClient":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()
