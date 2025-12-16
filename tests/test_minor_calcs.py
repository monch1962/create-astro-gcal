import pytest
import datetime
from astro.retrograde import RetrogradeCalculator
from astro.seasons import SeasonCalculator
from astro.moon_features import MoonFeatureCalculator
from astro.zodiac import ZodiacCalculator
from astro.moon_phases import MoonPhaseCalculator
from astro.year_progress import YearProgressCalculator

def test_retrograde_mercury_2024(engine):
    calc = RetrogradeCalculator(engine)
    events = calc.get_retrograde_events(2024, 2024, ['Mercury'])
    
    # Mercury Rx Station: April 1, 2024 (~22:14 UTC)
    target = next((e for e in events if e['start_time'].date() == datetime.date(2024, 4, 1)), None)
    
    assert target is not None, "Mercury should station retrograde on April 1, 2024"
    assert "Retrograde" in target['summary']
    # Check time (allow tolerance)
    assert 20 <= target['start_time'].hour <= 23

def test_seasons_2024(engine):
    calc = SeasonCalculator(engine)
    events = calc.get_seasons(2024, 2024)
    
    # Vernal Equinox: March 20, 2024 (~03:06 UTC)
    vernal = next((e for e in events if "Vernal Equinox" in e['summary']), None)
    assert vernal is not None
    assert vernal['start_time'].month == 3
    assert vernal['start_time'].day == 20
    assert 2 <= vernal['start_time'].hour <= 4

def test_moon_features_2024(engine):
    calc = MoonFeatureCalculator(engine)
    events = calc.get_moon_features(2024, 2024)
    # Check valid list
    assert len(events) > 40
    assert any("Moon North Node" in e['summary'] for e in events)

def test_zodiac_ingress_sun_2024(engine):
    calc = ZodiacCalculator(engine)
    events = calc.get_zodiac_ingress(2024, 2024, ['Sun'])
    
    # Sun enters Aries: March 20, 2024
    aries = next((e for e in events if "Sun enters Aries" in e['summary']), None)
    assert aries is not None
    assert aries['start_time'].month == 3
    assert aries['start_time'].day == 20
    # Should coincide with Equinox (~03:06 UTC)
    assert 2 <= aries['start_time'].hour <= 4

def test_moon_phases_2024(engine):
    calc = MoonPhaseCalculator(engine)
    events = calc.get_moon_phases(2024, 2024)
    
    # New Moon: Jan 11, 2024 (~11:57 UTC)
    avg_nm = next((e for e in events if "New Moon" in e['summary'] and e['start_time'].month == 1), None)
    assert avg_nm is not None
    assert avg_nm['start_time'].day == 11
    assert 10 <= avg_nm['start_time'].hour <= 14

def test_year_progress_2024(engine):
    calc = YearProgressCalculator(engine)
    cal_events = calc.get_calendar_year_events(2024, 2024)
    
    # 50% of year (Day ~183) -> July 1 or 2.
    # 8/16 = 50%
    halfway = next((e for e in cal_events if "8/16" in e['summary']), None)
    assert halfway is not None
    assert halfway['start_time'].month == 7
    assert halfway['start_time'].day <= 3
    
