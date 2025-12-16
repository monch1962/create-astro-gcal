from skyfield.api import load
from skyfield.framelib import ecliptic_frame
import datetime

class RetrogradeCalculator:
    """
    Calculates planetary retrograde motion stations and shadow periods.

    Purpose:
        - Identifies "Retrograde Station" (Direct -> Retrograde) and "Direct Station" (Retrograde -> Direct).
        - Calculates "Shadow Exit" (when planet returns to the longitude where it started retrograding).
        - Analyzes apparent longitude velocity relative to Earth.

    Usage:
        calc = RetrogradeCalculator(engine)
        events = calc.get_retrograde_events(2024, 2024, planets_to_check=['Mercury', 'Venus'])

        # Output:
        #   List of dictionaries, e.g.:
        #   [
        #     {'type': 'retrograde', 'summary': 'Mercury Retrograde', 'start_time': <datetime>, ...}, # Station R
        #     {'type': 'retrograde', 'summary': 'Mercury Direct', 'start_time': <datetime>, ...}, # Station D
        #     {'type': 'retrograde', 'summary': 'Mercury Shadow Exit', 'start_time': <datetime>, ...},
        #   ]
    """
    def __init__(self, engine):
        self.engine = engine

    def get_retrograde_events(self, year_start, year_end, planets_to_check):
        ts = self.engine.ts
        eph = self.engine.eph
        earth = eph['earth']
        
        # Scan wide enough to catch start/end of loops
        t_start_scan = ts.utc(year_start, 1, 1)
        t_end_scan = ts.utc(year_end + 2, 1, 1) 

        events = []
        
        name_map = {
            'mercury': 'mercury',
            'venus': 'venus',
            'mars': 'mars',
            'jupiter': 'jupiter barycenter',
            'saturn': 'saturn barycenter',
            'uranus': 'uranus barycenter',
            'neptune': 'neptune barycenter',
            'pluto': 'pluto barycenter'
        }
        
        for p_name in planets_to_check:
            clean_name = p_name.lower()
            if clean_name not in name_map: continue
            body = eph[name_map[clean_name]]
            
            def get_lon(t):
                _, lon, _ = earth.at(t).observe(body).apparent().frame_latlon(ecliptic_frame)
                return lon.degrees
                
            def get_velocity(t):
                dt = 1.0 / 1440.0 # 1 min
                l1 = get_lon(t)
                l2 = get_lon(ts.tt_jd(t.tt + dt))
                d = l2 - l1
                if d > 180: d -= 360
                if d < -180: d += 360
                return d

            # Step 1: Find all Stations in scan range
            current_t = t_start_scan
            end_t = t_end_scan
            
            # Initial State
            v = get_velocity(current_t)
            is_retro = v < 0
            
            stations = [] # (time, type='R'|'D', lon)
            
            # Day steps
            days_total = int(end_t - current_t)
            for i in range(days_total):
                t_check = ts.utc(year_start, 1, 1 + i)
                t_next = ts.utc(year_start, 1, 1 + i + 1)
                v_next = get_velocity(t_next)
                is_retro_next = v_next < 0
                
                if is_retro != is_retro_next:
                    # Find exact
                    low, high = t_check, t_next
                    for _ in range(15):
                        mid = ts.tt_jd((low.tt + high.tt)/2)
                        vm = get_velocity(mid)
                        if is_retro: # R to D (Direct Station)
                            if vm < 0: low = mid
                            else: high = mid
                        else: # D to R (Rx Station)
                            if vm > 0: low = mid
                            else: high = mid
                    
                    st_time = high
                    st_type = 'D' if is_retro else 'R' # If was R, now D.
                    st_lon = get_lon(st_time)
                    
                    stations.append({
                        'time': st_time,
                        'type': st_type,
                        'lon': st_lon
                    })
                    
                is_retro = is_retro_next
                
            # Step 2: Process Stations and Find Shadow Exits
            for i in range(len(stations)):
                st = stations[i]
                dt = st['time'].utc_datetime()
                
                if year_start <= dt.year <= year_end:
                    summary = f"{p_name.title()} Retrograde" if st['type'] == 'R' else f"{p_name.title()} Direct"
                    desc = f"{p_name.title()} stations {st['type']} at {st['lon']:.2f} deg."
                    events.append({
                        'type': 'retrograde',
                        'summary': summary,
                        'start_time': dt,
                        'duration_minutes': 0,
                        'description': desc,
                        'calendar': f"Astro: {p_name.title()}"
                    })
                    
                # If Direct Station, look for Shadow Exit
                if st['type'] == 'D':
                    # Find most recent R
                    if i > 0 and stations[i-1]['type'] == 'R':
                        prev_r = stations[i-1]
                        target_lon = prev_r['lon']
                        
                        search_start = st['time']
                        
                        # Rough scan
                        days_search = 365
                        for d in range(0, days_search, 2):
                            t_a = ts.tt_jd(search_start.tt + d)
                            t_b = ts.tt_jd(search_start.tt + d + 2)
                            
                            # Distance to target
                            def diff_target(t):
                                l = get_lon(t)
                                d = l - target_lon
                                if d > 180: d -= 360
                                if d < -180: d += 360
                                return d
                                
                            da = diff_target(t_a)
                            db = diff_target(t_b)
                            
                            if da < 0 and db >= 0: # Crossed from below to above
                                # Found it
                                low, high = t_a, t_b
                                for _ in range(15):
                                    mid = ts.tt_jd((low.tt + high.tt)/2)
                                    if diff_target(mid) < 0: low = mid
                                    else: high = mid
                                
                                exit_time = high
                                
                                dt_exit = exit_time.utc_datetime()
                                if year_start <= dt_exit.year <= year_end:
                                    events.append({
                                        'type': 'retrograde',
                                        'summary': f"{p_name.title()} Shadow Exit",
                                        'start_time': dt_exit,
                                        'duration_minutes': 0,
                                        'description': f"{p_name.title()} exits retrograde shadow at {target_lon:.2f} deg.",
                                        'calendar': f"Astro: {p_name.title()}"
                                    })
                                break
                        
        return events
