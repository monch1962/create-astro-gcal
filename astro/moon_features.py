from skyfield.api import load, wgs84
from skyfield import almanac
from skyfield.framelib import ecliptic_frame
import numpy as np
import datetime

class MoonFeatureCalculator:
    """
    Calculates miscellaneous lunar events.

    Purpose:
        - Lunar Nodes: Ascending (North Node) and Descending (South Node) ecliptic crossings.
        - Declination Extremes: Moon Furthest North/South (Lunar Standstills).

    Usage:
        calc = MoonFeatureCalculator(engine)
        events = calc.get_moon_features(2024, 2024)
        
        # Output:
        #   List of dictionaries, e.g.:
        #   [
        #     {'type': 'moon_feature', 'summary': 'Moon North Node', 'start_time': <datetime>, ...},
        #     {'type': 'moon_feature', 'summary': 'Moon Furthest North', 'start_time': <datetime>, ...},
        #   ]
    """
    def __init__(self, engine):
        self.engine = engine

    def get_moon_features(self, year_start, year_end):
        """
        Calculates Lunar Nodes (North/South) and Lunar Declination Extremes (Major/Minor Standstills).
        """
        ts = self.engine.ts
        eph = self.engine.eph
        moon = eph['moon']
        earth = eph['earth']
        
        t0 = ts.utc(year_start, 1, 1)
        t1 = ts.utc(year_end + 1, 1, 1) # Go a bit past to cover full end of year
        
        events_list = []
        
        # --- 1. Lunar Nodes (Ecliptic Latitude = 0) ---
        def moon_ecliptic_lat(t):
            lat, lon, dist = earth.at(t).observe(moon).apparent().frame_latlon(ecliptic_frame)
            return lat.degrees

        def moon_north_of_ecliptic(t):
            lat = moon_ecliptic_lat(t)
            return lat > 0

        moon_north_of_ecliptic.step_days = 0.5 # Moon moves fast
        
        t_nodes, y_nodes = almanac.find_discrete(t0, t1, moon_north_of_ecliptic)
        
        for ti, yi in zip(t_nodes, y_nodes):
            dt = ti.utc_datetime()
            
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
        def moon_declination_rate(t):
            # Calculate dec at t and t+epsilon
            _, dec, _ = earth.at(t).observe(moon).apparent().radec()
            
            dt = 1.0 / (24.0 * 3600.0) # 1 second step
            t_plus = ts.tt_jd(t.tt + dt)
            
            dec1 = dec.radians
            _, dec2, _ = earth.at(t_plus).observe(moon).apparent().radec()
            
            rate = dec2.radians - dec1
            return rate > 0 # True if increasing

        moon_declination_rate.step_days = 0.5

        t_ext, y_ext = almanac.find_discrete(t0, t1, moon_declination_rate)

        last_t_ext = None
        for ti, yi in zip(t_ext, y_ext):
            # Filter noise: Extremes coincide with derivative=0.
            # Numerical noise can cause rapid flipping around the zero-crossing.
            # Max/Min are separated by ~14 days. Ignore events closer than 5 days.
            if last_t_ext is not None and (ti.tt - last_t_ext.tt) < 5.0:
                continue
            last_t_ext = ti

            dt = ti.utc_datetime()
            
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
