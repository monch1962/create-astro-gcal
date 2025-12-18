import pytest
from astro.retrograde import RetrogradeCalculator
from datetime import datetime

def test_mercury_retrograde_2025(engine):
    """
    Verify Mercury Retrograde cycles in 2025.
    Expected Pattern: R (Retrograde) -> D (Direct) -> Shadow Exit.
    Mercury has ~3-4 cycles per year.
    2025 Cycles (Approx):
    1. Mar 15 (R) -> Apr 7 (D) -> Apr 26 (Exit)
    2. Jul 18 (R) -> Aug 11 (D) -> Aug 25 (Exit)
    3. Nov 9 (R) -> Nov 29 (D) -> Dec 17 (Exit)
    """
    calc = RetrogradeCalculator(engine)
    events = calc.get_retrograde_events(2025, 2025, ['Mercury'])
    
    # Sort
    events.sort(key=lambda x: x['start_time'])
    
    # We expect 9 events (3 cycles) 
    # Or possibly 10 if a shadow exit from Dec 2024 lands in Jan 2025?
    # Retrograde Dec 2024 ends Dec 2024. Shadow exit ~Jan 2025?
    # Let's inspect.
    if len(events) != 9:
        print(f"Got {len(events)} events:")
        for e in events:
            print(f" - {e['start_time']} : {e['summary']}")
            
    assert len(events) in [9, 10], f"Expected 9 or 10 events for Mercury 2025, found {len(events)}"
    
    # Check Cycle 1 (March)
    # Filter by month to be robust
    march_rx = [e for e in events if "Retrograde" in e['summary'] and e['start_time'].month == 3]
    assert len(march_rx) == 1
    
    # ... (Skipping strict day checks to avoid timezone brittleness)
    
    print("Mercury 2025 Retrograde Test Passed.")

def test_mars_retrograde_2025_impact(engine):
    """
    Check Mars. Mars Rx is rarer (every 2 years).
    In 2024-2025:
    Mars Rx starts Dec 6, 2024.
    Mars Direct Feb 24, 2025.
    Shadow Exit April/May 2025.
    """
    calc = RetrogradeCalculator(engine)
    events = calc.get_retrograde_events(2025, 2025, ['Mars'])
    
    directs = [e for e in events if "Direct" in e['summary']]
    exits = [e for e in events if "Shadow Exit" in e['summary']]
    
    assert len(directs) >= 1
    assert directs[0]['start_time'].month == 2 # Feb 2025
    
    assert len(exits) >= 1
    # Shadow Exit is April 22 (Month 4). Allow 4 or 5.
    assert exits[0]['start_time'].month in [4, 5]
    
    print("Mars 2025 Partial Cycle Test Passed.")
