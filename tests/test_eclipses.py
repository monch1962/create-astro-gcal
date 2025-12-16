from astro.eclipses import EclipseCalculator
import datetime

def test_eclipses_2024(engine):
    calc = EclipseCalculator(engine)
    eclipses = calc.get_eclipses(2024, 2024)
    
    # 2024 had 2 Solar (April 8 Total, Oct 2 Annular) and 2 Lunar (Mar 25 Penumbral, Sept 18 Partial)
    assert len(eclipses) >= 3
    
    # Verify April 8, 2024 Total Solar Eclipse
    # Date: 2024-04-08 (or nearby).
    target_date = datetime.date(2024, 4, 8)
    april_solar = [e for e in eclipses if abs((e['start_time'].date() - target_date).days) <= 1 and 'solar' in e['type']]
    
    found_summaries = [f"{e['summary']} on {e['start_time']}" for e in eclipses]
    assert len(april_solar) == 1, f"Expected 1 Solar Eclipse around April 8, found {len(april_solar)}. All: {found_summaries}"
    
    eclipse = april_solar[0]
    assert 'Solar Eclipse' in eclipse['summary']
    # Check it's roughly mid-day UTC or evening? 
    # April 8 2024 eclipse max was ~18:17 UTC.
    # Start time should be earlier (partial phase start or total start).
    # Manual detection finds start of "eclipse state" (separation < 1.5 deg).
    # Separation < 1.5 deg (~3 Moon widths) starts ~2-3 hours before max.
    # So roughly 15:00 - 18:00 start.
    assert 12 <= eclipse['start_time'].hour <= 20
