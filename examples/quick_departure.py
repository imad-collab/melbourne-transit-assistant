import sys
import os
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.ptv_client import PTVClient
from config.credentials import DEV_ID, API_KEY


def quick_departure_check():
    """Quick check for departures from popular stations"""
    client = PTVClient(DEV_ID, API_KEY)
    
    # Popular stations (you can customize this)
    popular_stops = {
        '1': {'name': 'Flinders Street Station', 'stop_id': 1071, 'route_type': 0},
        '2': {'name': 'Southern Cross Station', 'stop_id': 1181, 'route_type': 0},
        '3': {'name': 'Melbourne Central Station', 'stop_id': 1120, 'route_type': 0},
        '4': {'name': 'Parliament Station', 'stop_id': 1155, 'route_type': 0},
    }
    
    print("Quick Departure Check\n" + "="*50)
    print("\nPopular Stations:")
    for key, info in popular_stops.items():
        print(f"{key}. {info['name']}")
    
    print("\nOr enter 'custom' to search for your own stop")
    
    choice = input("\nYour choice: ").strip().lower()
    
    if choice == 'custom':
        stop_id = input("Enter Stop ID: ")
        route_type = input("Enter Route Type (0=Train, 1=Tram, 2=Bus): ")
        try:
            stop_id = int(stop_id)
            route_type = int(route_type)
        except ValueError:
            print("Invalid input!")
            return
    elif choice in popular_stops:
        stop_id = popular_stops[choice]['stop_id']
        route_type = popular_stops[choice]['route_type']
        print(f"\nChecking departures from {popular_stops[choice]['name']}...")
    else:
        print("Invalid choice!")
        return
    
    try:
        departures = client.get_departures(route_type, stop_id, max_results=10)
        
        print(f"\n{'='*50}")
        print(f"Next Departures")
        print(f"{'='*50}\n")
        
        if departures.get('departures'):
            for i, dep in enumerate(departures['departures'], 1):
                platform = dep.get('platform_number', 'N/A')
                direction = dep.get('direction_id', 'N/A')
                
                # Parse and format time
                scheduled = dep.get('scheduled_departure_utc', '')
                if scheduled:
                    dt = datetime.fromisoformat(scheduled.replace('Z', '+00:00'))
                    time_str = dt.strftime('%I:%M %p')
                else:
                    time_str = 'N/A'
                
                print(f"{i}. Platform {platform} | {time_str}")
                print(f"   Direction ID: {direction}")
                
                # Show if there's real-time data
                if dep.get('estimated_departure_utc'):
                    print(f"   ⚡ Real-time tracking available")
                print()
        else:
            print("No departures found!")
            
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    quick_departure_check()
