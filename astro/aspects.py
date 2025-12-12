from skyfield.api import load
from skyfield.framelib import ecliptic_frame
import datetime

# Define aspect angles
ASPECTS = {
    'conjunction': 0,
    'sextile': 60,
    'quintile': 72,
    'square': 90,
    'trine': 120,
    'biquintile': 144,
    'opposition': 180
}

def get_aspects(year_start, year_end, planets_to_check, aspects_to_check, orb=5.0, center_body='earth'):
    """
    Finds exact astrological aspects between specified planets.
    center_body: 'earth' (Geocentric) or 'sun' (Heliocentric).
    """
    ts = load.timescale()
    eph = load('de421.bsp')
    
    # Define observer based on center_body
    if center_body.lower() == 'sun':
        observer = eph['sun']
    else:
        observer = eph['earth']
    
    t0 = ts.utc(year_start, 1, 1)
    t1 = ts.utc(year_end + 1, 1, 1)

    events_list = []
    
    # Map common names to ephemeris names
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
    
    target_names = []
    for p in planets_to_check:
        p_lower = p.lower()
        if p_lower in name_map:
            # Filter invalid targets based on center
            mapped_name = name_map[p_lower]
            if center_body.lower() == 'sun' and mapped_name == 'sun':
                continue # Cannot observe Sun from Sun
            if center_body.lower() == 'earth' and mapped_name == 'earth':
                continue # Cannot observe Earth from Earth
            target_names.append(mapped_name)
        else:
            target_names.append(p)
            
    planet_objs = {name: eph[name] for name in target_names}
    names = list(planet_objs.keys())

    # Helper to get longitudes at a specific time
    def get_longitudes(t):
        longitudes = {}
        for name, body in planet_objs.items():
            # Ecliptic Longitude relative to observer
            _, lon, _ = observer.at(t).observe(body).apparent().frame_latlon(ecliptic_frame)
            longitudes[name] = lon.degrees
        return longitudes

    # Optimization: Pre-calculate daily steps? 
    # Or just iterate day by day. 365 days is fast.
    days = int(t1 - t0)
    
    previous_lons = get_longitudes(t0)
    
    for day in range(days + 1):
        t_start = ts.utc(year_start, 1, 1 + day)
        t_end = ts.utc(year_start, 1, 1 + day + 1)
        
        # We already have start from previous loop
        lons_start = previous_lons
        lons_end = get_longitudes(t_end) # This becomes next previous
        
        # Check every pair
        # Check every pair
        for i in range(len(names)):
            for j in range(i + 1, len(names)):
                n1 = names[i]
                n2 = names[j]
                
                l1_s = lons_start[n1]
                l2_s = lons_start[n2]
                diff_start = (l1_s - l2_s) % 360
                
                l1_e = lons_end[n1]
                l2_e = lons_end[n2]
                diff_end = (l1_e - l2_e) % 360
                
                # Check for crossing of any aspect
                for asp, target_angle in ASPECTS.items():
                    if asp not in aspects_to_check:
                        continue
                        
                    # We need to check if we crossed 'target_angle' or '360 - target_angle'?
                    # Actually, usually aspect is just angle separation.
                    # so absolute separation = target_angle.
                    # This happens when diff = target_angle OR diff = 360 - target_angle.
                    
                    targets = [target_angle, 360 - target_angle]
                    if target_angle == 0 or target_angle == 180:
                         targets = [target_angle]
                    
                    for tgt in targets:
                        # Check if tgt is "between" diff_start and diff_end shortest path
                        # Simple check: (diff_start - tgt) and (diff_end - tgt) have different signs?
                        # Care with wrap around.
                        
                        # Let's normalize everything relative to tgt to be [-180, 180]
                        d_s = (diff_start - tgt + 180) % 360 - 180
                        d_e = (diff_end - tgt + 180) % 360 - 180
                        
                        if d_s * d_e < 0 and abs(d_s - d_e) < 180:
                            # Crossed!
                            # Find exact time via binary search
                            
                            def get_diff_at(t):
                                _, lo1, _ = observer.at(t).observe(planet_objs[n1]).apparent().frame_latlon(ecliptic_frame)
                                _, lo2, _ = observer.at(t).observe(planet_objs[n2]).apparent().frame_latlon(ecliptic_frame)
                                return (lo1.degrees - lo2.degrees) % 360

                            # Binary search for EXACT peak (0 deg deviation from target)
                            low = 0.0
                            high = 1.0
                            for _ in range(15): # ~3 seconds precision
                                mid = (low + high) / 2
                                t_mid = ts.utc(year_start, 1, 1 + day + mid)
                                diff_mid = get_diff_at(t_mid)
                                
                                d_m = (diff_mid - tgt + 180) % 360 - 180
                                
                                if d_s * d_m < 0:
                                    high = mid
                                    # d_e becomes d_m effectively
                                else:
                                    low = mid
                                    # d_s becomes d_m effectively
                                    d_s = d_m
                            
                            t_exact = ts.utc(year_start, 1, 1 + day + low)
                            
                            # Calculate Orb Entry/Exit
                            # We search backwards/forwards until deviation > orb
                            
                            def get_dev(time):
                                diff_val = get_diff_at(time)
                                d = (diff_val - tgt + 180) % 360 - 180
                                return abs(d)

                            # Find Start (Entry)
                            # Search back in steps until dev > orb
                            t_start_search = t_exact
                            t_entry = t_exact
                            
                            # Step size: 1 day? For outer planets orb can be weeks.
                            # For Moon it is hours.
                            # We'll step 1 hour for safety? Or dynamic.
                            # Step: 4 hours (1/6 day)
                            step_days = 1.0/6.0
                            found_entry = False
                            
                            
                            for search_step in range(200): # max ~30 days back
                                t_prev = ts.utc(t_start_search.utc_datetime() - datetime.timedelta(hours=4))
                                dev_prev = get_dev(t_prev)
                                if dev_prev > orb:
                                    # Entry is between t_prev and t_start_search
                                    # Binary search
                                    lo = t_prev
                                    hi = t_start_search
                                    for _ in range(10):
                                        mid = ts.utc(lo.utc_datetime() + (hi.utc_datetime() - lo.utc_datetime()) / 2)
                                        if get_dev(mid) > orb: lo = mid
                                        else: hi = mid
                                    t_entry = hi
                                    found_entry = True
                                    break
                                t_start_search = t_prev
                                
                            if not found_entry:
                                t_entry = t_exact # Fallback if orb is huge (>30 days half-width)

                            # Find End (Exit)
                            t_end_search = t_exact
                            t_exit = t_exact
                            found_exit = False
                            
                            
                            for search_step in range(200):
                                t_next = ts.utc(t_end_search.utc_datetime() + datetime.timedelta(hours=4))
                                dev_next = get_dev(t_next)
                                if dev_next > orb:
                                    lo = t_end_search
                                    hi = t_next
                                    for _ in range(10):
                                        mid = ts.utc(lo.utc_datetime() + (hi.utc_datetime() - lo.utc_datetime()) / 2)
                                        if get_dev(mid) < orb: lo = mid
                                        else: hi = mid
                                    t_exit = lo
                                    found_exit = True
                                    break
                                t_end_search = t_next
                                
                            if not found_exit:
                                t_exit = t_exact

                            dt_start = t_entry.utc_datetime()
                            dt_end = t_exit.utc_datetime()
                            
                            duration_min = (dt_end - dt_start).total_seconds() / 60.0
                            if duration_min < 1: duration_min = 1
                            
                            summary = f"{asp.title()}: {n1.title()} - {n2.title()}"
                            
                            events_list.append({
                                'type': 'aspect',
                                'summary': summary,
                                'start_time': dt_start,
                                'duration_minutes': int(duration_min),
                                'description': f"{n1} and {n2} exact {asp} ({target_angle} deg). Orb: {orb} deg.",
                                'participants': [n1, n2]
                            })

        previous_lons = lons_end

    return events_list
