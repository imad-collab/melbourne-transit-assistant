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
        STRICTLY filters to Victoria/Melbourne locations only using geographic bounds.
        Tries with Melbourne/Victoria appended if initial search fails.
        
        Melbourne CBD Center: -37.8136, 144.9631
        Victoria bounding box: lat [-39.2, -34.1], lon [141.0, 150.0]
        """
        # Melbourne CBD center for proximity bias
        melbourne_cbd_lat = -37.8136
        melbourne_cbd_lon = 144.9631
        
        # Victoria bounding box to validate results
        VICTORIA_BOUNDS = {
            "lat_min": -39.2,
            "lat_max": -34.1,
            "lon_min": 141.0,
            "lon_max": 150.0,
        }
        
        # Try both with and without Melbourne specification
        search_queries = [
            location,  # First try original location
            f"{location} Melbourne Victoria",  # Add Melbourne/Victoria if first fails
        ]
        
        for attempt, search_query in enumerate(search_queries, 1):
            params = {
                "q": search_query,
                "apikey": self.api_key,
                "in": "countryCode:AUS",  # Restrict to Australia
                "near": f"{melbourne_cbd_lat},{melbourne_cbd_lon}",  # Bias to Melbourne CBD
                "limit": 10,  # Get more results to find the right one
            }

            LOGGER.info(f"Geocoding attempt {attempt}: '{search_query}'")

            try:
                response = self.session.get(
                    self.GEOCODE_URL, params=params, timeout=timeout
                )
                response.raise_for_status()
                payload = response.json()

                items = payload.get("items", [])
                if not items:
                    LOGGER.debug(f"No results for '{search_query}'")
                    continue

                # STRICTLY filter for Victoria locations using geographic bounds
                victoria_items = []
                for item in items:
                    address = item.get("address", {})
                    state = address.get("state", "")
                    position = item.get("position", {})
                    lat = position.get("lat")
                    lon = position.get("lng")
                    label = address.get("label", "")
                    
                    # Primary check: within Victoria geographic bounds
                    is_within_bounds = (
                        lat and lon and
                        VICTORIA_BOUNDS["lat_min"] <= lat <= VICTORIA_BOUNDS["lat_max"] and
                        VICTORIA_BOUNDS["lon_min"] <= lon <= VICTORIA_BOUNDS["lon_max"]
                    )
                    
                    if is_within_bounds:
                        victoria_items.append(item)
                        LOGGER.debug(f"✓ Victoria: {label} ({lat:.4f}, {lon:.4f}) [{state}]")
                    else:
                        lat_str = f"{lat:.4f}" if lat else "0.0000"
                        lon_str = f"{lon:.4f}" if lon else "0.0000"
                        LOGGER.debug(f"✗ Non-Victoria: {label} ({lat_str}, {lon_str}) [{state}]")
                
                if not victoria_items:
                    LOGGER.debug(f"No Victoria results for '{search_query}' - trying next query")
                    continue
                
                LOGGER.info(f"✓ Found {len(victoria_items)} Victoria location(s)")
                
                # Prefer Melbourne city, then other Victoria locations
                best_item = None
                for item in victoria_items:
                    address = item.get("address", {})
                    city = address.get("city", "").lower()
                    if "melbourne" in city:
                        best_item = item
                        break
                
                # Use first Victoria result if no Melbourne match
                if not best_item:
                    best_item = victoria_items[0]
                
                position = best_item.get("position", {})
                lat = position.get("lat")
                lon = position.get("lng")

                if lat and lon:
                    address_label = best_item.get("address", {}).get("label", "")
                    state = best_item.get("address", {}).get("state", "")
                    LOGGER.info(f"✓ GEOCODED '{location}' → ({lat:.4f}, {lon:.4f}) in {state or 'Victoria'} - {address_label}")
                    return (lat, lon)

            except requests.exceptions.RequestException as e:
                LOGGER.error(f"Geocoding request failed for '{search_query}': {e}")
                continue
        
        # If we get here, no Victoria results found
        LOGGER.warning(f"❌ Could not find '{location}' in Victoria/Melbourne")
        return None

    def search_parking_nearby(
        self,
        latitude: float,
        longitude: float,
        limit: int = 10,
        timeout: int = 10,
    ) -> List[dict]:
        """Search for car parking locations near a given coordinate.
        
        Returns list of car parking facilities with:
        - title: Name of parking location
        - position: lat/lon coordinates
        - address: Full address
        - distance: Distance from search center (meters)
        
        Filters to show only car/auto parking, excluding motorcycles and bicycles.
        """

        params = {
            "at": f"{latitude},{longitude}",
            "q": "car parking",  # Search specifically for car parking
            "apikey": self.api_key,
            "limit": limit * 2,  # Get more results to compensate for filtering
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

            # Keywords to exclude (motorcycles, bicycles, scooters, etc.)
            exclude_keywords = [
                "motorcycle",
                "motorbike",
                "bike",
                "bicycle",
                "scooter",
                "two wheeler",
                "two-wheeler",
                "cycle",
                "bikes only",
                "motorcycles only",
            ]

            results: List[dict] = []
            for item in items:
                # Extract parking information
                title = item.get("title", "Unknown Parking")
                address = item.get("address", {})
                address_str = address.get("label", "Address unavailable")
                position = item.get("position", {})
                distance = item.get("distance", 0)

                # Filter: Exclude motorcycle/bicycle only parking
                combined_text = f"{title} {address_str}".lower()
                if any(keyword in combined_text for keyword in exclude_keywords):
                    LOGGER.debug("Skipping non-car parking: %s", title)
                    continue

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
                
                # Stop once we have enough car parking results
                if len(results) >= limit:
                    break

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
