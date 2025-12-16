from astro.almanac import AlmanacCalculator
import datetime

def test_almanac_sun_2024(engine):
    """
    Test almanac for Sun only to ensure speed (avoiding 10 planets * 365 days).
    """
    calc = AlmanacCalculator(engine)
    events = calc.get_almanac_events(2024, 2024, bodies=['Sun'], location_name="Null Island", observer_lat=0, observer_lon=0)
    
    # Should have Rise, Set, Transit for roughly 365 days.
    # Check Jan 1, 2024 Sunrise at (0, 0).
    # roughly 06:00 UTC.
    jan_1_events = [e for e in events if e['start_time'].date() == datetime.date(2024, 1, 1)]
    sunrise = next((e for e in jan_1_events if 'Rise' in e['summary']), None)
    
    assert sunrise is not None
    # Sunrise at equator is ~06:00 local solar time. 
    # At 0 lon, UTC ~ Local Solar Time. 
    # Equation of Time ~3-4 mins. 
    # Refraction makes it rise earlier (~2 mins).
    # So 05:50 - 06:10 range.
    assert 5 <= sunrise['start_time'].hour <= 6
