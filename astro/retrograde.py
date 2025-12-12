from skyfield.api import load
from skyfield.framelib import ecliptic_frame
import datetime

def get_retrograde_events(year_start, year_end, planets_to_check):
    """
    Finds Retrograde Stations, Direct Stations, and Shadow Exits.
    """
    ts = load.timescale()
    eph = load('de421.bsp')
    earth = eph['earth']
    
    t0 = ts.utc(year_start, 1, 1)
    # Go a bit extra to catch shadow exits for events starting in range
    t1 = ts.utc(year_end + 2, 1, 1) 

    events_list = []
    
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
        if clean_name not in name_map:
            continue
            
        body = eph[name_map[clean_name]]
        
        # 1. Define Velocity Function to find Stations
        # Retrograde happens when apparent ecliptic longitude decreasing.
        # Station = Velocity 0.
        
        def get_lon(t):
            _, lon, _ = earth.at(t).observe(body).apparent().frame_latlon(ecliptic_frame)
            return lon.degrees
            
        def get_velocity(t):
            # approximate instantaneous velocity
            # delta 1 minute
            dt_days = 1.0 / (24.0 * 60.0) 
            t_plus = ts.tt_jd(t.tt + dt_days)
            
            l1 = get_lon(t)
            l2 = get_lon(t_plus)
            
            diff = l2 - l1
            if diff > 180: diff -= 360
            if diff < -180: diff += 360
            
            return diff

        # Use find_discrete? 
        # We need a function that changes sign.
        # Forward (+), Retrograde (-). 
        # Station Retrograde: + to -
        # Station Direct: - to +
        
        # We need to define a discrete function?
        # No, simpler: check sign of velocity daily, then binary search.
        # Most planets stay Rx for weeks/months.
        
        # Optimization: Step daily.
        days = int(t1 - t0)
        
        # State: 'D' (Direct) or 'R' (Retrograde)
        # Init state
        v_start = get_velocity(t0)
        state = 'D' if v_start >= 0 else 'R'
        
        # Track active Rx to find Shadow Exit
        # We store the Longitude of the Rx Station
        current_rx_lon = None
        current_rx_start_dt = None
        
        # We need to handle year boundaries carefully.
        # If we start in the middle of Rx, we might detect Direct, but no simple Shadow Exit logic 
        # (since we missed the Rx Station lon). That's acceptable.
        
        for day in range(days):
            t_curr = ts.utc(year_start, 1, 1 + day)
            t_next = ts.utc(year_start, 1, 1 + day + 1)
            
            v_next = get_velocity(t_next)
            next_state = 'D' if v_next >= 0 else 'R'
            
            if state != next_state:
                # STATION DETECTED
                # Binary search for 0 crossing
                low = t_curr
                high = t_next
                
                for _ in range(15): # Precision
                    mid = ts.tt_jd((low.tt + high.tt) / 2)
                    v_mid = get_velocity(mid)
                    if state == 'D': # + to -
                        if v_mid > 0: low = mid
                        else: high = mid
                    else: # - to +
                        if v_mid < 0: low = mid
                        else: high = mid
                        
                t_station = high
                dt = t_station.utc_datetime()
                
                # Filter events strictly outside requested range (we scan extra for shadow)
                in_range = year_start <= dt.year <= year_end
                
                lz = get_lon(t_station)
                
                if state == 'D' and next_state == 'R':
                    # STATION RETROGRADE
                    if in_range:
                        events_list.append({
                            'type': 'retrograde',
                            'summary': f"{p_name.title()} Retrograde",
                            'start_time': dt,
                            'duration_minutes': 0,
                            'description': f"{p_name.title()} stations Retrograde at {lz:.2f} deg.",
                            'calendar': f"Astro: {p_name.title()}"
                        })
                    current_rx_lon = lz
                    current_rx_start_dt = dt
                    
                elif state == 'R' and next_state == 'D':
                    # STATION DIRECT
                    if in_range:
                        events_list.append({
                            'type': 'retrograde',
                            'summary': f"{p_name.title()} Direct",
                            'start_time': dt,
                            'duration_minutes': 0,
                            'description': f"{p_name.title()} stations Direct at {lz:.2f} deg.",
                            'calendar': f"Astro: {p_name.title()}"
                        })
                    
                    # Need to look for SHADOW EXIT
                    # Shadow exit is when it reaches current_rx_lon again.
                    # It is currently at lz (minima). It needs to go up to current_rx_lon.
                    if current_rx_lon is not None:
                         # We need to search FORWARD from t_station until lon = current_rx_lon
                         # This might take weeks/months.
                         # We can continue the main loop and check 'shadow_search' state?
                         pass
                         
            state = next_state
        
        # Shadow Search:
        # Re-scan for Shadow Exits based on identified Rx periods?
        # Or do it inline? Inline is hard because main loop is 1-day steps.
        # Easier: Collect all Rx/Direct pairs first.
        
    return events_list

# Refined Logic for Shadow Exits:
# It's cleaner to implement a 2-pass approach or separate searches.
# Given the "task" complexity, I will rewrite the function above to be robust.

def get_retrograde_full(year_start, year_end, planets_to_check):
    ts = load.timescale()
    eph = load('de421.bsp')
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
        # Shadow Exit happens after Direct Station, when Lon = Prev Rx Station Lon.
        
        for i in range(len(stations)):
            st = stations[i]
            dt = st['time'].utc_datetime()
            
            # Skip if out of user range (year_end)
            # But we process input for logic, filter output later?
            # Yes.
            
            # Event: Station
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
                    
                    # Search forward from st['time'] until lon = target_lon
                    # Planet moves forward now.
                    # Limit search to... 1 year? 
                    
                    search_start = st['time']
                    search_end = ts.tt_jd(search_start.tt + 365) # max 1 year search
                    
                    # Rough scan
                    found_exit = False
                    curr_search = search_start
                    
                    # Search 10 day chunks then refine?
                    days_search = 365
                    for d in range(0, days_search, 2):
                        t_a = ts.tt_jd(search_start.tt + d)
                        t_b = ts.tt_jd(search_start.tt + d + 2)
                        
                        la = get_lon(t_a)
                        lb = get_lon(t_b)
                        
                        # Check wrapping?
                        # target_lon is fixed. Planet is moving D.
                        # We want cross target_lon.
                        
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
                            found_exit = True
                            
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
