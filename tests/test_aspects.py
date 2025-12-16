from astro.aspects import AspectCalculator
import datetime

def test_aspects_jupiter_uranus_2024(engine):
    calc = AspectCalculator(engine)
    
    # Jupiter-Uranus Conjunction: April 20, 2024 
    # Exact moment ~07:27 UTC.
    events = calc.get_aspects(2024, 2024, ['Jupiter', 'Uranus'], ['conjunction'], orb=1.0)
    
    assert len(events) > 0
    # Find the one covering April 20.
    # Event has start_time and duration_minutes.
    target = None
    target_date = datetime.date(2024, 4, 20)
    
    for e in events:
        start_dt = e['start_time'].date()
        end_dt = (e['start_time'] + datetime.timedelta(minutes=e['duration_minutes'])).date()
        if start_dt <= target_date <= end_dt:
            target = e
            break
            
    assert target is not None, f"Did not find Jupiter-Uranus conjunction covering April 20, 2024. Found: {[e['summary'] + ' ' + str(e['start_time']) for e in events]}"
    assert target['type'] == 'aspect'
    assert 'Conjunction' in target['summary']

def test_aspects_vectorized_speed(engine):
    # Just a quick check that it doesn't crash on empty or single body
    calc = AspectCalculator(engine)
    events = calc.get_aspects(2024, 2024, ['Sun'], ['conjunction'], orb=1.0)
    assert len(events) == 0 # Cannot conjoin self (unless logic is flawed)
