import sys
import os
from datetime import datetime, timezone

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.ptv_client import PTVClient
from config.credentials import DEV_ID, API_KEY


def find_trains_to_southern_cross(target_hour=19, target_minute=0):
    """
    Find trains from Tarneit to Southern Cross around a specific time
    
    Args:
        target_hour: Hour in 24h format (e.g., 19 for 7 PM)
        target_minute: Minute (e.g., 0 for sharp hour)
    """
    client = PTVClient(DEV_ID, API_KEY)
    
    # Tarneit Railway Station - Stop ID: 1599, Route Type: 3 (V/Line)
    tarneit_stop_id = 1599
    route_type = 3
    
    print("="*70)
    print(f"🚂 TRAINS FROM TARNEIT TO SOUTHERN CROSS")
    print(f"⏰ Target Time: {target_hour:02d}:{target_minute:02d}")
    print("="*70)
    
    try:
        # Get all departures from Tarneit
        departures = client.get_departures(route_type, tarneit_stop_id, max_results=50)
        
        if not departures.get('departures'):
            print("\n❌ No departures found!")
            return
        
        # Filter trains around target time and going towards Melbourne
        target_trains = []
        
        for dep in departures['departures']:
            scheduled = dep.get('scheduled_departure_utc', '')
            direction_id = dep.get('direction_id', 0)
            
            # Direction ID 10 or 0 typically means towards Melbourne/Southern Cross
            # You might need to adjust this based on actual API data
            if direction_id not in [0, 10]:
                continue
            
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
                            'platform': dep.get('platform_number', 'N/A'),
                            'direction_id': direction_id,
                            'estimated': dep.get('estimated_departure_utc'),
                            'at_platform': dep.get('at_platform', False),
                            'run_ref': dep.get('run_ref', 'N/A')
                        })
                except Exception as e:
                    continue
        
        if not target_trains:
            print(f"\n❌ No trains found around {target_hour:02d}:{target_minute:02d}")
            return
        
        # Sort by time
        target_trains.sort(key=lambda x: x['datetime'])
        
        print(f"\n📋 Found {len(target_trains)} trains towards Melbourne/Southern Cross:\n")
        
        for i, train in enumerate(target_trains, 1):
            time_str = train['datetime'].strftime('%I:%M %p')
            date_str = train['datetime'].strftime('%a %d %b')
            
            # Highlight trains close to target time
            time_diff = abs((train['hour'] * 60 + train['minute']) - (target_hour * 60 + target_minute))
            
            if time_diff <= 15:  # Within 15 minutes
                marker = "⭐ "
            elif time_diff <= 30:  # Within 30 minutes
                marker = "✨ "
            else:
                marker = "   "
            
            print(f"{marker}Train #{i}")
            print(f"   🕐 Departure: {time_str} ({date_str})")
            print(f"   🚉 Platform: {train['platform']}")
            
            if train['at_platform']:
                print(f"   🟢 Train is at platform NOW!")
            
            if train['estimated']:
                try:
                    est_dt = datetime.fromisoformat(train['estimated'].replace('Z', '+00:00'))
                    est_time = est_dt.strftime('%I:%M %p')
                    print(f"   ⚡ Real-time estimate: {est_time}")
                except:
                    pass
            
            # Calculate time difference from target
            time_diff_str = f"{time_diff} minutes"
            if time_diff < 15:
                print(f"   ⏱️  Perfect timing! ({time_diff_str} from target)")
            elif time_diff < 30:
                print(f"   ⏱️  Close to target ({time_diff_str} difference)")
            else:
                print(f"   ⏱️  {time_diff_str} from target time")
            
            print()
        
        # Find the closest train to target time
        closest_train = min(target_trains, 
                           key=lambda x: abs((x['hour'] * 60 + x['minute']) - 
                                           (target_hour * 60 + target_minute)))
        
        print("="*70)
        print("🎯 RECOMMENDED TRAIN:")
        print(f"   Departure: {closest_train['datetime'].strftime('%I:%M %p')}")
        print(f"   Platform: {closest_train['platform']}")
        print("="*70)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")


def main():
    """Main function with customizable time"""
    print("\n🚂 Tarneit to Southern Cross Train Finder\n")
    
    # You can change these values or make them interactive
    TARGET_HOUR = 19  # 7 PM in 24-hour format
    TARGET_MINUTE = 0  # Sharp hour
    
    find_trains_to_southern_cross(TARGET_HOUR, TARGET_MINUTE)
    
    print("\n💡 TIP: Edit the TARGET_HOUR and TARGET_MINUTE variables")
    print("   in this script to search for different times!")


if __name__ == "__main__":
    main()
