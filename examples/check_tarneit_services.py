import sys
import os
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.ptv_client import PTVClient
from config.credentials import DEV_ID, API_KEY


def check_tarneit_services():
    """Check what types of train services run through Tarneit"""
    client = PTVClient(DEV_ID, API_KEY)
    
    print("="*80)
    print("🔍 CHECKING ALL TRAIN SERVICES AT TARNEIT STATION")
    print("="*80)
    
    # Check both Metro and V/Line
    services = {
        'Metro Train': {'route_type': 0, 'stop_id': 1071},  # Try metro
        'V/Line': {'route_type': 3, 'stop_id': 1599}         # V/Line
    }
    
    for service_name, info in services.items():
        print(f"\n{'='*80}")
        print(f"🚂 Checking {service_name} services...")
        print(f"{'='*80}")
        
        try:
            departures = client.get_departures(
                info['route_type'], 
                info['stop_id'], 
                max_results=10
            )
            
            if departures.get('departures'):
                print(f"\n✅ Found {len(departures['departures'])} {service_name} departures!")
                print(f"\nNext 5 departures:\n")
                
                for i, dep in enumerate(departures['departures'][:5], 1):
                    scheduled = dep.get('scheduled_departure_utc', '')
                    if scheduled:
                        try:
                            dt = datetime.fromisoformat(scheduled.replace('Z', '+00:00'))
                            time_str = dt.strftime('%I:%M %p')
                        except:
                            time_str = scheduled
                    else:
                        time_str = 'N/A'
                    
                    platform = dep.get('platform_number', 'N/A')
                    direction = dep.get('direction_id', 'N/A')
                    
                    print(f"   {i}. {time_str} - Platform {platform} - Direction {direction}")
            else:
                print(f"\n❌ No {service_name} services found at this stop")
                
        except Exception as e:
            print(f"\n⚠️  Error checking {service_name}: {e}")
    
    print("\n" + "="*80)
    print("📝 SUMMARY:")
    print("="*80)
    print("Tarneit Station is on the V/Line network (Geelong/Warrnambool line)")
    print("V/Line services connect Tarneit to Melbourne (Southern Cross)")
    print("\nRoute Type 0 = Metro Trains (Suburban)")
    print("Route Type 3 = V/Line (Regional)")
    print("="*80)


if __name__ == "__main__":
    check_tarneit_services()
