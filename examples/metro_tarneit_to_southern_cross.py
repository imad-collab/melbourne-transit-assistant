import sys
import os
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.ptv_client import PTVClient
from config.credentials import DEV_ID, API_KEY


def find_metro_trains(target_hour=19, target_minute=0):
    """
    Find METRO trains from Tarneit to Southern Cross around a specific time
    
    Args:
        target_hour: Hour in 24h format (e.g., 19 for 7 PM)
        target_minute: Minute (e.g., 0 for sharp hour)
    """
    client = PTVClient(DEV_ID, API_KEY)
    
    # Tarneit Railway Station - Stop ID: 1071, Route Type: 0 (Metro)
    tarneit_stop_id = 1071
    route_type = 0  # Metro Trains
    
    print("="*80)
    print(f"🚇 METRO TRAINS: TARNEIT → SOUTHERN CROSS (Suburban Network)")
    print(f"⏰ Target Time: {target_hour:02d}:{target_minute:02d}")
    print("="*80)
    
    try:
        print("\n⏳ Fetching Metro train departures...")
        departures_data = client.get_departures(
            route_type, 
            tarneit_stop_id, 
            max_results=100
        )
        
        if not departures_data.get('departures'):
            print("\n❌ No Metro train departures found!")
            return
        
        # Filter trains around target time
        target_trains = []
        
        for dep in departures_data['departures']:
            scheduled = dep.get('scheduled_departure_utc', '')
            direction_id = dep.get('direction_id', 0)
            
            if scheduled:
                try:
                    dt = datetime.fromisoformat(scheduled.replace('Z', '+00:00'))
                    hour = dt.hour
                    minute = dt.minute
                    
                    # Find trains within 2 hours of target time
                    time_diff = abs((hour * 60 + minute) - (target_hour * 60 + target_minute))
                    
                    if time_diff <= 120:  # Within 2 hours
                        target_trains.append({
                            'datetime': dt,
                            'hour': hour,
                            'minute': minute,
                            'platform': dep.get('platform_number', 'TBA'),
                            'direction_id': direction_id,
                            'estimated': dep.get('estimated_departure_utc'),
                            'at_platform': dep.get('at_platform', False),
                            'flags': dep.get('flags', ''),
                            'time_diff': time_diff
                        })
                except Exception as e:
                    continue
        
        if not target_trains:
            print(f"\n❌ No Metro trains found around {target_hour:02d}:{target_minute:02d}")
            return
        
        # Sort by time
        target_trains.sort(key=lambda x: x['datetime'])
        
        print(f"\n✅ Found {len(target_trains)} Metro trains:\n")
        
        for i, train in enumerate(target_trains, 1):
            time_str = train['datetime'].strftime('%I:%M %p')
            date_str = train['datetime'].strftime('%a %d %b')
            
            # Highlight trains close to target time
            if train['time_diff'] <= 5:
                marker = "🎯 "
            elif train['time_diff'] <= 15:
                marker = "⭐ "
            elif train['time_diff'] <= 30:
                marker = "✨ "
            else:
                marker = "   "
            
            print(f"{marker}{'─'*76}")
            print(f"   TRAIN #{i}")
            print(f"   {'─'*76}")
            print(f"   🕐 Departure: {time_str} ({date_str})")
            print(f"   🚉 Platform: {train['platform']}")
            print(f"   📍 Direction ID: {train['direction_id']}")
            
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
            mins_diff = (train['hour'] * 60 + train['minute']) - (target_hour * 60 + target_minute)
            
            if train['time_diff'] == 0:
                print(f"   ⏱️  PERFECT! Exactly at {target_hour:02d}:{target_minute:02d}")
            elif train['time_diff'] <= 5:
                print(f"   ⏱️  EXCELLENT! ({train['time_diff']} min from target)")
            elif train['time_diff'] <= 15:
                if mins_diff < 0:
                    print(f"   ⏱️  Good option ({abs(mins_diff)} min before target)")
                else:
                    print(f"   ⏱️  Good option ({mins_diff} min after target)")
            else:
                if mins_diff < 0:
                    print(f"   ⏱️  {abs(mins_diff)} min before target time")
                else:
                    print(f"   ⏱️  {mins_diff} min after target time")
            
            print()
        
        # Find the best train
        closest_train = min(target_trains, key=lambda x: x['time_diff'])
        
        print("="*80)
        print("🎯 RECOMMENDED METRO TRAIN:")
        print(f"   Departure: {closest_train['datetime'].strftime('%I:%M %p')}")
        print(f"   Platform: {closest_train['platform']}")
        print(f"   Direction ID: {closest_train['direction_id']}")
        
        # Show trains before and after
        exact_time = target_hour * 60 + target_minute
        before = [t for t in target_trains if (t['hour'] * 60 + t['minute']) < exact_time]
        after = [t for t in target_trains if (t['hour'] * 60 + t['minute']) >= exact_time]
        
        if before:
            last_before = before[-1]
            print(f"\n   Last train before {target_hour:02d}:{target_minute:02d}: {last_before['datetime'].strftime('%I:%M %p')} (Platform {last_before['platform']})")
        
        if after:
            first_after = after[0]
            print(f"   First train at/after {target_hour:02d}:{target_minute:02d}: {first_after['datetime'].strftime('%I:%M %p')} (Platform {first_after['platform']})")
        
        print("="*80)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


def main():
    """Main function with customizable time"""
    print("\n🚇 Metro Train Finder: Tarneit → Southern Cross\n")
    
    # Customizable target time
    TARGET_HOUR = 19  # 7 PM in 24-hour format
    TARGET_MINUTE = 0  # Sharp hour
    
    find_metro_trains(TARGET_HOUR, TARGET_MINUTE)
    
    print("\n💡 TIP: Edit TARGET_HOUR and TARGET_MINUTE in the script")
    print("   to search for different departure times!")
    print("\n📝 Metro trains are the suburban network - more frequent services!")


if __name__ == "__main__":
    main()
