from skyfield.api import wgs84
from skyfield import almanac
import datetime
import pytz

class AlmanacCalculator:
    def __init__(self, engine):
        self.engine = engine

    def get_almanac_events(self, year_start, year_end, bodies, location_name="Local Location", observer_lat=40.7128, observer_lon=-74.0060):
        """
        Calculates Rise, Set, Meridian Transit, and Nadir events for specified bodies.
        param location_name: Name of the location for the description (e.g. "New York").
        """
        ts = self.engine.ts
        eph = self.engine.eph
        
        if bodies is None:
            # Default fallback
            bodies = ['sun', 'moon']
            
        observer = wgs84.latlon(observer_lat, observer_lon)
        
        t0 = ts.utc(year_start, 1, 1)
        t1 = ts.utc(year_end + 1, 1, 1)
    
        events_list = []
        
        # Name map for Skyfield lookup
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
        
        for body_name in bodies:
            clean_name = body_name.lower()
            lookup_name = name_map.get(clean_name, clean_name)
            
            try:
                body = eph[lookup_name]
            except KeyError:
                # print(f"Warning: Could not find body '{lookup_name}' in ephemeris. Skipping.")
                continue
                
            # 1. Rise and Set
            f_rise_set = almanac.risings_and_settings(eph, body, observer)
            t_rs, y_rs = almanac.find_discrete(t0, t1, f_rise_set)
            
            last_rise_time = None
            
            for ti, yi in zip(t_rs, y_rs):
                # yi: 1=Rise, 0=Set
                is_rise = yi
                action = "Rise" if is_rise else "Set"
                dt = ti.utc_datetime()
                
                events_list.append({
                    'type': 'almanac',
                    'summary': f"{body_name.title()} {action}",
                    'start_time': dt,
                    'duration_minutes': 0,
                    'description': f"{body_name.title()} {action} at {location_name}.",
                    'calendar': f"Astro: {body_name.title()}", # Organize by planet
                    'participants': [body_name] # For consistency
                })
                
                if is_rise:
                    last_rise_time = dt
                else:
                    # Set event. Check if we have a previous Rise to calculate intervals.
                    if last_rise_time is not None:
                        duration = dt - last_rise_time
                        # Ensure positive duration (should be, unless data is weird)
                        if duration.total_seconds() > 0:
                            # Generate Thirds, Eighths, Nineteenths
                            divisions = {
                                3: range(1, 3),     # 1/3, 2/3
                                8: range(1, 8),     # 1/8 ... 7/8
                                19: range(1, 19)    # 1/19 ... 18/19
                            }
                            
                            for denom, numerators in divisions.items():
                                for num in numerators:
                                    fraction = num / denom
                                    delta = duration * fraction
                                    event_time = last_rise_time + delta
                                    
                                    events_list.append({
                                        'type': 'almanac',
                                        'summary': f"{body_name.title()} {num}/{denom} (Rise-Set)",
                                        'start_time': event_time,
                                        'duration_minutes': 0,
                                        'description': f"{body_name.title()} {num}/{denom} of day (Rise to Set).",
                                        'calendar': f"Astro: {body_name.title()}",
                                        'participants': [body_name]
                                    })
                        
                        last_rise_time = None # Reset pair
    
            # 2. Meridian Transits (MC and IC)
            # almanac.meridian_transits finds when body crosses meridian.
            # It returns 1 for transit (culmination/MC) and 0 for anti-transit (IC).
            f_transit = almanac.meridian_transits(eph, body, observer)
            t_tr, y_tr = almanac.find_discrete(t0, t1, f_transit)
            
            for ti, yi in zip(t_tr, y_tr):
                # yi: 1=Meridian Transit (Midheaven/MC), 0=Anti-transit (Nadir/IC)
                if yi:
                    action = "Midheaven (MC)"
                    code = "MC"
                else:
                    action = "Nadir (IC)"
                    code = "IC"
                    
                dt = ti.utc_datetime()
                
                events_list.append({
                    'type': 'almanac',
                    'summary': f"{body_name.title()} {code}",
                    'start_time': dt,
                    'duration_minutes': 0,
                    'description': f"{body_name.title()} {action} at {location_name}.",
                    'calendar': f"Astro: {body_name.title()}",
                    'participants': [body_name]
                })
                
        return events_list
