import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.ptv_client import PTVClient
from config.credentials import DEV_ID, API_KEY


def get_tram_route_details():
    """Get details of tram routes to map Route IDs to tram numbers"""
    client = PTVClient(DEV_ID, API_KEY)
    
    print("="*80)
    print("🔍 MAPPING TRAM ROUTE IDs TO TRAM NUMBERS")
    print("="*80)
    
    try:
        # Get all tram routes (Route Type 1 = Tram)
        print("\n⏳ Fetching all tram routes...\n")
        routes_data = client.get_routes(route_types=[1])
        
        if not routes_data.get('routes'):
            print("❌ No tram routes found!")
            return
        
        routes = routes_data['routes']
        print(f"Found {len(routes)} tram routes!\n")
        
        # Look for specific tram numbers
        target_trams = ['11', '12', '48', '96']
        target_route_ids = [3343, 2903]
        
        print("="*80)
        print("🚊 TRAM ROUTES YOU'RE INTERESTED IN:")
        print("="*80)
        
        for tram_num in target_trams:
            matching = [r for r in routes if r.get('route_number') == tram_num]
            if matching:
                for route in matching:
                    print(f"\n🚊 Tram {tram_num}:")
                    print(f"   Route ID:     {route.get('route_id')}")
                    print(f"   Route Name:   {route.get('route_name', 'N/A')}")
                    print(f"   Route Number: {route.get('route_number', 'N/A')}")
        
        print("\n" + "="*80)
        print("🔍 ROUTE IDs WE SAW IN DEPARTURES:")
        print("="*80)
        
        for route_id in target_route_ids:
            matching = [r for r in routes if r.get('route_id') == route_id]
            if matching:
                for route in matching:
                    print(f"\n📍 Route ID {route_id}:")
                    print(f"   Tram Number:  {route.get('route_number', 'Unknown')}")
                    print(f"   Route Name:   {route.get('route_name', 'N/A')}")
            else:
                print(f"\n📍 Route ID {route_id}: Not found in tram routes")
        
        print("\n" + "="*80)
        print("📋 ALL TRAM ROUTES (first 20):")
        print("="*80)
        
        for i, route in enumerate(routes[:20], 1):
            route_num = route.get('route_number', 'N/A')
            route_name = route.get('route_name', 'N/A')
            route_id = route.get('route_id', 'N/A')
            print(f"{i:2d}. Tram {route_num:3s} │ ID: {route_id:4d} │ {route_name[:50]}")
        
        print("\n" + "="*80)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    get_tram_route_details()
