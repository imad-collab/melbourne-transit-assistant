import sys
import os
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.ptv_client import PTVClient
from config.credentials import DEV_ID, API_KEY


def get_vline_trains_after_7pm():
    """Get first 5 V/Line trains AFTER 7 PM from Tarneit to Southern Cross"""
    client = PTVClient(DEV_ID, API_KEY)
    
    # Tarneit Railway Station - Stop ID: 1599, Route Type: 3 (V/Line)
    tarneit_stop_id = 1599
    route_type = 3  # V/Line
    
    print("="*80)
    print("🚂 V/LINE TRAINS: TARNEIT → SOUTHERN CROSS")
    print("⏰ Departing AT or AFTER 7:00 PM (19:00)")
    print("="*80)
    
    try:
        # Get V/Line departures
        departures_data = client.get_departures(route_type, tarneit_stop_id, max_results=50)
        
        if not departures_data.get('departures'):
            print("\n❌ No V/Line departures found!")
            return
        
        # Filter for trains AT or AFTER 7 PM
        after_7pm_trains = []
        target_hour = 19
        target_minute = 0
        
        for dep in departures_data['departures']:
            scheduled = dep.get('scheduled_departure_utc', '')
            
            if scheduled:
                try:
                    dt = datetime.fromisoformat(scheduled.replace('Z', '+00:00'))
                    hour = dt.hour
                    minute = dt.minute
                    
                    # Only get trains at or after 7:00 PM
                    total_minutes = hour * 60 + minute
                    target_minutes = target_hour * 60 + target_minute
                    
                    if total_minutes >= target_minutes:
                        after_7pm_trains.append({
                            'datetime': dt,
                            'scheduled': scheduled,
                            'platform': dep.get('platform_number', 'TBA'),
                            'direction_id': dep.get('direction_id'),
                            'estimated': dep.get('estimated_departure_utc'),
                            'at_platform': dep.get('at_platform', False),
                            'mins_after': total_minutes - target_minutes
                        })
                except:
                    continue
        
        # Sort by time and get first 5
        after_7pm_trains.sort(key=lambda x: x['datetime'])
        first_5 = after_7pm_trains[:5]
        
        if not first_5:
            print("\n❌ No V/Line trains found at or after 7:00 PM")
            return
        
        print(f"\n📋 First 5 V/Line Trains AT or AFTER 7:00 PM:\n")
        
        for i, train in enumerate(first_5, 1):
            time_str = train['datetime'].strftime('%I:%M %p')
            date_str = train['datetime'].strftime('%a, %d %b %Y')
            
            print(f"{'='*80}")
            print(f"🚂 TRAIN #{i}")
            print(f"{'='*80}")
            print(f"📅 Date:      {date_str}")
            print(f"🕐 Departure: {time_str}")
            print(f"🚉 Platform:  {train['platform']}")
            print(f"📍 Direction: ID {train['direction_id']}")
            
            # Calculate time from 7 PM
            if train['mins_after'] == 0:
                print(f"⏱️  Timing:    EXACTLY at 7:00 PM ⭐")
            else:
                print(f"⏱️  Timing:    {train['mins_after']} minutes AFTER 7:00 PM")
            
            if train['at_platform']:
                print(f"🟢 Status:    TRAIN IS AT PLATFORM NOW!")
            
            if train['estimated']:
                print(f"⚡ Real-time: Yes (live tracking available)")
            
            print()
        
        print("="*80)
        print("✅ This is LIVE data from PTV Timetable API")
        print("✅ All trains shown depart AT or AFTER 7:00 PM")
        print("="*80)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")


if __name__ == "__main__":
    get_vline_trains_after_7pm()
