import pytest
import datetime
from datetime import timedelta
from astro.aspects import AspectCalculator
from astro.retrograde import RetrogradeCalculator
from astro.zodiac import ZodiacCalculator
from astro.almanac import AlmanacCalculator
from astro.eclipses import EclipseCalculator
from astro.seasons import SeasonCalculator
from astro.moon_phases import MoonPhaseCalculator

# Thresholds for duplication detection
THRESHOLDS = {
    'aspects': timedelta(hours=1),   # Aspects shouldn't repeat typically within an hour (except maybe Moon, but even then)
    'retrograde': timedelta(days=5), # Stations/Shadows are slow
    'zodiac': timedelta(hours=12),   # Ingress shouldn't flip-flop faster than 12h
    'almanac': timedelta(minutes=10), # Rise/Set shouldn't happen twice in 10 mins
    'eclipses': timedelta(days=1),
    'seasons': timedelta(days=10),
    'moon_phases': timedelta(days=1) 
}

def check_for_duplicates(events, category):
    events.sort(key=lambda x: x['start_time'])
    threshold = THRESHOLDS.get(category, timedelta(hours=1))
    
    duplicates = []
    last_event = None
    
    for e in events:
        if last_event:
            # Check summary match
            if e['summary'] == last_event['summary']:
                dt = e['start_time'] - last_event['start_time']
                if dt < threshold:
                    duplicates.append((last_event, e, dt))
        last_event = e
        
    return duplicates

def test_aspect_duplicates(engine):
    calc = AspectCalculator(engine)
    # Test major planets
    events = calc.get_aspects(2025, 2025, ['Sun', 'Mars'], ['conjunction', 'square'], 1.0, 'earth')
    dupes = check_for_duplicates(events, 'aspects')
    assert len(dupes) == 0, f"Found Aspect duplicates: {dupes}"

def test_retrograde_duplicates(engine):
    calc = RetrogradeCalculator(engine)
    events = calc.get_retrograde_events(2025, 2025, ['Mercury', 'Jupiter'])
    dupes = check_for_duplicates(events, 'retrograde')
    assert len(dupes) == 0, f"Found Retrograde duplicates: {dupes}"

def test_zodiac_duplicates(engine):
    calc = ZodiacCalculator(engine)
    events = calc.get_zodiac_ingress(2025, 2025, ['Sun', 'Moon', 'Mercury'])
    dupes = check_for_duplicates(events, 'zodiac')
    assert len(dupes) == 0, f"Found Zodiac duplicates: {dupes}"

def test_almanac_duplicates(engine):
    calc = AlmanacCalculator(engine)
    # Sun events
    events = calc.get_almanac_events(2025, 2025, ['Sun'], "TestLoc", 40.7, -74.0)
    dupes = check_for_duplicates(events, 'almanac')
    assert len(dupes) == 0, f"Found Almanac duplicates: {dupes}"

def test_eclipse_duplicates(engine):
    calc = EclipseCalculator(engine)
    events = calc.get_eclipses(2025, 2025)
    dupes = check_for_duplicates(events, 'eclipses')
    assert len(dupes) == 0, f"Found Eclipse duplicates: {dupes}"
    
def test_season_duplicates(engine):
    calc = SeasonCalculator(engine)
    events = calc.get_seasons(2025, 2025)
    dupes = check_for_duplicates(events, 'seasons')
    assert len(dupes) == 0, f"Found Season duplicates: {dupes}"
