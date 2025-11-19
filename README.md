## APIs Used
- Parking Spaces API
- GTFS (General Transit Feed Specification) API
- Freeway API
- Google API


# Melbourne Transit Assistant

Melbourne Transit Assistant is a real-time public transport application for Melbourne and Geelong CBD. It provides live train, tram, and bus information, and users can find parking spots for their vehicle in Melbourne and Geelong CBD. Designed for commuters and visitors, it streamlines journey planning and parking discovery in busy city centers.

Key Features:
- Real-time train, tram, and bus information for Melbourne and Geelong
- Search and discover available parking spots inside Melbourne CBD and Geelong CBD
- Easy journey planning for commuters and visitors
- Fast, reliable, and user-friendly interface

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Configure your API credentials:
   - Add your API credentials for the required services (Parking Spaces API, GTFS API, Freeway API, Google API) in the appropriate config files. Do not share your API keys publicly.

3. Run the demo:
   ```bash
   python examples/demo.py
   ```

## Project Structure

- `src/` - Core client code
- `config/` - Configuration and credentials
- `examples/` - Example usage scripts
