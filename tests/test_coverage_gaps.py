import pytest
import datetime
from unittest.mock import MagicMock, patch
from utils import geocoding, engine_helper
from astro.year_progress import YearProgressCalculator

# --- Utils: Engine Helper ---
def test_engine_helper():
    # Reset first
    engine_helper.reset_engine()
    assert engine_helper._ENGINE_INSTANCE is None
    
    # Get engine
    e1 = engine_helper.get_shared_engine()
    assert e1 is not None
    assert engine_helper._ENGINE_INSTANCE is not None
    
    # Get again (should be same instance)
    e2 = engine_helper.get_shared_engine()
    assert e1 is e2
    
    # Reset
    engine_helper.reset_engine()
    assert engine_helper._ENGINE_INSTANCE is None

# --- Utils: Geocoding ---
def test_geocoding_cached():
    # Test strict cache hit
    res = geocoding.get_lat_lon("New York, USA")
    assert res == (40.7128, -74.0060)

@patch('utils.geocoding.geolocator')
def test_geocoding_api_hit(mock_geolocator):
    # Mock return
    mock_loc = MagicMock()
    mock_loc.latitude = 12.34
    mock_loc.longitude = 56.78
    mock_geolocator.geocode.return_value = mock_loc
    
    res = geocoding.get_lat_lon("Unknown City")
    assert res == (12.34, 56.78)
    mock_geolocator.geocode.assert_called_with("Unknown City")

@patch('utils.geocoding.geolocator')
def test_geocoding_api_fail(mock_geolocator):
    # Mock failure/not found
    mock_geolocator.geocode.return_value = None
    res = geocoding.get_lat_lon("Moon City")
    assert res is None

# --- Astro: Solar Year Progress ---
def test_solar_year_progress(engine):
    calc = YearProgressCalculator(engine)
    events = calc.get_solar_year_events(2024, 2024)
    
    # Should contain Solar Progress events
    assert len(events) > 0
    
    # Check for "Solar Year"
    solar_events = [e for e in events if "Solar Year" in e['summary']]
    assert len(solar_events) > 0
    
    # Check for fractionation
    fracs = [e for e in solar_events if "1/16" in e['summary']]
    assert len(fracs) > 0
    
    # Check for squares
    squares = [e for e in solar_events if "Day 4" in e['summary']]
    assert len(squares) > 0
