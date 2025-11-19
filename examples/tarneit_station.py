import sys
import os
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.ptv_client import PTVClient
from config.credentials import DEV_ID, API_KEY


def tarneit_departures():
    """Get departures from Tarneit Railway Station"""
    client = PTVClient(DEV_ID, API_KEY)
    
    # Tarneit Railway Station - Stop ID: 1599, Route Type: 3 (V/Line)
    stop_id = 1599
    route_type = 3
    
    print("🚂 TARNEIT RAILWAY STATION - Next Departures")
    print("="*60)
    
    try:
        departures = client.get_departures(route_type, stop_id, max_results=15)
        
        if departures.get('departures'):
            print(f"\nShowing next {len(departures['departures'])} trains:\n")
            
            for i, dep in enumerate(departures['departures'], 1):
                platform = dep.get('platform_number', 'N/A')
                direction = dep.get('direction_id', 'Unknown')
                
                # Parse scheduled time
                scheduled = dep.get('scheduled_departure_utc', '')
                if scheduled:
                    try:
                        dt = datetime.fromisoformat(scheduled.replace('Z', '+00:00'))
                        time_str = dt.strftime('%I:%M %p')
                        date_str = dt.strftime('%a %d %b')
                    except:
                        time_str = scheduled
                        date_str = ''
                else:
                    time_str = 'N/A'
                    date_str = ''
                
                print(f"🚆 Train #{i}")
                print(f"   Platform: {platform}")
                print(f"   Time: {time_str} ({date_str})")
                print(f"   Direction ID: {direction}")
                
                # Check for real-time data
                if dep.get('estimated_departure_utc'):
                    print(f"   ⚡ Real-time tracking available")
                
                # Check for delays
                if dep.get('at_platform'):
                    print(f"   🟢 Train is at platform")
                
                print()
        else:
            print("\n❌ No departures found!")
            print("This might mean:")
            print("- No trains scheduled for this time")
            print("- The station might not have V/Line services at this hour")
            
    except Exception as e:
        print(f"\n❌ Error: {e}")


if __name__ == "__main__":
    tarneit_departures()
