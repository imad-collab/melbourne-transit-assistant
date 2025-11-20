"""
Melbourne Transit Assistant - Comprehensive Usage Example

This script demonstrates how to use the Melbourne Transit Assistant library
to query departures, search stops, and check real-time parking availability.

Run this script to see practical examples of all major features.
"""

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.ptv_client import PTVClient
from src.parking_service import (
    fetch_parking_availability,
    list_parking_areas,
    MissingApiKeyError,
    UnknownParkingAreaError,
)
from config.credentials import DEV_ID, API_KEY


def print_section(title):
    """Print a formatted section header."""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60 + "\n")


def example_1_search_stops():
    """Example 1: Search for transit stops by name."""
    print_section("Example 1: Search for Transit Stops")
    
    client = PTVClient(DEV_ID, API_KEY)
    
    # Search for "Flinders Street"
    print("Searching for stops matching 'Flinders Street'...\n")
    result = client.search_stops("Flinders Street", max_results=5)
    
    if result.get("stops"):
        for stop in result["stops"][:5]:
            stop_id = stop.get("stop_id")
            stop_name = stop.get("stop_name")
            routes = stop.get("routes", [])
            route_types = [r.get("route_type_name") for r in routes if r.get("route_type_name")]
            print(f"  Stop ID: {stop_id}")
            print(f"  Name: {stop_name}")
            if route_types:
                print(f"  Available routes: {', '.join(set(route_types))}")
            print()
    else:
        print("  No stops found.")


def example_2_departures():
    """Example 2: Get upcoming departures from a stop."""
    print_section("Example 2: Upcoming Departures from a Stop")
    
    client = PTVClient(DEV_ID, API_KEY)
    
    # Flinders Street Station (stop ID 1071, route type 0 = train)
    stop_id = 1071
    route_type = 0
    
    print(f"Getting next 5 departures from Flinders Street (Stop ID {stop_id})...\n")
    
    result = client.get_departures(
        route_type=route_type,
        stop_id=stop_id,
        max_results=5,
        expand=["run", "route", "stop"],
    )
    
    departures = result.get("departures", [])
    
    if departures:
        for i, dep in enumerate(departures, 1):
            run_id = dep.get("run_id")
            route_id = dep.get("route_id")
            scheduled = dep.get("scheduled_departure_utc")
            estimated = dep.get("estimated_departure_utc")
            platform = dep.get("platform_number")
            
            # Parse timestamps
            time_display = estimated or scheduled or "TBA"
            if time_display and "T" in time_display:
                time_display = time_display.split("T")[1].split("+")[0]
            
            print(f"  {i}. Run {run_id} (Route {route_id})")
            print(f"     Departure: {time_display}")
            if platform:
                print(f"     Platform: {platform}")
            print()
    else:
        print("  No departures found.")


def example_3_route_info():
    """Example 3: Get information about a specific route."""
    print_section("Example 3: Route Information")
    
    client = PTVClient(DEV_ID, API_KEY)
    
    print("Fetching route information for route ID 1 (typically a major train line)...\n")
    
    result = client.get_route_info(route_id=1)
    
    if result.get("route"):
        route = result["route"]
        print(f"  Route ID: {route.get('route_id')}")
        print(f"  Route Name: {route.get('route_name')}")
        print(f"  Route Type: {route.get('route_type_name')}")
        print(f"  Status: {route.get('status')}")
    else:
        print("  Route not found.")


def example_4_parking_availability():
    """Example 4: Check real-time parking availability."""
    print_section("Example 4: Real-Time Parking Availability")
    
    # First, show available parking areas
    print("Available parking areas:\n")
    areas = list_parking_areas()
    for area in areas:
        print(f"  • {area.key}: {area.display_name} (search radius {area.radius_m}m)")
    
    print("\nFetching parking availability for Melbourne CBD...\n")
    
    try:
        availability = fetch_parking_availability("melbourne_cbd", limit=5)
        
        if availability:
            print(f"Found {len(availability)} parking locations:\n")
            for i, item in enumerate(availability, 1):
                name = item.get("name") or item.get("id") or "Unnamed"
                status = item.get("status") or "UNKNOWN"
                available = item.get("available")
                total = item.get("total")
                address = item.get("address") or "Address unavailable"
                
                print(f"  {i}. {name}")
                print(f"     Status: {status}")
                print(f"     Available: {available}/{total} bays")
                print(f"     Address: {address}")
                print()
        else:
            print("  No parking locations returned.")
    
    except UnknownParkingAreaError as e:
        print(f"  Error: {e}")
    except MissingApiKeyError as e:
        print(f"  Note: {e}")
        print("  (Set TOMTOM_API_KEY environment variable to enable parking queries)")


def example_5_stop_types():
    """Example 5: Show available route types."""
    print_section("Example 5: Available Route Types")
    
    client = PTVClient(DEV_ID, API_KEY)
    
    print("Fetching available route types...\n")
    
    result = client.get_route_types()
    
    if result.get("route_types"):
        for rt in result["route_types"]:
            route_type_id = rt.get("route_type_id")
            route_type_name = rt.get("route_type_name")
            print(f"  {route_type_id}: {route_type_name}")
    else:
        print("  No route types found.")


def main():
    """Run all examples."""
    print("\n" + "🚆" * 30)
    print("Melbourne Transit Assistant - Usage Examples")
    print("🚆" * 30)
    
    try:
        example_1_search_stops()
        example_2_departures()
        example_3_route_info()
        example_4_parking_availability()
        example_5_stop_types()
        
        print_section("Summary")
        print("✅ All examples completed successfully!")
        print("""
Key takeaways:
  • Use PTVClient to query transit data (routes, stops, departures)
  • Use parking_service helpers to check real-time parking availability
  • Set TOMTOM_API_KEY environment variable to enable parking features
  • Refer to the README for Telegram bot command examples
        """)
        
    except Exception as e:
        print(f"\n❌ Error during execution: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
