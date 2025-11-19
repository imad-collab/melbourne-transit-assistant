import sys
import os
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.ptv_client import PTVClient
from config.credentials import DEV_ID, API_KEY


def find_trams_to_state_library():
    """Find trams from Southern Cross to State Library after 7 PM"""
    client = PTVClient(DEV_ID, API_KEY)
    
    print("="*80)
    print("🚊 TRAMS: SOUTHERN CROSS STATION → STATE LIBRARY STATION")
    print("⏰ Departing AFTER 7:00 PM (19:00)")
    print("="*80)
    
    try:
        # Search for Southern Cross tram stops
        print("\n🔍 Step 1: Finding tram stops near Southern Cross...\n")
        southern_cross_stops = client.search_stops("Southern Cross", route_types=[1], max_results=10)
        
        if not southern_cross_stops.get('stops'):
            print("❌ No tram stops found near Southern Cross")
            return
        
        print(f"Found {len(southern_cross_stops['stops'])} tram stops:\n")
        for i, stop in enumerate(southern_cross_stops['stops'][:3], 1):
            print(f"{i}. {stop['stop_name']} (Stop ID: {stop['stop_id']})")
        
        # Use the main Collins St stop
        main_stop = southern_cross_stops['stops'][0]
        stop_id = main_stop['stop_id']
        stop_name = main_stop['stop_name']
        
        print(f"\n✅ Using: {stop_name}")
        
        # Search for State Library stops
        print("\n🔍 Step 2: Finding tram stops near State Library...\n")
        state_library_stops = client.search_stops("State Library", route_types=[1], max_results=10)
        
        if state_library_stops.get('stops'):
            print(f"Found {len(state_library_stops['stops'])} tram stops near State Library:\n")
            for i, stop in enumerate(state_library_stops['stops'][:5], 1):
                print(f"{i}. {stop['stop_name']} (Stop ID: {stop['stop_id']})")
        
        print("\n" + "="*80)
        
        # Get tram departures from Southern Cross
        print("\n⏳ Step 3: Fetching tram departures after 7 PM...\n")
        
        departures_data = client.get_departures(1, stop_id, max_results=100)
        
        if not departures_data.get('departures'):
            print("❌ No tram departures found!")
            return
        
        # Filter for trams after 7 PM
        after_7pm_trams = []
        target_hour = 19
        target_minute = 0
        
        for dep in departures_data['departures']:
            scheduled = dep.get('scheduled_departure_utc', '')
            
            if scheduled:
                try:
                    dt = datetime.fromisoformat(scheduled.replace('Z', '+00:00'))
                    
                    # Only get trams at or after 7:00 PM today
                    total_minutes = dt.hour * 60 + dt.minute
                    target_minutes = target_hour * 60 + target_minute
                    
                    if total_minutes >= target_minutes and dt.day == 19:
                        after_7pm_trams.append({
                            'datetime': dt,
                            'time_str': dt.strftime('%I:%M %p'),
                            'platform': dep.get('platform_number', 'N/A'),
                            'route_id': dep.get('route_id'),
                            'direction_id': dep.get('direction_id'),
                            'estimated': dep.get('estimated_departure_utc'),
                            'at_platform': dep.get('at_platform', False),
                            'mins_after': total_minutes - target_minutes
                        })
                except:
                    continue
        
        # Sort by time and get first 10
        after_7pm_trams.sort(key=lambda x: x['datetime'])
        first_10 = after_7pm_trams[:10]
        
        if not first_10:
            print("❌ No trams found after 7:00 PM")
            return
        
        print(f"📋 First 10 Trams After 7:00 PM:\n")
        print("="*80)
        
        for i, tram in enumerate(first_10, 1):
            if tram['mins_after'] == 0:
                marker = "⭐"
            elif tram['mins_after'] <= 10:
                marker = "✨"
            else:
                marker = "  "
            
            print(f"{marker} {i:2d}. 🚊 {tram['time_str']:8s} │ Platform: {str(tram['platform']):4s} │ Route: {tram['route_id']:4d} │ Direction: {tram['direction_id']:2d}")
        
        print("="*80)
        print("\n📝 ROUTE INFORMATION:")
        print("   State Library is on Swanston Street")
        print("   From Southern Cross (Collins St), take:")
        print("   • Any tram heading EAST along Collins St")
        print("   • Get off at Swanston St/Collins St or La Trobe St")
        print("   • Walk to State Library (1-2 min)")
        print("\n   🚊 Common routes: Tram 11, 12, 48, 96, 109")
        print("="*80)
        
        # Show closest train
        closest = first_10[0]
        print(f"\n🎯 NEXT TRAM: {closest['time_str']}")
        if closest['at_platform']:
            print("   🟢 TRAM IS AT PLATFORM NOW!")
        print()
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


def main():
    print("\n🚊 Tram Finder: Southern Cross → State Library\n")
    find_trams_to_state_library()


if __name__ == "__main__":
    main()
