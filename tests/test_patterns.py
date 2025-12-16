from astro.patterns import PatternCalculator
import datetime

def test_patterns_2024(engine):
    calc = PatternCalculator(engine)
    
    # Specific Pattern found in jan 2024:
    # Jupiter Barycenter: Sq Sun & Tri Venus at ~2024-01-28 03:58 UTC
    # To keep test fast, only verify these 3 bodies.
    # This avoids calculating thousands of Moon aspects.
    bodies = ['Jupiter', 'Sun', 'Venus']
    
    events = calc.get_square_trine_patterns(2024, 2024, bodies)
    
    # Identify the specific instance
    target_date = datetime.date(2024, 1, 28)
    
    # Look for matching pattern
    # Summary should be "Jupiter Barycenter: Sq Sun & Tri Venus" or similar ordering.
    
    target = None
    for e in events:
        if e['start_time'].date() == target_date:
            # Check components
            s = e['summary']
            if 'Jupiter' in s and 'Square' in s and 'Trine' in s: # Relaxed check for "Sq" / "Tri" abbreviations
                 target = e
                 break
            # My code uses abbreviations: "Sq" and "Tri"
            if 'Jupiter' in s and 'Sq' in s and 'Tri' in s:
                 target = e
                 break
                 
    assert target is not None, f"Did not find Jupiter-Sun-Venus pattern on Jan 28, 2024. Found: {[e['summary'] for e in events]}"
    
    assert "Jupiter" in target['summary']
    assert "Sun" in target['summary']
    assert "Venus" in target['summary']
    assert target['type'] == 'pattern_square_trine'
