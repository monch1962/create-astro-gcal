from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderUnavailable

# Initialize the geocoder with a unique user-agent to avoid blocking
geolocator = Nominatim(user_agent="astro_gcal_generator_v1")

# Common cities cache to avoid API timeouts
FALLBACK_CITIES = {
    "New York, USA": (40.7128, -74.0060),
    "London, UK": (51.5074, -0.1278),
    "Paris, France": (48.8566, 2.3522),
    "Tokyo, Japan": (35.6762, 139.6503),
    "Sydney, Australia": (-33.8688, 151.2093),
    "Chicago, USA": (41.8781, -87.6298),
    "Frankfurt, Germany": (50.1109, 8.6821),
    "Hong Kong": (22.3193, 114.1694),
    "Singapore": (1.3521, 103.8198),
    "Shanghai, China": (31.2304, 121.4737),
    "Mumbai, India": (19.0760, 72.8777),
    "Sao Paulo, Brazil": (-23.5505, -46.6333),
    "Dubai, UAE": (25.2048, 55.2708),
}

def get_lat_lon(city_name):
    """
    Resolves a city name to latitude and longitude.
    Returns a tuple (lat, lon) or None if not found.
    """
    # Check cache first
    if city_name in FALLBACK_CITIES:
        return FALLBACK_CITIES[city_name]
        
    try:
        location = geolocator.geocode(city_name)
        if location:
            return location.latitude, location.longitude
        else:
            return None
    except (GeocoderTimedOut, GeocoderUnavailable) as e:
        print(f"Geocoding service error: {e}")
        return None
