import pytest
import datetime
from astro.moon_features import MoonFeatureCalculator

def test_moon_features_duplicates(engine):
    start_year = 2024
    end_year = 2024
    
    calc = MoonFeatureCalculator(engine)
    events = calc.get_moon_features(start_year, end_year)
    
    # Sort by time
    events.sort(key=lambda x: x['start_time'])
    
    # Check for duplicates or close clusters
    last_event = None
    for e in events:
        if last_event:
            dt = e['start_time'] - last_event['start_time']
            # If events are identical summary and < 1 day apart, likely duplicate
            if e['summary'] == last_event['summary']:
                assert dt.total_seconds() > 86400, f"Duplicate event found: {e['summary']} at {e['start_time']} and {last_event['start_time']}"
        
        last_event = e
        
    print(f"Checked {len(events)} events. No close duplicates found.")

def test_moon_features_count(engine):
    # In 1 year, roughly 13 Nodes x 2 (North/South) = 26 Nodes
    # 13 Extremes x 2 (N/S) = 26 Extremes
    # Total ~ 52 events.
    calc = MoonFeatureCalculator(engine)
    events = calc.get_moon_features(2024, 2024)
    print(f"Total events: {len(events)}")
    assert 45 < len(events) < 60
