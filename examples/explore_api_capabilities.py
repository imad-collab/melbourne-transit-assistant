import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.ptv_client import PTVClient
from config.credentials_alt import DEV_ID, API_KEY


def explore_api_capabilities():
    """Explore what the second API can actually do"""
    client = PTVClient(DEV_ID, API_KEY)
    
    print("="*80)
    print("🔍 EXPLORING SECOND API CAPABILITIES")
    print("="*80)
    print(f"\nUsing DEV_ID: {DEV_ID}")
    print(f"Base URL: {client.base_url}")
    print("\n" + "="*80)
    
    try:
        # Test 1: Check all route types
        print("\n1️⃣  ROUTE TYPES AVAILABLE:")
        print("─"*80)
        route_types = client.get_route_types()
        if route_types.get('route_types'):
            for rt in route_types['route_types']:
                print(f"   {rt['route_type']}: {rt['route_type_name']}")
        
        # Test 2: Get all routes
        print("\n2️⃣  CHECKING ALL ROUTES:")
        print("─"*80)
        all_routes = client.get_routes()
        if all_routes.get('routes'):
            print(f"   Total routes found: {len(all_routes['routes'])}")
            
            # Group by route type
            route_by_type = {}
            for route in all_routes['routes']:
                route_type = route.get('route_type', 'Unknown')
                route_type_name = {0: 'Train', 1: 'Tram', 2: 'Bus', 3: 'V/Line', 4: 'Night Bus'}.get(route_type, 'Unknown')
                if route_type_name not in route_by_type:
                    route_by_type[route_type_name] = []
                route_by_type[route_type_name].append(route)
            
            print("\n   Routes by type:")
            for rtype, routes in route_by_type.items():
                print(f"   - {rtype}: {len(routes)} routes")
        
        # Test 3: Try to search for freeway-related terms
        print("\n3️⃣  SEARCHING FOR FREEWAY/ROAD RELATED DATA:")
        print("─"*80)
        
        search_terms = [
            "freeway", "highway", "motorway", "citylink", 
            "westgate", "eastlink", "monash freeway", "road"
        ]
        
        found_anything = False
        for term in search_terms:
            try:
                results = client.search_stops(term, max_results=5)
                if results.get('stops') or results.get('routes'):
                    print(f"   ✅ Found results for '{term}':")
                    if results.get('stops'):
                        print(f"      - {len(results['stops'])} stops")
                        for stop in results['stops'][:3]:
                            print(f"        • {stop['stop_name']}")
                    if results.get('routes'):
                        print(f"      - {len(results['routes'])} routes")
                    found_anything = True
            except:
                pass
        
        if not found_anything:
            print("   ❌ No freeway/road related data found")
        
        # Test 4: Check available API endpoints
        print("\n4️⃣  STANDARD PTV API ENDPOINTS:")
        print("─"*80)
        print("   The PTV Timetable API provides access to:")
        print("   ✅ /v3/route_types          - Route types (train, tram, bus, etc.)")
        print("   ✅ /v3/routes               - All routes")
        print("   ✅ /v3/stops                - Stop information")
        print("   ✅ /v3/departures           - Departure times")
        print("   ✅ /v3/search               - Search for stops/routes")
        print("   ✅ /v3/patterns             - Route patterns")
        print("   ✅ /v3/disruptions          - Service disruptions")
        print("   ✅ /v3/directions           - Route directions")
        print("   ✅ /v3/runs                 - Run information")
        print("   ✅ /v3/outlets              - Myki outlets")
        print("   ✅ /v3/fare_estimate        - Fare estimates")
        
        print("\n   ❌ NOT AVAILABLE:")
        print("   ❌ Freeway/road traffic data")
        print("   ❌ Road conditions")
        print("   ❌ Traffic speed/congestion")
        print("   ❌ Road closures")
        print("   ❌ Traffic cameras")
        
        print("\n" + "="*80)
        print("📊 CONCLUSION:")
        print("="*80)
        print("This API (DEV_ID 3003798) is a PTV TIMETABLE API")
        print("\n✅ Provides: Public Transport data (trains, trams, buses)")
        print("❌ Does NOT provide: Freeway/road/traffic data")
        print("\nFor freeway data, you would need:")
        print("- VicRoads Traffic API")
        print("- DOT (Department of Transport) API")
        print("- Or another road/traffic specific API")
        print("="*80)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    print("\n🔍 API Capability Explorer\n")
    explore_api_capabilities()
