from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderUnavailable

# Initialize the geocoder with a unique user-agent to avoid blocking
geolocator = Nominatim(user_agent="astro_gcal_generator_v1")

def get_lat_lon(city_name):
    """
    Resolves a city name to latitude and longitude.
    Returns a tuple (lat, lon) or None if not found.
    """
    try:
        location = geolocator.geocode(city_name)
        if location:
            return location.latitude, location.longitude
        else:
            return None
    except (GeocoderTimedOut, GeocoderUnavailable) as e:
        print(f"Geocoding service error: {e}")
        return None
