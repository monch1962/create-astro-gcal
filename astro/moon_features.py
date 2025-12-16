from skyfield.api import load, wgs84
from skyfield import almanac
from skyfield.framelib import ecliptic_frame
import numpy as np
import datetime

def get_moon_features(year_start, year_end, ephemeris=None):
    """
    Calculates Lunar Nodes (North/South) and Lunar Declination Extremes (Major/Minor Standstills).
    """
    ts = load.timescale()
    if ephemeris:
        eph = ephemeris
    else:
        eph = load('de421.bsp')
    moon = eph['moon']
    earth = eph['earth']
    
    t0 = ts.utc(year_start, 1, 1)
    t1 = ts.utc(year_end + 1, 1, 1) # Go a bit past to cover full end of year
    
    events_list = []
    
    # --- 1. Lunar Nodes (Ecliptic Latitude = 0) ---
    def moon_ecliptic_lat(t):
        # apparent() includes light travel time, etc.
        # But for nodes we usually want geometric or apparent? 
        # Skyfield docs often use apparent for this.
        lat, lon, dist = earth.at(t).observe(moon).apparent().frame_latlon(ecliptic_frame)
        return lat.degrees

    # We want to find where lat is 0. 
    # find_discrete needs a function that returns disjoint values, but here we have continuous function.
    # We can use `find_discrete` if we define a boolean "is north of ecliptic".
    # Crossings happen when this boolean changes.
    
    def moon_north_of_ecliptic(t):
        lat = moon_ecliptic_lat(t)
        return lat > 0

    moon_north_of_ecliptic.step_days = 0.5 # Moon moves fast
    
    t_nodes, y_nodes = almanac.find_discrete(t0, t1, moon_north_of_ecliptic)
    
    for ti, yi in zip(t_nodes, y_nodes):
        dt = ti.utc_datetime()
        # yi is the new state. 
        # If yi is True (Lat > 0), we just crossed from South to North -> Ascending/North Node.
        # If yi is False (Lat < 0), we crossed from North to South -> Descending/South Node.
        
        if yi:
            summary = "Moon North Node"
            desc = "Moon crosses ecliptic to the North (Ascending Node)."
        else:
            summary = "Moon South Node"
            desc = "Moon crosses ecliptic to the South (Descending Node)."
            
        events_list.append({
            'type': 'moon_feature',
            'summary': summary,
            'start_time': dt,
            'duration_minutes': 0,
            'description': desc,
            'calendar': 'Astro: Moon Features'
        })


    # --- 2. Declination Extremes (Max/Min Dec) ---
    # We want where derivative of declination is 0.
    
    def moon_declination_rate(t):
        # We need check rate of change.
        # A simple way is to observe a slightly later time and diff (numerical derivative).
        # Or simpler: Skyfield has searchlib for maxima? No, only find_discrete for state changes usually.
        # But we can define "is declination increasing?". 
        # Peaks occur when "increasing" changes clearly.
        
        # Careful: numerical derivative might be noisy? No, DE421 is smooth.
        # We want dec(t).
        
        # Calculate dec at t and t+epsilon
        # But calling .frame_latlon() is expensive.
        # Let's inspect dec.
        
        ra, dec, dist = earth.at(t).observe(moon).apparent().radec()
        
        # We also need rate. 
        # Let's try "is declination positive?" no that gives crossings eq.
        # "Is declination increasing?"
        
        # We can implement a function that returns True if velocity in Dec is positive.
        # Declination velocity.
        
        # Actually skyfield position objects have output of velocity.
        # But radec() returns values, not velocities directly usually unless requested.
        # Let's use a small step for rate.
        
        dt = 1.0 / (24.0 * 3600.0) # 1 second step
        t_plus = ts.tt_jd(t.tt + dt)
        
        dec1 = dec.radians
        ra2, dec2, dist2 = earth.at(t_plus).observe(moon).apparent().radec()
        
        rate = dec2.radians - dec1
        return rate > 0 # True if increasing

    moon_declination_rate.step_days = 0.5

    t_ext, y_ext = almanac.find_discrete(t0, t1, moon_declination_rate)

    for ti, yi in zip(t_ext, y_ext):
        dt = ti.utc_datetime()
        # yi is the NEW state.
        # If yi is True (Increasing), we were decreasing before? No.
        # Wait, find_discrete finds when return value CHANGES.
        # If Change to True (Now Increasing), previous was Decreasing -> Minimum (South)
        # If Change to False (Now Decreasing), previous was Increasing -> Maximum (North)
        
        if yi:
            # Changed from Decreasing to Increasing -> Min (South Peak)
            summary = "Moon Furthest South"
            desc = "Lunar Southern Standstill (Max South Declination)."
        else:
            # Changed from Increasing to Decreasing -> Max (North Peak)
            summary = "Moon Furthest North"
            desc = "Lunar Northern Standstill (Max North Declination)."

        events_list.append({
            'type': 'moon_feature',
            'summary': summary,
            'start_time': dt,
            'duration_minutes': 0,
            'description': desc,
            'calendar': 'Astro: Moon Features'
        })
        
    return events_list
