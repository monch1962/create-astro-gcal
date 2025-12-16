import datetime
from skyfield.api import load
from skyfield import almanac

def generate_progress_events(year, start_dt, end_dt, calendar_name, event_prefix):
    """
    Helper to generate 1/16ths and Square Day events for a given duration.
    """
    events_list = []
    total_duration = end_dt - start_dt
    total_seconds = total_duration.total_seconds()
    
    # --- 1/16th Intervals ---
    for k in range(1, 16):
        fraction = k / 16.0
        percent = fraction * 100
        
        delta_seconds = total_seconds * fraction
        event_dt = start_dt + datetime.timedelta(seconds=delta_seconds)
        
        summary = f"{event_prefix}: {k}/16 ({percent:.1f}%)"
        description = f"Year {year} ({event_prefix}) is {percent:.1f}% complete."
        
        events_list.append({
            'type': 'year_progress_fraction',
            'summary': summary,
            'start_time': event_dt,
            'duration_minutes': 0,
            'description': description,
            'calendar': calendar_name
        })
        
    # --- Square Number Days ---
    # Day 1 is start_dt. Day n is start + (n-1) days.
    days_in_period = (end_dt - start_dt).days
    
    n = 1
    while True:
        sq = n * n
        if sq > days_in_period + 1: # check slightly beyond to be safe, but mostly strictly >
             break
        
        # Only process if sq is within duration
        # Day 1 = start + 0
        event_dt = start_dt + datetime.timedelta(days=sq - 1)
        
        if event_dt >= end_dt:
            break

        summary = f"{event_prefix} Day {sq} ({n}²)"
        description = f"Day {sq} of {event_prefix} {year} (Square of {n})."
        
        events_list.append({
            'type': 'year_progress_square',
            'summary': summary,
            'start_time': event_dt,
            'duration_minutes': 0,
            'description': description,
            'calendar': calendar_name
        })
        
        n += 1
        
    return events_list

def get_calendar_year_events(year_start, year_end):
    """
    Generates events for Calendar Year (Jan 1 - Dec 31).
    """
    events_list = []
    
    for year in range(year_start, year_end + 1):
        start_dt = datetime.datetime(year, 1, 1, tzinfo=datetime.timezone.utc)
        next_start_dt = datetime.datetime(year + 1, 1, 1, tzinfo=datetime.timezone.utc)
        
        events_list.extend(generate_progress_events(
            year, 
            start_dt, 
            next_start_dt, 
            "Astro: Calendar Year Progress",
            "Calendar Year"
        ))
            
    return events_list

def get_solar_year_events(year_start, year_end, ephemeris=None):
    """
    Generates events for Solar Year (Vernal Equinox - Vernal Equinox).
    """
    ts = load.timescale()
    if ephemeris:
        eph = ephemeris
    else:
        eph = load('de421.bsp')
    
    events_list = []
    
    # Need to find equinox for year_start... year_end + 1
    # We look a bit wider to capture start and end points
    t0 = ts.utc(year_start, 1, 1)
    t1 = ts.utc(year_end + 2, 1, 1) # Look ahead to get the 'end' of the last year
    
    f = almanac.seasons(eph)
    times, events = almanac.find_discrete(t0, t1, f)
    
    # 0 = Vernal Equinox, 1 = Summer Solstice, 2 = Autumnal Equinox, 3 = Winter Solstice
    vernals = []
    for t, code in zip(times, events):
        if code == 0:
            vernals.append(t.utc_datetime())
            
    # We iterate through the Vernal Equinoxes found. 
    # Valid solar year 'Y' starts at Vernal Y and ends at Vernal Y+1
    
    for i in range(len(vernals) - 1):
        start_dt = vernals[i]
        end_dt = vernals[i+1]
        
        # Determine "Year" label. Usually the year of the start date.
        year = start_dt.year
        
        if year >= year_start and year <= year_end:
            events_list.extend(generate_progress_events(
                year,
                start_dt,
                end_dt,
                "Astro: Solar Year Progress",
                "Solar Year"
            ))
            
    return events_list
