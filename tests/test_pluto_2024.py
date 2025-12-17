import pytest
from astro.zodiac import ZodiacCalculator

def test_pluto_2024_ingress(engine):
    """
    Verify Pluto's sign changes in 2024.
    Pluto enters Aquarius (Jan), Rxs into Capricorn (Sep), and enters Aquarius (Nov).
    Total 3 events.
    """
    calc = ZodiacCalculator(engine)
    events = calc.get_zodiac_ingress(2024, 2024, ['Pluto'])
    
    assert len(events) == 3, f"Expected 3 Pluto events in 2024, found {len(events)}"
    
    # Sort events by time just in case
    events.sort(key=lambda x: x['start_time'])
    
    # Event 1: Jan 20/21 - Enters Aquarius
    assert "Aquarius" in events[0]['summary']
    assert events[0]['start_time'].month == 1
    
    # Event 2: Sep 1/2 - Enters Capricorn (Rx)
    assert "Capricorn" in events[1]['summary']
    assert events[1]['start_time'].month == 9
    
    # Event 3: Nov 19/20 - Enters Aquarius
    assert "Aquarius" in events[2]['summary']
    assert events[2]['start_time'].month == 11
    
    print("Pluto 2024 Test Passed: 3 Events confirmed.")
