import sys
import os
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.ptv_client import PTVClient
from config.credentials import DEV_ID, API_KEY


def find_trams_to_docklands():
    """Find trams from Southern Cross to Docklands Library after 7 PM"""
    client = PTVClient(DEV_ID, API_KEY)
    
    print("="*80)
    print("🚊 TRAMS: SOUTHERN CROSS → DOCKLANDS LIBRARY")
    print("⏰ Departing AFTER 7:00 PM (19:00)")
    print("="*80)
    
    try:
        # First, search for Southern Cross tram stops
        print("\n🔍 Searching for tram stops near Southern Cross...\n")
        southern_cross_stops = client.search_stops("Southern Cross", route_types=[1], max_results=20)
        
        if southern_cross_stops.get('stops'):
            print(f"Found {len(southern_cross_stops['stops'])} tram stops near Southern Cross:\n")
            for i, stop in enumerate(southern_cross_stops['stops'][:5], 1):
                print(f"{i}. {stop['stop_name']} (Stop ID: {stop['stop_id']})")
            
            # Use the first one (usually the main stop)
            main_stop = southern_cross_stops['stops'][0]
            stop_id = main_stop['stop_id']
            stop_name = main_stop['stop_name']
            
            print(f"\n✅ Using: {stop_name} (ID: {stop_id})")
            print("="*80)
            
            # Get tram departures
            print("\n⏳ Fetching tram departures after 7 PM...\n")
            
            # Route Type 1 = Tram
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
                        hour = dt.hour
                        minute = dt.minute
                        
                        # Only get trams at or after 7:00 PM today
                        total_minutes = hour * 60 + minute
                        target_minutes = target_hour * 60 + target_minute
                        
                        if total_minutes >= target_minutes and dt.day == 19:
                            after_7pm_trams.append({
                                'datetime': dt,
                                'platform': dep.get('platform_number', 'TBA'),
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
            
            for i, tram in enumerate(first_10, 1):
                time_str = tram['datetime'].strftime('%I:%M %p')
                
                print(f"{'─'*76}")
                print(f"🚊 TRAM #{i}")
                print(f"{'─'*76}")
                print(f"🕐 Departure:  {time_str}")
                print(f"🚉 Platform:   {tram['platform']}")
                print(f"🔢 Route ID:   {tram['route_id']}")
                print(f"📍 Direction:  ID {tram['direction_id']}")
                
                if tram['mins_after'] == 0:
                    print(f"⏱️  Timing:     EXACTLY at 7:00 PM ⭐")
                else:
                    print(f"⏱️  Timing:     {tram['mins_after']} minutes after 7:00 PM")
                
                if tram['at_platform']:
                    print(f"🟢 Status:     TRAM IS AT PLATFORM NOW!")
                
                print()
            
            print("="*80)
            print("📝 NOTE: Docklands is very close to Southern Cross")
            print("   You can walk to Docklands Library in about 10-15 minutes!")
            print("   Or take tram route 11, 30, 35, or 48 towards Docklands")
            print("="*80)
            
        else:
            print("❌ No tram stops found near Southern Cross")
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


def search_docklands_library():
    """Also search for stops near Docklands Library"""
    client = PTVClient(DEV_ID, API_KEY)
    
    print("\n" + "="*80)
    print("📚 SEARCHING FOR STOPS NEAR DOCKLANDS LIBRARY")
    print("="*80)
    
    try:
        docklands_stops = client.search_stops("Docklands", route_types=[1], max_results=10)
        
        if docklands_stops.get('stops'):
            print(f"\nFound {len(docklands_stops['stops'])} tram stops near Docklands:\n")
            for i, stop in enumerate(docklands_stops['stops'], 1):
                print(f"{i}. {stop['stop_name']} (Stop ID: {stop['stop_id']})")
            print()
        else:
            print("\n❌ No stops found near Docklands")
            
    except Exception as e:
        print(f"\n❌ Error: {e}")


def main():
    print("\n🚊 Southern Cross to Docklands Library - Tram Finder\n")
    find_trams_to_docklands()
    search_docklands_library()


if __name__ == "__main__":
    main()
