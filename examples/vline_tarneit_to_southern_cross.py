import sys
import os
from datetime import datetime, timezone

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.ptv_client import PTVClient
from config.credentials import DEV_ID, API_KEY


def find_vline_trains(target_hour=19, target_minute=0):
    """
    Find V/Line trains from Tarneit to Southern Cross around a specific time
    
    Args:
        target_hour: Hour in 24h format (e.g., 19 for 7 PM)
        target_minute: Minute (e.g., 0 for sharp hour)
    """
    client = PTVClient(DEV_ID, API_KEY)
    
    # Tarneit Railway Station - Stop ID: 1599, Route Type: 3 (V/Line)
    tarneit_stop_id = 1599
    route_type = 3  # V/Line
    
    print("="*80)
    print(f"🚂 V/LINE TRAINS: TARNEIT → SOUTHERN CROSS")
    print(f"⏰ Target Time: {target_hour:02d}:{target_minute:02d}")
    print("="*80)
    
    try:
        # Get departures with expanded data (includes route and run info)
        print("\n⏳ Fetching V/Line departures...")
        departures_data = client.get_departures(
            route_type, 
            tarneit_stop_id, 
            max_results=50,
            expand=["route", "run", "direction"]
        )
        
        if not departures_data.get('departures'):
            print("\n❌ No V/Line departures found!")
            return
        
        # Extract routes and directions info
        routes = {r['route_id']: r for r in departures_data.get('routes', [])}
        directions = {d['direction_id']: d for d in departures_data.get('directions', [])}
        runs = {r['run_id']: r for r in departures_data.get('runs', [])}
        
        # Filter and organize trains
        target_trains = []
        
        for dep in departures_data['departures']:
            scheduled = dep.get('scheduled_departure_utc', '')
            direction_id = dep.get('direction_id', 0)
            route_id = dep.get('route_id')
            run_id = dep.get('run_id')
            
            if scheduled:
                try:
                    dt = datetime.fromisoformat(scheduled.replace('Z', '+00:00'))
                    hour = dt.hour
                    minute = dt.minute
                    
                    # Find trains within 3 hours of target time
                    time_diff = abs((hour * 60 + minute) - (target_hour * 60 + target_minute))
                    
                    if time_diff <= 180:  # Within 3 hours
                        # Get route and direction info
                        route_info = routes.get(route_id, {})
                        direction_info = directions.get(direction_id, {})
                        run_info = runs.get(run_id, {})
                        
                        route_name = route_info.get('route_name', 'Unknown Route')
                        direction_name = direction_info.get('direction_name', 'Unknown Direction')
                        
                        target_trains.append({
                            'datetime': dt,
                            'hour': hour,
                            'minute': minute,
                            'platform': dep.get('platform_number', 'TBA'),
                            'direction_id': direction_id,
                            'direction_name': direction_name,
                            'route_name': route_name,
                            'route_number': route_info.get('route_number', ''),
                            'estimated': dep.get('estimated_departure_utc'),
                            'at_platform': dep.get('at_platform', False),
                            'run_ref': dep.get('run_ref', 'N/A'),
                            'flags': dep.get('flags', ''),
                            'time_diff': time_diff
                        })
                except Exception as e:
                    continue
        
        if not target_trains:
            print(f"\n❌ No V/Line trains found around {target_hour:02d}:{target_minute:02d}")
            return
        
        # Sort by time
        target_trains.sort(key=lambda x: x['datetime'])
        
        # Filter for trains going towards Melbourne (usually direction name contains "City" or specific route)
        melbourne_trains = [t for t in target_trains if 
                           'Southern Cross' in t['direction_name'] or 
                           'Melbourne' in t['direction_name'] or
                           'City' in t['direction_name'] or
                           t['direction_id'] in [0, 10]]
        
        if melbourne_trains:
            trains_to_show = melbourne_trains
            print(f"\n✅ Found {len(trains_to_show)} V/Line trains towards Melbourne/Southern Cross:\n")
        else:
            trains_to_show = target_trains
            print(f"\n📋 Found {len(trains_to_show)} V/Line trains (showing all directions):\n")
        
        for i, train in enumerate(trains_to_show, 1):
            time_str = train['datetime'].strftime('%I:%M %p')
            date_str = train['datetime'].strftime('%a %d %b')
            
            # Highlight trains close to target time
            if train['time_diff'] <= 10:
                marker = "🎯 "
            elif train['time_diff'] <= 30:
                marker = "⭐ "
            else:
                marker = "   "
            
            print(f"{marker}{'='*76}")
            print(f"   TRAIN #{i} - {train['route_name']}")
            print(f"   {'='*76}")
            print(f"   🕐 Departure: {time_str} ({date_str})")
            print(f"   🚉 Platform: {train['platform']}")
            print(f"   📍 Direction: {train['direction_name']}")
            
            if train['route_number']:
                print(f"   🔢 Route: {train['route_number']}")
            
            if train['at_platform']:
                print(f"   🟢 *** TRAIN IS AT PLATFORM NOW! ***")
            
            if train['estimated']:
                try:
                    est_dt = datetime.fromisoformat(train['estimated'].replace('Z', '+00:00'))
                    est_time = est_dt.strftime('%I:%M %p')
                    if est_time != time_str:
                        print(f"   ⚡ Real-time: {est_time} (Updated)")
                except:
                    pass
            
            # Calculate time difference from target
            if train['time_diff'] == 0:
                print(f"   ⏱️  PERFECT TIMING! (Exactly at {target_hour:02d}:{target_minute:02d})")
            elif train['time_diff'] < 15:
                print(f"   ⏱️  Excellent timing! ({train['time_diff']} min from target)")
            elif train['time_diff'] < 30:
                print(f"   ⏱️  Good option ({train['time_diff']} min from target)")
            else:
                mins_before_after = (train['hour'] * 60 + train['minute']) - (target_hour * 60 + target_minute)
                if mins_before_after < 0:
                    print(f"   ⏱️  {abs(mins_before_after)} min before target time")
                else:
                    print(f"   ⏱️  {mins_before_after} min after target time")
            
            print()
        
        # Find the best train
        if trains_to_show:
            closest_train = min(trains_to_show, key=lambda x: x['time_diff'])
            
            print("="*80)
            print("🎯 RECOMMENDED V/LINE TRAIN:")
            print(f"   Route: {closest_train['route_name']}")
            print(f"   Departure: {closest_train['datetime'].strftime('%I:%M %p')}")
            print(f"   Platform: {closest_train['platform']}")
            print(f"   To: {closest_train['direction_name']}")
            print("="*80)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


def main():
    """Main function with customizable time"""
    print("\n🚂 V/Line Train Finder: Tarneit → Southern Cross\n")
    
    # Customizable target time
    TARGET_HOUR = 19  # 7 PM in 24-hour format
    TARGET_MINUTE = 0  # Sharp hour
    
    find_vline_trains(TARGET_HOUR, TARGET_MINUTE)
    
    print("\n💡 TIP: Edit TARGET_HOUR and TARGET_MINUTE in the script")
    print("   to search for different departure times!")
    print("\n📝 V/Line trains typically run on the Geelong and Warrnambool lines")
    print("   through Tarneit station.")


if __name__ == "__main__":
    main()
