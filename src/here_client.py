"""HERE Discover API client for finding parking locations."""
from __future__ import annotations

import logging
from typing import List, Optional

import requests

LOGGER = logging.getLogger(__name__)


class HEREParkingClient:
    """Wrapper around HERE Discover API for parking location search."""

    DISCOVER_URL = "https://discover.search.hereapi.com/v1/discover"

    def __init__(self, api_key: str, session: Optional[requests.Session] = None) -> None:
        if not api_key:
            raise ValueError("HERE API key is required")
        self.api_key = api_key
        self.session = session or requests.Session()

    def search_parking_nearby(
        self,
        latitude: float,
        longitude: float,
        limit: int = 10,
        timeout: int = 10,
    ) -> List[dict]:
        """Search for parking locations near a given coordinate.
        
        Returns list of parking facilities with:
        - title: Name of parking location
        - position: lat/lon coordinates
        - address: Full address
        - distance: Distance from search center (meters)
        """

        params = {
            "at": f"{latitude},{longitude}",
            "q": "parking",
            "apikey": self.api_key,
            "limit": limit,
        }

        LOGGER.debug(
            "Searching HERE parking nearby (lat=%s, lon=%s, limit=%s)",
            latitude,
            longitude,
            limit,
        )

        try:
            response = self.session.get(
                self.DISCOVER_URL, params=params, timeout=timeout
            )
            response.raise_for_status()
            payload = response.json()

            items = payload.get("items", [])
            LOGGER.debug("Found %d parking items from HERE API", len(items))

            results: List[dict] = []
            for item in items:
                # Extract parking information
                title = item.get("title", "Unknown Parking")
                address = item.get("address", {})
                address_str = address.get("label", "Address unavailable")
                position = item.get("position", {})
                distance = item.get("distance", 0)

                results.append(
                    {
                        "name": title,
                        "address": address_str,
                        "latitude": position.get("lat"),
                        "longitude": position.get("lng"),
                        "distance": distance,
                        "status": "AVAILABLE",  # HERE doesn't provide real-time availability
                        "id": item.get("id", title.lower().replace(" ", "_")),
                    }
                )

            return results

        except requests.exceptions.HTTPError as e:
            LOGGER.error("HERE API HTTP error: %s", e)
            raise
        except requests.exceptions.RequestException as e:
            LOGGER.error("HERE API request failed: %s", e)
            raise
        except (KeyError, ValueError) as e:
            LOGGER.error("Failed to parse HERE API response: %s", e)
            raise
