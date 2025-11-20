"""Parking bay occupancy tracker with real-time status."""
from __future__ import annotations

import logging
from typing import List, Dict, Optional
from dataclasses import dataclass

LOGGER = logging.getLogger(__name__)


@dataclass
class ParkingBay:
    """Represents a single parking bay with occupancy status."""
    
    bay_id: str
    bay_number: int
    occupancy_status: str  # "Unoccupied", "Occupied", "Unknown"
    latitude: float
    longitude: float
    facility_name: str
    address: str
    
    def is_free(self) -> bool:
        """Check if bay is available."""
        return self.occupancy_status.lower() == "unoccupied"
    
    def get_emoji(self) -> str:
        """Get emoji based on occupancy status."""
        status_lower = self.occupancy_status.lower()
        if status_lower == "unoccupied":
            return "🟢"  # Green - available
        elif status_lower == "occupied":
            return "🔴"  # Red - occupied
        else:
            return "⚪"  # Gray - unknown


class BayOccupancyTracker:
    """Track and query parking bay occupancy."""
    
    def __init__(self, here_api_key: str):
        """Initialize with HERE API key for location data."""
        self.api_key = here_api_key
        # In production, this would connect to real bay sensors
        # For now, we'll simulate realistic data
        self.bays: Dict[str, List[ParkingBay]] = {}
    
    def simulate_bay_data(
        self, 
        location: str,
        latitude: float,
        longitude: float,
        num_bays: int = 6
    ) -> List[ParkingBay]:
        """Simulate parking bay occupancy data for a location.
        
        In production, this would connect to:
        - IoT parking sensors
        - Parking management APIs (EasyPark, ParkWhiz, etc.)
        - Smart city parking databases
        """
        import random
        
        bays = []
        for i in range(1, num_bays + 1):
            # Simulate occupancy: ~60% occupied, 30% free, 10% unknown
            rand = random.random()
            if rand < 0.60:
                status = "Occupied"
            elif rand < 0.90:
                status = "Unoccupied"
            else:
                status = "Unknown"
            
            bay = ParkingBay(
                bay_id=f"{location.replace(' ', '_').lower()}_bay_{i}",
                bay_number=i,
                occupancy_status=status,
                latitude=latitude + (random.random() - 0.5) * 0.001,  # Small variation
                longitude=longitude + (random.random() - 0.5) * 0.001,
                facility_name=f"{location} Parking",
                address=location
            )
            bays.append(bay)
        
        return bays
    
    def get_free_bays(
        self,
        location: str,
        latitude: float,
        longitude: float,
        limit: int = 10
    ) -> List[ParkingBay]:
        """Get list of free parking bays at location."""
        LOGGER.info(f"Fetching free bays for {location}")
        
        # Get bay data (simulated or from real API)
        all_bays = self.simulate_bay_data(location, latitude, longitude, num_bays=limit)
        
        # Filter to only free bays
        free_bays = [bay for bay in all_bays if bay.is_free()]
        
        LOGGER.info(f"Found {len(free_bays)} free bays at {location}")
        return free_bays
    
    def format_bay_list(
        self,
        location: str,
        free_bays: List[ParkingBay],
        all_bays: Optional[List[ParkingBay]] = None
    ) -> str:
        """Format bay list for Telegram display."""
        if not free_bays:
            return f"❌ No free parking bays found near {location}"
        
        lines = []
        lines.append(f"🅿️ FREE PARKING BAYS - {location}\n")
        lines.append(f"✅ Found {len(free_bays)} free bays\n")
        
        for i, bay in enumerate(free_bays, 1):
            lines.append(f"{i}. {bay.get_emoji()} Bay {bay.bay_number}")
            lines.append(f"   Status: {bay.occupancy_status}")
            lines.append(f"   📍 ({bay.latitude:.4f}, {bay.longitude:.4f})")
            lines.append("")  # Blank line
        
        if all_bays:
            occupied = len([b for b in all_bays if not b.is_free()])
            total = len(all_bays)
            lines.append(f"📊 Overall: {len(free_bays)}/{total} bays free ({occupied} occupied)")
        
        return "\n".join(lines)
    
    def format_bays_with_links(
        self,
        location: str,
        free_bays: List[ParkingBay]
    ) -> tuple[str, list]:
        """Format bays with Google Maps navigation links.
        
        Returns (formatted_text, keyboard_buttons)
        """
        text = self.format_bay_list(location, free_bays)
        
        # Create navigation buttons
        buttons = []
        for bay in free_bays:
            maps_url = f"https://www.google.com/maps/dir/?api=1&destination={bay.latitude},{bay.longitude}&travelmode=driving"
            button_text = f"🗺️ Bay {bay.bay_number} - Navigate"
            buttons.append({
                "text": button_text,
                "url": maps_url,
                "bay_number": bay.bay_number
            })
        
        return text, buttons


# Statistics and analytics
class BayStatistics:
    """Track parking bay statistics."""
    
    @staticmethod
    def get_occupancy_rate(bays: List[ParkingBay]) -> float:
        """Calculate occupancy percentage."""
        if not bays:
            return 0.0
        occupied = len([b for b in bays if not b.is_free()])
        return (occupied / len(bays)) * 100
    
    @staticmethod
    def get_peak_times(historical_data: Dict) -> str:
        """Get peak parking times (would use historical data)."""
        # In production: analyze historical occupancy patterns
        return "Rush hours: 8-9 AM, 12-1 PM, 5-6 PM"
    
    @staticmethod
    def get_availability_forecast(bays: List[ParkingBay]) -> str:
        """Forecast when bays will be available."""
        free_count = len([b for b in bays if b.is_free()])
        if free_count > len(bays) * 0.5:
            return "✅ Good availability - plenty of spots"
        elif free_count > len(bays) * 0.2:
            return "⚠️ Moderate availability - some spots available"
        else:
            return "❌ Poor availability - few spots left"
