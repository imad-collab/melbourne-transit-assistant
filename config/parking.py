"""Configuration helpers for parking integrations (TomTom and HERE)."""
from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Dict

from dotenv import load_dotenv

# Load environment variables from a local .env if present
load_dotenv()

TOMTOM_API_KEY = os.getenv("TOMTOM_API_KEY", "")
HERE_API_KEY = os.getenv("HERE_API_KEY", "")


@dataclass(frozen=True)
class CityParkingArea:
    """Represents a named parking search area for TomTom API queries."""

    display_name: str
    latitude: float
    longitude: float
    radius_m: int


CITY_PARKING_AREAS: Dict[str, CityParkingArea] = {
    "melbourne_cbd": CityParkingArea(
        display_name="Melbourne CBD",
        latitude=-37.8167,
        longitude=144.9570,
        radius_m=1500,
    ),
    "geelong_cbd": CityParkingArea(
        display_name="Geelong CBD",
        latitude=-38.1499,
        longitude=144.3617,
        radius_m=1300,
    ),
}
