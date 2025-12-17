from skyfield.api import load, wgs84
from skyfield.framelib import ecliptic_frame
import numpy as np
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

class AspectCalculator:
    """
    Calculates exact astrological aspects between planets.
    
    Purpose:
        - Identifies Conjunctions, Sextiles, Squares, Trines, Oppositions, etc.
        - Calculates precise start/end times based on an 'Orb' (degree of tolerance).
        - Determines exact moment of 0-degree separation ("Exactness").
        
    Usage:
        from astro.aspects import AspectCalculator
        
        calc = AspectCalculator(engine)
        events = calc.get_aspects(
            year_start=2024,
            year_end=2024,
            planets_to_check=['Sun', 'Jupiter', 'Saturn'],
            aspects_to_check=['conjunction', 'square'],
            orb=1.0,
            center_body='earth' # or 'sun' for Heliocentric
        )
        
        # Output:
        #   List of dictionaries, e.g.:
        #   [
        #     {'type': 'aspect', 'summary': 'Conjunction: Sun - Jupiter', 'start_time': <datetime>, 'duration_minutes': <int>, ...},
        #   ]
    """
    def __init__(self, engine):
        self.engine = engine

    def get_aspects(self, year_start, year_end, planets_to_check, aspects_to_check, orb=5.0, center_body='earth'):
        """
        Finds exact astrological aspects between specified planets using vectorized calculation.
        center_body: 'earth' (Geocentric) or 'sun' (Heliocentric).
        """
        ts = self.engine.ts
        eph = self.engine.eph
        
        # Define observer
        if center_body.lower() == 'sun':
            observer = eph['sun']
        else:
            observer = eph['earth']
        
        # 1. Map Names and Filter
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
                mapped_name = name_map[p_lower]
                # Filter self-observation
                if center_body.lower() == 'sun' and mapped_name == 'sun': continue
                if center_body.lower() == 'earth' and mapped_name == 'earth': continue
                target_names.append(mapped_name)
            else:
                target_names.append(p)
                
        planet_objs = {name: eph[name] for name in target_names}
        names = list(planet_objs.keys())

        # 2. Vectorized Position Calculation
        # Generate time grid. 
        # Daily steps (like original code) are sufficient even for Moon (~13 deg/day).
        start_dt = datetime.datetime(year_start, 1, 1, tzinfo=datetime.timezone.utc)
        end_dt = datetime.datetime(year_end + 1, 1, 1, tzinfo=datetime.timezone.utc)
        days = (end_dt - start_dt).days + 1
        
        steps_per_day = 1 
        total_steps = days * steps_per_day
        
        # Generate array of offsets in hours
        hours_vector = np.arange(total_steps) * (24.0 / steps_per_day)
        t_vector = ts.utc(year_start, 1, 1, hours_vector)
        
        # Pre-calculate longitudes for all bodies
        # Store as dictionary of arrays
        longitudes = {}
        
        for name, body in planet_objs.items():
            # Optimization: Use Astrometric (Geometric) position for coarse search.
            # This is ~8.5x faster than apparent() and sufficient for finding proper intervals.
            # Precision is handled by bisection_search using apparent() later.
            _, lon, _ = observer.at(t_vector).observe(body).frame_latlon(ecliptic_frame)
            longitudes[name] = lon.degrees # NumPy array

        events_list = []
        
        # Helper for root finding using Bisection
        def bisection_search(f, t_start, t_end, tol_days=1e-6): # ~0.1 seconds precision
            jd_min = t_start.tt
            jd_max = t_end.tt
            
            v_min = f(t_start)
            
            for _ in range(20): # 20 iterations is sufficient for high precision
                jd_mid = (jd_min + jd_max) / 2.0
                if (jd_max - jd_min) < tol_days:
                    return ts.tt_jd(jd_mid)
                    
                t_mid = ts.tt_jd(jd_mid)
                v_mid = f(t_mid)
                
                if v_mid == 0:
                     return t_mid
                
                if v_min * v_mid < 0:
                    jd_max = jd_mid
                    # v_max = v_mid
                else:
                    jd_min = jd_mid
                    v_min = v_mid
                    
            return ts.tt_jd((jd_min + jd_max) / 2.0)

        # Function Factories
        def get_diff_func(body1, body2, target):
            def f(t):
                _, l1, _ = observer.at(t).observe(body1).apparent().frame_latlon(ecliptic_frame)
                _, l2, _ = observer.at(t).observe(body2).apparent().frame_latlon(ecliptic_frame)
                d = (l1.degrees - l2.degrees) % 360
                return (d - target + 180) % 360 - 180
            return f

        def get_orb_func(body1, body2, target, orb):
            def f(t):
                _, l1, _ = observer.at(t).observe(body1).apparent().frame_latlon(ecliptic_frame)
                _, l2, _ = observer.at(t).observe(body2).apparent().frame_latlon(ecliptic_frame)
                d = (l1.degrees - l2.degrees) % 360
                dist = (d - target + 180) % 360 - 180
                return abs(dist) - orb
            return f

        # 3. Pairwise Comparison
        for i in range(len(names)):
            for j in range(i + 1, len(names)):
                n1 = names[i]
                n2 = names[j]
                
                l1_arr = longitudes[n1]
                l2_arr = longitudes[n2]
                
                # Difference array
                diff_arr = (l1_arr - l2_arr) % 360
                
                for asp, angle in ASPECTS.items():
                    if asp not in aspects_to_check: continue
                    
                    targets = [angle]
                    if angle != 0 and angle != 180:
                        targets.append(360 - angle)
                    
                    for tgt in targets:
                        # Detect crossings in the coarse array
                        val = (diff_arr - tgt + 180) % 360 - 180
                        
                        # Sign change detection
                        sign_change = (val[:-1] * val[1:] <= 0)
                        no_wrap = (np.abs(val[:-1] - val[1:]) < 180)
                        candidate_indices = np.where(sign_change & no_wrap)[0]
                        
                        for idx in candidate_indices:
                            t_start = t_vector[idx]
                            t_end = t_vector[idx+1]
                            
                            # Find exact root
                            func = get_diff_func(planet_objs[n1], planet_objs[n2], tgt)
                            try:
                                t_exact = bisection_search(func, t_start, t_end)
                                
                                # Calculate Duration (Orb)
                                orb_func = get_orb_func(planet_objs[n1], planet_objs[n2], tgt, orb)
                                
                                # Duration Search Window (e.g., 30 days back/fwd or dynamic)
                                # Simple approach: Check coarse grid to find bracket? 
                                # Or just blind search 30 days if planet is slow?
                                
                                # Entry
                                t_entry = t_exact
                                try:
                                    # Look back 30 days
                                    t_back = ts.utc(t_exact.utc_datetime() - datetime.timedelta(days=30))
                                    # Check if orb_func changes sign between t_back and t_exact
                                    # Only if we entered the orb window.
                                    if orb_func(t_back) * orb_func(t_exact) < 0:
                                         t_entry = bisection_search(orb_func, t_back, t_exact)
                                    else:
                                         # Maybe closer? Try 1 day
                                         t_back_1d = ts.utc(t_exact.utc_datetime() - datetime.timedelta(days=1))
                                         if orb_func(t_back_1d) * orb_func(t_exact) < 0:
                                             t_entry = bisection_search(orb_func, t_back_1d, t_exact)
                                except: pass
                                    
                                # Exit
                                t_exit = t_exact
                                try:
                                    t_fwd = ts.utc(t_exact.utc_datetime() + datetime.timedelta(days=30))
                                    if orb_func(t_exact) * orb_func(t_fwd) < 0:
                                         t_exit = bisection_search(orb_func, t_exact, t_fwd)
                                    else:
                                         t_fwd_1d = ts.utc(t_exact.utc_datetime() + datetime.timedelta(days=1))
                                         if orb_func(t_exact) * orb_func(t_fwd_1d) < 0:
                                             t_exit = bisection_search(orb_func, t_exact, t_fwd_1d)
                                except: pass

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
                                    'description': f"{n1} and {n2} exact {asp} ({tgt} deg). Orb: {orb} deg.",
                                    'participants': [n1, n2]
                                })
                                
                            except Exception as e:
                                # print(f"Error calculating aspect {summary}: {e}")
                                continue

        return events_list
