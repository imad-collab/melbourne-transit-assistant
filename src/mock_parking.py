"""Mock parking data provider for testing without real TomTom API access."""
from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Dict, List


@dataclass
class MockParkingSpot:
    """A mock parking spot with realistic Melbourne data."""

    name: str
    address: str
    available: int
    total: int
    status: str  # AVAILABLE, LIMITED, FULL


# Melbourne CBD parking spots
MELBOURNE_CBD_SPOTS = [
    MockParkingSpot(
        name="Flinders Street Station Car Park",
        address="205 Flinders Street, Melbourne VIC 3000",
        available=random.randint(5, 45),
        total=120,
        status="AVAILABLE",
    ),
    MockParkingSpot(
        name="Melbourne Central Parking",
        address="300 Lonsdale Street, Melbourne VIC 3000",
        available=random.randint(2, 20),
        total=85,
        status="LIMITED",
    ),
    MockParkingSpot(
        name="Queen Victoria Market Car Park",
        address="Queen Victoria Market, Melbourne VIC 3000",
        available=random.randint(8, 60),
        total=150,
        status="AVAILABLE",
    ),
    MockParkingSpot(
        name="Southbank Parklands Car Park",
        address="100 St Kilda Road, Melbourne VIC 3052",
        available=random.randint(10, 40),
        total=200,
        status="AVAILABLE",
    ),
    MockParkingSpot(
        name="Melbourne Sports & Aquatic Centre",
        address="Swan Street, Melbourne VIC 3004",
        available=random.randint(20, 80),
        total=180,
        status="AVAILABLE",
    ),
    MockParkingSpot(
        name="Federation Square Car Park",
        address="Flinders Street, Melbourne VIC 3000",
        available=random.randint(1, 15),
        total=70,
        status="LIMITED",
    ),
    MockParkingSpot(
        name="GPO Car Park",
        address="350 Bourke Street, Melbourne VIC 3000",
        available=random.randint(3, 25),
        total=90,
        status="AVAILABLE",
    ),
    MockParkingSpot(
        name="Treasury Gardens Car Park",
        address="Spring Street, Melbourne VIC 3000",
        available=random.randint(5, 50),
        total=110,
        status="AVAILABLE",
    ),
    MockParkingSpot(
        name="Fitzroy Gardens Car Park",
        address="Fitzroy Gardens, Melbourne VIC 3004",
        available=random.randint(15, 70),
        total=140,
        status="AVAILABLE",
    ),
    MockParkingSpot(
        name="National Gallery of Victoria Car Park",
        address="180 St Kilda Road, Melbourne VIC 3004",
        available=random.randint(5, 35),
        total=100,
        status="AVAILABLE",
    ),
]

# Geelong CBD parking spots
GEELONG_CBD_SPOTS = [
    MockParkingSpot(
        name="Geelong Station Car Park",
        address="Gheringhap Street, Geelong VIC 3220",
        available=random.randint(10, 50),
        total=120,
        status="AVAILABLE",
    ),
    MockParkingSpot(
        name="Westfield Geelong Car Park",
        address="Malop Street, Geelong VIC 3220",
        available=random.randint(5, 40),
        total=200,
        status="AVAILABLE",
    ),
    MockParkingSpot(
        name="Geelong Library Car Park",
        address="Gheringhap Street, Geelong VIC 3220",
        available=random.randint(8, 30),
        total=80,
        status="AVAILABLE",
    ),
    MockParkingSpot(
        name="City Centre Car Park",
        address="Ryrie Street, Geelong VIC 3220",
        available=random.randint(2, 20),
        total=60,
        status="LIMITED",
    ),
    MockParkingSpot(
        name="Kardinia Park Sports Centre Car Park",
        address="Kardinia Park, Geelong VIC 3215",
        available=random.randint(20, 100),
        total=250,
        status="AVAILABLE",
    ),
]

PARKING_AREAS: Dict[str, List[MockParkingSpot]] = {
    "melbourne_cbd": MELBOURNE_CBD_SPOTS,
    "geelong_cbd": GEELONG_CBD_SPOTS,
}


def get_mock_parking(area_key: str) -> List[dict]:
    """Return mock parking data for the given area."""
    spots = PARKING_AREAS.get(area_key.lower())
    if not spots:
        return []

    # Convert to dict format matching TomTom response
    return [
        {
            "name": spot.name,
            "address": spot.address,
            "available": spot.available,
            "total": spot.total,
            "status": spot.status,
            "id": spot.name.lower().replace(" ", "_"),
        }
        for spot in spots
    ]
