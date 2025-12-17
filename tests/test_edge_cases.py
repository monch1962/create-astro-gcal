import pytest
from astro.almanac import AlmanacCalculator
from astro.zodiac import ZodiacCalculator
from astro.moon_phases import MoonPhaseCalculator
from astro.aspects import AspectCalculator
from astro.engine import AstroEngine
import datetime

# Fixture to provide engine (cached if possible, but strict for tests)
@pytest.fixture(scope="module")
def engine():
    return AstroEngine()

def test_high_latitude_almanac(engine):
    """
    Test Almanac behavior in Tromsø (69.6 N) during Midnight Sun (June).
    Expectation: No Sunrise or Sunset events in mid-June.
    """
    calc = AlmanacCalculator(engine)
    # Tromsø coordinates
    lat, lon = 69.6492, 18.9553
    
    # June 2024
    events = calc.get_almanac_events(2024, 2024, ['Sun'], "Tromsø", lat, lon)
    
    # Filter for June
    june_events = [e for e in events if e['start_time'].month == 6]
    
    # In June in Tromsø, Sun is always UP. There should be NO Rise/Set events.
    # (Except maybe start/end of Midnight Sun period, but definitely not daily).
    
    # Check strictly for "Sun Rise" or "Sun Set"
    # Note: "Sun 1/3 (Rise-Set)" events ARE generated during Midnight Sun (treating it as a long day).
    rises = [e for e in june_events if e['summary'] == "Sun Rise"]
    sets = [e for e in june_events if e['summary'] == "Sun Set"]
    
    # Expect 0 rises/sets in June in Tromsø
    assert len(rises) == 0, f"Found unexpected Sun Rise in Midnight Sun: {rises}"
    assert len(sets) == 0, f"Found unexpected Sun Set in Midnight Sun: {sets}"
    print("High Latitude Test Passed: No daily Rise/Set during Midnight Sun.")

def test_zodiac_wraparound(engine):
    """
    Test Sun crossing from Pisces (330) -> Aries (0).
    Equinox ~ March 20/21.
    """
    calc = ZodiacCalculator(engine)
    events = calc.get_zodiac_ingress(2024, 2024, ['Sun'])
    
    aries_ingress = [e for e in events if "Aries" in e['summary']]
    assert len(aries_ingress) == 1
    assert "Sun enters Aries" in aries_ingress[0]['summary']
    assert aries_ingress[0]['start_time'].month == 3
    print("Zodiac Wraparound Test Passed.")

def test_blue_moon_august_2023(engine):
    """
    Test Blue Moon Month (August 2023).
    Expect Full Moon on Aug 1 and Aug 30/31.
    """
    calc = MoonPhaseCalculator(engine)
    events = calc.get_moon_phases(2023, 2023)
    
    full_moons = [e for e in events if "Full Moon" in e['summary']]
    aug_full_moons = [e for e in full_moons if e['start_time'].month == 8]
    
    assert len(aug_full_moons) == 2, f"Expected 2 Full Moons in Aug 2023, found {len(aug_full_moons)}"
    print("Blue Moon Test Passed.")

def test_triple_transit_2021(engine):
    """
    Test Saturn Square Uranus in 2021.
    It happened 3 times: Feb 17, Jun 14, Dec 24.
    """
    calc = AspectCalculator(engine)
    events = calc.get_aspects(2021, 2021, ['Saturn', 'Uranus'], ['square'], 1.0, 'earth')
    
    su_squares = [e for e in events if "Saturn" in e['summary'] and "Uranus" in e['summary'] and "Square" in e['summary']]
    
    # We might get multiple entries per aspect (Enter/Exact/Exit or just Duration).
    # Group by month.
    months = sorted(list(set([e['start_time'].month for e in su_squares])))
    
    # Expect occurrences in specific months
    assert 2 in months # Feb
    assert 6 in months # June
    assert 12 in months # Dec
    print("Triple Transit Test Passed.")

def test_leap_day_2024(engine):
    """
    Verify calculations handle Feb 29 correctly using Day Squares.
    Day 64 (8^2) should be Mar 4 in 2024 (Leap) and Mar 5 in 2025 (Non-Leap).
    """
    from astro.year_progress import YearProgressCalculator
    calc = YearProgressCalculator(engine)
    
    # 2024 (Leap)
    events_24 = calc.get_calendar_year_events(2024, 2024)
    day_64_24 = [e for e in events_24 if "Day 64 " in e['summary']][0]
    assert day_64_24['start_time'].month == 3
    assert day_64_24['start_time'].day == 4
    
    # 2025 (Non-Leap)
    events_25 = calc.get_calendar_year_events(2025, 2025)
    day_64_25 = [e for e in events_25 if "Day 64 " in e['summary']][0]
    assert day_64_25['start_time'].month == 3
    assert day_64_25['start_time'].day == 5
    
    print("Leap Year Test Passed.")
