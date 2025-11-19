import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.ptv_client import PTVClient
from config.credentials import DEV_ID, API_KEY


def find_stops_by_type():
    """Search for stops by transport type"""
    client = PTVClient(DEV_ID, API_KEY)
    
    print("Transport Types:")
    print("0 - Train")
    print("1 - Tram")
    print("2 - Bus")
    print("3 - V/Line")
    print("4 - Night Bus")
    
    transport_type = input("\nSelect transport type (0-4): ")
    location = input("Enter location/suburb name: ")
    
    try:
        route_types = [int(transport_type)]
        print(f"\nSearching for stops near '{location}'...")
        
        results = client.search_stops(location, route_types=route_types, max_results=15)
        
        if results.get('stops'):
            print(f"\nFound {len(results['stops'])} stops:\n")
            for stop in results['stops']:
                print(f"📍 {stop['stop_name']}")
                print(f"   Stop ID: {stop['stop_id']}")
                if stop.get('stop_suburb'):
                    print(f"   Suburb: {stop['stop_suburb']}")
                print()
        else:
            print("No stops found!")
            
    except ValueError:
        print("Invalid transport type!")


if __name__ == "__main__":
    find_stops_by_type()
