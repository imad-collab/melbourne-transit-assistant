import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.ptv_client import PTVClient
from config.credentials import DEV_ID, API_KEY


def search_and_get_departures():
    """Search for a stop and get its departures"""
    client = PTVClient(DEV_ID, API_KEY)
    
    # Get user input
    stop_name = input("Enter the stop name to search for (e.g., 'Southern Cross'): ")
    
    print(f"\nSearching for '{stop_name}'...")
    results = client.search_stops(stop_name, max_results=10)
    
    if not results.get('stops'):
        print("No stops found!")
        return
    
    # Display the stops
    print(f"\nFound {len(results['stops'])} stops:\n")
    for i, stop in enumerate(results['stops'], 1):
        route_type = stop.get('route_type', 'Unknown')
        route_type_name = {0: 'Train', 1: 'Tram', 2: 'Bus', 3: 'V/Line', 4: 'Night Bus'}.get(route_type, 'Unknown')
        print(f"{i}. {stop['stop_name']} ({route_type_name})")
        print(f"   Stop ID: {stop['stop_id']}, Route Type: {route_type}")
    
    # Get user to select a stop
    choice = input(f"\nSelect a stop (1-{len(results['stops'])}): ")
    try:
        selected_stop = results['stops'][int(choice) - 1]
        stop_id = selected_stop['stop_id']
        route_type = selected_stop['route_type']
        
        print(f"\nGetting next departures from {selected_stop['stop_name']}...\n")
        departures = client.get_departures(route_type, stop_id, max_results=10)
        
        if departures.get('departures'):
            print(f"Next {len(departures['departures'])} departures:\n")
            for dep in departures['departures']:
                platform = dep.get('platform_number', 'N/A')
                direction = dep.get('direction_id', 'N/A')
                scheduled = dep.get('scheduled_departure_utc', 'N/A')
                print(f"  • Platform {platform}: Direction {direction}")
                print(f"    Scheduled: {scheduled}")
                if dep.get('estimated_departure_utc'):
                    print(f"    Estimated: {dep['estimated_departure_utc']}")
                print()
        else:
            print("No departures found!")
            
    except (ValueError, IndexError):
        print("Invalid selection!")


if __name__ == "__main__":
    search_and_get_departures()
