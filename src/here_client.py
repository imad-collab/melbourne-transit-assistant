"""HERE Discover API client for finding parking locations."""
from __future__ import annotations

import logging
import random
from typing import List, Optional, Tuple

import requests

LOGGER = logging.getLogger(__name__)


class HEREParkingClient:
    """Wrapper around HERE Discover and Geocode APIs for parking location search."""

    DISCOVER_URL = "https://discover.search.hereapi.com/v1/discover"
    GEOCODE_URL = "https://geocode.search.hereapi.com/v1/geocode"

    def __init__(self, api_key: str, session: Optional[requests.Session] = None) -> None:
        if not api_key:
            raise ValueError("HERE API key is required")
        self.api_key = api_key
        self.session = session or requests.Session()

    def geocode_location(self, location: str, timeout: int = 10) -> Optional[Tuple[float, float]]:
        """Convert location name to coordinates (latitude, longitude).
        
        Returns tuple of (lat, lon) or None if not found.
        Biased to Melbourne, Australia region.
        """
        params = {
            "q": location,
            "apikey": self.api_key,
            "in": "countryCode:AUS",  # Restrict to Australia
            "limit": 10,  # Get more results to find the right one
        }

        LOGGER.debug("Geocoding location: %s (Australia)", location)

        try:
            response = self.session.get(
                self.GEOCODE_URL, params=params, timeout=timeout
            )
            response.raise_for_status()
            payload = response.json()

            items = payload.get("items", [])
            if not items:
                LOGGER.warning("No geocode results for: %s", location)
                return None

            # Try to find result in Victoria (Melbourne state) or use first result
            best_item = None
            for item in items:
                address = item.get("address", {})
                state = address.get("state", "")
                if "Victoria" in state or "VIC" in state or state == "VIC":
                    best_item = item
                    break
            
            # Fall back to first result if no Victoria match
            if not best_item:
                best_item = items[0]
            
            position = best_item.get("position", {})
            lat = position.get("lat")
            lon = position.get("lng")

            if lat and lon:
                address_label = best_item.get("address", {}).get("label", "")
                LOGGER.debug("Geocoded '%s' to (%.4f, %.4f) - %s", location, lat, lon, address_label)
                return (lat, lon)

            return None

        except requests.exceptions.RequestException as e:
            LOGGER.error("Geocoding failed: %s", e)
            raise

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

    def search_parking_by_location(
        self, location: str, limit: int = 5, timeout: int = 10
    ) -> List[dict]:
        """Search for parking near a named location (e.g., 'Southern Cross Station').
        
        Args:
            location: Name of location to search near
            limit: Maximum parking results to return
            timeout: Request timeout in seconds
            
        Returns:
            List of parking facilities near the location
        """
        LOGGER.info("Searching parking near: %s", location)

        # First, geocode the location to get coordinates
        coords = self.geocode_location(location, timeout=timeout)
        if not coords:
            raise ValueError(f"Could not find location: {location}")

        lat, lon = coords
        LOGGER.info("Found location at (%.4f, %.4f), searching for parking", lat, lon)

        # Now search for parking near those coordinates
        return self.search_parking_nearby(
            latitude=lat, longitude=lon, limit=limit, timeout=timeout
        )
