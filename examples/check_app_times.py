import sys
import os
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.ptv_client import PTVClient
from config.credentials import DEV_ID, API_KEY


def check_705_708_737():
    """Check if 7:05 PM, 7:08 PM, 7:37 PM trains exist in Metro"""
    client = PTVClient(DEV_ID, API_KEY)
    
    print("="*80)
    print("🔍 CHECKING FOR TRAINS AT 7:05 PM, 7:08 PM, 7:37 PM")
    print("="*80)
    
    # Check both Metro and V/Line
    services = {
        'Metro (Route Type 0)': {'route_type': 0, 'stop_id': 1071},
        'V/Line (Route Type 3)': {'route_type': 3, 'stop_id': 1599}
    }
    
    target_times = ['19:05', '19:08', '19:37']  # 7:05 PM, 7:08 PM, 7:37 PM
    
    for service_name, info in services.items():
        print(f"\n{'='*80}")
        print(f"🚂 Checking {service_name}")
        print(f"{'='*80}\n")
        
        try:
            departures = client.get_departures(info['route_type'], info['stop_id'], max_results=100)
            
            found_trains = []
            
            for dep in departures.get('departures', []):
                scheduled = dep.get('scheduled_departure_utc', '')
                estimated = dep.get('estimated_departure_utc')
                
                if scheduled:
                    try:
                        dt = datetime.fromisoformat(scheduled.replace('Z', '+00:00'))
                        time_str = dt.strftime('%H:%M')
                        
                        # Check if this matches any target time
                        if time_str in target_times and dt.day == 19:
                            found_trains.append({
                                'time': dt.strftime('%I:%M %p'),
                                'scheduled': scheduled,
                                'estimated': estimated,
                                'platform': dep.get('platform_number', 'TBA'),
                                'direction': dep.get('direction_id')
                            })
                    except:
                        continue
            
            if found_trains:
                print(f"✅ FOUND {len(found_trains)} MATCHING TRAINS:\n")
                for train in found_trains:
                    print(f"   🚆 {train['time']}")
                    print(f"      Platform: {train['platform']}")
                    print(f"      Direction ID: {train['direction']}")
                    if train['estimated']:
                        print(f"      ⚡ Has real-time data")
                    print()
            else:
                print(f"❌ No trains found at 7:05 PM, 7:08 PM, or 7:37 PM\n")
                
        except Exception as e:
            print(f"⚠️  Error: {e}\n")
    
    print("="*80)
    print("💡 CONCLUSION:")
    print("   The trains you see in the PTV app might be:")
    print("   1. Metro trains (not V/Line)")
    print("   2. From a different date")
    print("   3. Real-time adjusted times")
    print("="*80)


if __name__ == "__main__":
    check_705_708_737()
