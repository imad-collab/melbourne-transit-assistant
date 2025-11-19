import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.ptv_client import PTVClient
from config.credentials import DEV_ID, API_KEY


def main():
    # Initialize the PTV client
    client = PTVClient(DEV_ID, API_KEY)
    
    print("Melbourne Transit Assistant\n" + "="*50)
    
    try:
        # Example 1: Get route types
        print("\n1. Getting route types...")
        route_types = client.get_route_types()
        print(f"Found {len(route_types['route_types'])} route types:")
        for rt in route_types['route_types']:
            print(f"  - {rt['route_type_name']} (ID: {rt['route_type']})")
        
        # Example 2: Search for stops
        print("\n2. Searching for 'Flinders Street' stops...")
        search_results = client.search_stops("Flinders Street", max_results=5)
        if search_results.get('stops'):
            print(f"Found {len(search_results['stops'])} stops:")
            for stop in search_results['stops'][:5]:
                print(f"  - {stop['stop_name']} (Stop ID: {stop['stop_id']})")
        
        # Example 3: Get departures (using Flinders Street Station as example)
        # Stop ID 1071 is Flinders Street Station
        print("\n3. Getting departures from Flinders Street Station...")
        departures = client.get_departures(route_type=0, stop_id=1071, max_results=5)
        print(f"Next {len(departures['departures'])} departures:")
        for dep in departures['departures'][:5]:
            print(f"  - Platform {dep.get('platform_number', 'N/A')}: "
                  f"{dep.get('direction_id', 'N/A')} at {dep.get('scheduled_departure_utc', 'N/A')}")
        
        print("\n" + "="*50)
        print("Demo completed successfully!")
        
    except Exception as e:
        print(f"\nError: {e}")
        print("\nMake sure you've set your API credentials in config/credentials.py")


if __name__ == "__main__":
    main()
