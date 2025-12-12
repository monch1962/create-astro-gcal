from skyfield.api import load
from skyfield.api import N, S, E, W
from skyfield import almanac
import datetime

def get_conjunctions(year_start, year_end, planets_to_check=['mars', 'jupiter', 'saturn', 'venus']):
    """
    Finds conjunctions between specified planets.
    """
    ts = load.timescale()
    eph = load('de421.bsp')
    earth = eph['earth']
    
    t0 = ts.utc(year_start, 1, 1)
    t1 = ts.utc(year_end + 1, 1, 1)

    events_list = []
    
    # Map common names to ephemeris names
    # de421.bsp has barycenters for Jupiter/Saturn/Uranus/Neptune/Pluto
    name_map = {
        'mercury': 'mercury',
        'venus': 'venus',
        'earth': 'earth',
        'mars': 'mars',
        'jupiter': 'jupiter barycenter',
        'saturn': 'saturn barycenter',
        'uranus': 'uranus barycenter',
        'neptune': 'neptune barycenter',
        'pluto': 'pluto barycenter',
        'moon': 'moon',
        'sun': 'sun'
    }
    
    # Filter and resolve names
    target_names = []
    for p in planets_to_check:
        p_lower = p.lower()
        if p_lower in name_map:
            target_names.append(name_map[p_lower])
        else:
             # Fallback or strict?
             target_names.append(p)

    planet_objs = {name: eph[name] for name in target_names}
    
    # We need to compare every pair.
    # This can be computationally expensive if we check every minute.
    # Approach: Use almanac.find_discrete for each pair? 
    # Or just iterate daily/hourly?
    # Skyfield `almanac` doesn't have a direct "conjunction" finder for planets.
    
    # Let's simple check: Find local minima of separation?
    # Or just "separation < X degrees".
    
    # Implementing a separation function for a pair
    names = list(planet_objs.keys())
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            p1_name = names[i]
            p2_name = names[j]
            p1 = planet_objs[p1_name]
            p2 = planet_objs[p2_name]
            
            def separation_at(t):
                # angular separation in degrees
                obs1 = earth.at(t).observe(p1)
                obs2 = earth.at(t).observe(p2)
                return obs1.separation_from(obs2).degrees
            
            # Use `separation_at` to find minima? 
            # Optimization: check daily, if close, refine.
            # Simplified: just checking daily for now to demonstrate. 
            # If < 2 degrees, log it.
            
            # A more robust way: use searchlib
            # But for this MVP, let's step through days.
            
            curr_t = t0
            while curr_t.tt < t1.tt:
                sep = separation_at(curr_t)
                if sep < 2.0: # Close conjunction
                    # Check if it's a local minimum or just part of a close pass
                    # For now just add an event if it's the first time we see it close in this "window"
                    # logic to avoid duplicates: rudimentary
                    
                    dt = curr_t.utc_datetime()
                    summary = f"Conjunction: {p1_name.title()} & {p2_name.title()}"
                    events_list.append({
                        'type': 'conjunction',
                        'summary': summary,
                        'start_time': dt,
                        'duration_minutes': 60,
                        'description': f"{p1_name.title()} and {p2_name.title()} are within {sep:.2f} degrees."
                    })
                    # Skip ahead a few days to avoid multiple entries for the same event
                    curr_t = ts.tt_jd(curr_t.tt + 5) 
                else:
                    curr_t = ts.tt_jd(curr_t.tt + 1)
                    
    return events_list
