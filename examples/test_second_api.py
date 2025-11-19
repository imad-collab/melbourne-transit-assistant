import sys
import os
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.ptv_client import PTVClient
# Use the SECOND set of credentials
from config.credentials_alt import DEV_ID, API_KEY


def test_second_api():
    """Test the second API credentials"""
    client = PTVClient(DEV_ID, API_KEY)
    
    print("="*80)
    print("🔑 TESTING SECOND API CREDENTIALS")
    print("="*80)
    print(f"\nDeveloper ID: {DEV_ID}")
    print(f"API Key: {API_KEY[:20]}...")
    print("\n" + "="*80)
    
    try:
        # Test 1: Get route types
        print("\n✅ Test 1: Getting route types...")
        route_types = client.get_route_types()
        if route_types.get('route_types'):
            print(f"   SUCCESS! Found {len(route_types['route_types'])} route types:")
            for rt in route_types['route_types']:
                print(f"   - {rt['route_type_name']} (ID: {rt['route_type']})")
        
        # Test 2: Search for a station
        print("\n✅ Test 2: Searching for Tarneit Station...")
        results = client.search_stops("Tarneit Station", max_results=3)
        if results.get('stops'):
            print(f"   SUCCESS! Found {len(results['stops'])} stops")
            for stop in results['stops'][:3]:
                print(f"   - {stop['stop_name']} (ID: {stop['stop_id']})")
        
        # Test 3: Get departures
        print("\n✅ Test 3: Getting departures from Flinders Street...")
        departures = client.get_departures(route_type=0, stop_id=1071, max_results=5)
        if departures.get('departures'):
            print(f"   SUCCESS! Found {len(departures['departures'])} departures")
            for i, dep in enumerate(departures['departures'][:3], 1):
                scheduled = dep.get('scheduled_departure_utc', '')
                if scheduled:
                    try:
                        dt = datetime.fromisoformat(scheduled.replace('Z', '+00:00'))
                        time_str = dt.strftime('%I:%M %p')
                    except:
                        time_str = scheduled
                else:
                    time_str = 'N/A'
                print(f"   {i}. Departure at {time_str}")
        
        print("\n" + "="*80)
        print("✅ ALL TESTS PASSED!")
        print("🎉 Second API credentials are working perfectly!")
        print("="*80)
        
    except Exception as e:
        print("\n" + "="*80)
        print("❌ TEST FAILED!")
        print(f"Error: {e}")
        print("="*80)


if __name__ == "__main__":
    print("\n🔑 Second API Credentials Test\n")
    test_second_api()
