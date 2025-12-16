from skyfield.api import load
from skyfield import almanac
import datetime

def get_seasons(year_start, year_end, ephemeris=None):
    """
    Calculates Equinoxes and Solstices.
    """
    ts = load.timescale()
    if ephemeris:
        eph = ephemeris
    else:
        eph = load('de421.bsp')
    
    t0 = ts.utc(year_start, 1, 1)
    t1 = ts.utc(year_end + 1, 1, 1)
    
    # almanac.seasons returns time, value
    # values: 0=Spring, 1=Summer, 2=Autumn, 3=Winter (Northern Hemisphere)
    t, y = almanac.find_discrete(t0, t1, almanac.seasons(eph))
    
    events_list = []
    
    season_names = {
        0: "Vernal Equinox (Spring)",
        1: "Summer Solstice",
        2: "Autumnal Equinox (Fall)",
        3: "Winter Solstice"
    }
    
    for ti, yi in zip(t, y):
        dt = ti.utc_datetime()
        name = season_names.get(yi, "Unknown Season")
        
        events_list.append({
            'type': 'season',
            'summary': name,
            'start_time': dt,
            'duration_minutes': 0, # Point event
            'description': f"{name}. Exact moment.",
            'calendar': 'Astro: Seasons'
        })
        
    return events_list
