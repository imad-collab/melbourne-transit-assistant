import sys
import os
from datetime import datetime
import json

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.ptv_client import PTVClient
from config.credentials import DEV_ID, API_KEY


def debug_vline_trains():
    """Debug V/Line trains to see ALL details"""
    client = PTVClient(DEV_ID, API_KEY)
    
    # Tarneit Railway Station - Stop ID: 1599, Route Type: 3 (V/Line)
    tarneit_stop_id = 1599
    route_type = 3  # V/Line
    
    print("="*80)
    print("🔍 DEBUGGING V/LINE TRAINS FROM TARNEIT")
    print("="*80)
    
    try:
        # Get V/Line departures with expanded data
        departures_data = client.get_departures(route_type, tarneit_stop_id, max_results=50, expand=["route", "run", "direction"])
        
        if not departures_data.get('departures'):
            print("\n❌ No V/Line departures found!")
            return
        
        # Get routes and directions
        routes = {r['route_id']: r for r in departures_data.get('routes', [])}
        directions = {d['direction_id']: d for d in departures_data.get('directions', [])}
        
        # Filter for trains after 7 PM today
        after_7pm = []
        
        for dep in departures_data['departures']:
            scheduled = dep.get('scheduled_departure_utc', '')
            estimated = dep.get('estimated_departure_utc')
            
            if scheduled:
                try:
                    dt_scheduled = datetime.fromisoformat(scheduled.replace('Z', '+00:00'))
                    
                    # Only today's trains after 7 PM
                    if dt_scheduled.day == 19 and dt_scheduled.month == 11 and dt_scheduled.hour >= 19:
                        
                        # Get estimated time if available
                        dt_estimated = None
                        if estimated:
                            try:
                                dt_estimated = datetime.fromisoformat(estimated.replace('Z', '+00:00'))
                            except:
                                pass
                        
                        route_id = dep.get('route_id')
                        direction_id = dep.get('direction_id')
                        
                        route_info = routes.get(route_id, {})
                        direction_info = directions.get(direction_id, {})
                        
                        after_7pm.append({
                            'scheduled_time': dt_scheduled,
                            'estimated_time': dt_estimated,
                            'scheduled_str': scheduled,
                            'estimated_str': estimated,
                            'platform': dep.get('platform_number'),
                            'direction_id': direction_id,
                            'direction_name': direction_info.get('direction_name', 'Unknown'),
                            'route_name': route_info.get('route_name', 'Unknown'),
                            'route_number': route_info.get('route_number', ''),
                            'flags': dep.get('flags', ''),
                            'run_ref': dep.get('run_ref', '')
                        })
                except:
                    continue
        
        # Sort by time
        after_7pm.sort(key=lambda x: x['estimated_time'] if x['estimated_time'] else x['scheduled_time'])
        
        print(f"\n📋 Found {len(after_7pm)} V/Line trains after 7 PM today\n")
        print("Showing first 10:\n")
        
        for i, train in enumerate(after_7pm[:10], 1):
            scheduled_str = train['scheduled_time'].strftime('%I:%M %p')
            
            print(f"{'='*80}")
            print(f"🚂 TRAIN #{i}")
            print(f"{'='*80}")
            
            if train['estimated_time']:
                estimated_str = train['estimated_time'].strftime('%I:%M %p')
                print(f"📅 Scheduled:  {scheduled_str}")
                print(f"⚡ ESTIMATED:  {estimated_str} ⭐ (Real-time update!)")
            else:
                print(f"📅 Departure:  {scheduled_str}")
            
            print(f"🚉 Platform:   {train['platform']}")
            print(f"📍 Direction:  {train['direction_name']} (ID: {train['direction_id']})")
            print(f"🚆 Route:      {train['route_name']}")
            
            if train['route_number']:
                print(f"🔢 Route #:    {train['route_number']}")
            
            print()
        
        print("="*80)
        print("💡 KEY INSIGHT:")
        print("   If ESTIMATED times are shown, those are the REAL-TIME updated times")
        print("   The PTV app shows ESTIMATED times, not scheduled times!")
        print("="*80)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    debug_vline_trains()
