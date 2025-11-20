import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.ptv_client import PTVClient
from config.credentials import DEV_ID, API_KEY


def get_route_stops():
    """Get all stops on the metro route from Southern Cross to Tarneit"""
    client = PTVClient(DEV_ID, API_KEY)
    
    print("\n🚇 METRO ROUTE STOPS: Southern Cross → Tarneit\n")
    print("="*70)
    
    # Get stops on the metro line (route type 0 = Metro)
    try:
        # Southern Cross Railway Station - Stop ID: 1071
        southern_cross_stop_id = 1071
        
        print(f"\n📍 Starting Point: Southern Cross Railway Station (Stop ID: {southern_cross_stop_id})")
        print("\n🛤️  All Metro Stops on this route:\n")
        
        # Get all stops for metro (route type 0)
        stops_data = client.get_stops_by_route(route_type=0, route_id=1)
        
        if 'stops' in stops_data:
            stops = stops_data['stops']
            
            # Filter for westbound/outer stops from Southern Cross towards Tarneit
            print(f"Found {len(stops)} total metro stops\n")
            
            for i, stop in enumerate(stops[:20], 1):  # Show first 20 stops
                stop_id = stop.get('stop_id')
                stop_name = stop.get('stop_name', 'Unknown')
                suburb = stop.get('stop_suburb', '')
                
                print(f"{i:2d}. {stop_name}")
                if suburb:
                    print(f"    ({suburb})")
                print(f"    Stop ID: {stop_id}\n")
        
        print("="*70)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    get_route_stops()
