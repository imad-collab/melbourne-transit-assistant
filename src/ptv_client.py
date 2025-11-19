import hashlib
import hmac
import requests
from urllib.parse import urlparse, quote


class PTVClient:
    """Client for interacting with the PTV Timetable API (Melbourne Transit Assistant)"""
    
    def __init__(self, dev_id, api_key, base_url="https://timetableapi.ptv.vic.gov.au"):
        self.dev_id = dev_id
        self.api_key = api_key
        self.base_url = base_url
    
    def _generate_signature(self, request_path):
        """Generate HMAC signature for API request"""
        raw = request_path + ("&" if "?" in request_path else "?") + f"devid={self.dev_id}"
        hashed = hmac.new(
            self.api_key.encode('utf-8'),
            raw.encode('utf-8'),
            hashlib.sha1
        )
        signature = hashed.hexdigest()
        return signature
    
    def _build_url(self, endpoint):
        """Build full URL with signature"""
        request_path = endpoint
        signature = self._generate_signature(request_path)
        url = f"{self.base_url}{request_path}"
        url += "&" if "?" in url else "?"
        url += f"devid={self.dev_id}&signature={signature}"
        return url
    
    def make_request(self, endpoint):
        """Make authenticated request to PTV API"""
        url = self._build_url(endpoint)
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    
    # Example API methods
    def get_route_types(self):
        """Get all route types (train, tram, bus, etc.)"""
        return self.make_request("/v3/route_types")
    
    def search_stops(self, search_term, route_types=None, max_results=10):
        """Search for stops by name"""
        # URL encode the search term
        encoded_term = quote(search_term, safe='')
        endpoint = f"/v3/search/{encoded_term}"
        params = []
        if route_types:
            params.append(f"route_types={','.join(map(str, route_types))}")
        if max_results:
            params.append(f"max_results={max_results}")
        if params:
            endpoint += "?" + "&".join(params)
        return self.make_request(endpoint)
    
    def get_departures(self, route_type, stop_id, max_results=5, expand=None):
        """Get departures from a specific stop"""
        endpoint = f"/v3/departures/route_type/{route_type}/stop/{stop_id}"
        params = [f"max_results={max_results}"]
        if expand:
            params.append(f"expand={','.join(expand)}")
        endpoint += "?" + "&".join(params)
        return self.make_request(endpoint)
    
    def get_routes(self, route_types=None):
        """Get all routes for specified route types"""
        if route_types:
            endpoint = f"/v3/routes?route_types={','.join(map(str, route_types))}"
        else:
            endpoint = "/v3/routes"
        return self.make_request(endpoint)
    
    def get_route_info(self, route_id):
        """Get detailed information about a specific route"""
        endpoint = f"/v3/routes/{route_id}"
        return self.make_request(endpoint)
    
    def get_run_info(self, run_ref, route_type):
        """Get detailed information about a specific run"""
        endpoint = f"/v3/runs/{run_ref}/route_type/{route_type}"
        return self.make_request(endpoint)
