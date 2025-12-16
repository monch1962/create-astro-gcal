from skyfield.api import load, wgs84
from skyfield import almanac
import skyfield.eclipselib as eclipselib
import datetime
import pytz

class EclipseCalculator:
    """
    Detects Solar and Lunar eclipses.

    Purpose:
        - Solar Eclipses: Uses a manual detection method (New Moon + Solar-Lunar separation check) 
          as Skyfield's search_global is not available in the current version.
        - Lunar Eclipses: Uses Skyfield's eclipselib.lunar_eclipses function.
        - Calculates duration for both types using binary search on separation/shadow thresholds.

    Usage:
        calc = EclipseCalculator(engine)
        events = calc.get_eclipses(2024, 2024)
        
        # Output:
        #   List of dictionaries, e.g.:
        #   [
        #     {'type': 'solar_eclipse', 'summary': 'Total Solar Eclipse', 'start_time': <datetime>, 'duration_minutes': <int>, ...},
        #     {'type': 'lunar_eclipse', 'summary': 'Partial Lunar Eclipse', 'start_time': <datetime>, ...},
        #   ]
    """
    def __init__(self, engine):
        self.engine = engine

    def get_eclipses(self, start_year, end_year):
        ts = self.engine.ts
        eph = self.engine.eph
        earth = eph['earth']
        sun = eph['sun']
        moon = eph['moon']
        
        t0 = ts.utc(start_year, 1, 1)
        t1 = ts.utc(end_year + 1, 1, 1)

        events_list = []

        # 1. Solar Eclipses (Manual: New Moon + Separation)
        f = almanac.moon_phases(eph)
        times, phases = almanac.find_discrete(t0, t1, f)
        
        SEP_LIMIT_SOLAR = 1.5 # degrees
        
        for t, phase in zip(times, phases):
            if phase == 0: # New Moon
                def get_solar_sep(time):
                    # Separation between Sun and Moon
                    astrometric = earth.at(time).observe(sun)
                    apparent = astrometric.apparent()
                    moon_apparent = earth.at(time).observe(moon).apparent()
                    return apparent.separation_from(moon_apparent).degrees

                sep_t = get_solar_sep(t)
                
                if sep_t < SEP_LIMIT_SOLAR:
                    # Classify based on separation (approx)
                    eclipse_type = "Partial Solar Eclipse"
                    if sep_t < 0.05: # Very close alignment suitable for Central (Total/Annular)
                         # Distinguishing Total vs Annular requires apparent size check.
                         # We'll stick to 'Total/Annular' or just 'Solar Eclipse'.
                         eclipse_type = "Total Solar Eclipse" 
                    elif sep_t < 0.5:
                         eclipse_type = "Solar Eclipse"
                    
                    t_start, t_end = self._find_duration(ts, t, get_solar_sep, SEP_LIMIT_SOLAR)
                    
                    dt_start = t_start.utc_datetime()
                    dt_end = t_end.utc_datetime()
                    duration_min = (dt_end - dt_start).total_seconds() / 60.0
                    if duration_min < 1: duration_min = 1
                    
                    description = f"{eclipse_type}. Max separation: {sep_t:.3f} deg. Duration: {int(duration_min)} mins."
                    
                    events_list.append({
                        'type': 'solar_eclipse',
                        'summary': eclipse_type,
                        'start_time': dt_start,
                        'duration_minutes': int(duration_min),
                        'description': description,
                        'calendar': 'Astro: Solar Eclipses'
                    })

        # 2. Lunar Eclipses (Library)
        t_lunar, y_lunar, details_lunar = eclipselib.lunar_eclipses(t0, t1, eph)
        
        lunar_codes = {
            0: 'Penumbral Lunar Eclipse',
            1: 'Partial Lunar Eclipse',
            2: 'Total Lunar Eclipse'
        }
        
        for ti, yi, det in zip(t_lunar, y_lunar, details_lunar):
            eclipse_type = lunar_codes.get(yi, "Lunar Eclipse")
            dt = ti.utc_datetime()
            
            # Duration? Library doesn't give duration directly, just peak time.
            # We can use our manual duration finder if we define a sep function?
            # Or just point event.
            # Let's try to calculate duration using Shadow Separation.
            
            def get_lunar_sep(time):
                # Distance from Earth Shadow center (Anti-Sun)
                sun_obs = earth.at(time).observe(sun)
                sun_lat, sun_lon, _ = sun_obs.apparent().ecliptic_latlon()
                shadow_lon = (sun_lon.degrees + 180) % 360
                shadow_lat = -sun_lat.degrees
                
                moon_obs = earth.at(time).observe(moon)
                moon_lat, moon_lon, _ = moon_obs.apparent().ecliptic_latlon()
                
                d_lon = abs(moon_lon.degrees - shadow_lon)
                if d_lon > 180: d_lon = 360 - d_lon
                d_lat = abs(moon_lat.degrees - shadow_lat)
                return (d_lon**2 + d_lat**2)**0.5

            # Limit: Penumbra radius (~1.25 deg) + Moon radius (~0.25 deg) ~ 1.5 deg
            SEP_LIMIT_LUNAR = 1.5
            
            t_start, t_end = self._find_duration(ts, ti, get_lunar_sep, SEP_LIMIT_LUNAR)
            dt_start = t_start.utc_datetime()
            dt_end = t_end.utc_datetime()
            duration_min = (dt_end - dt_start).total_seconds() / 60.0
            if duration_min < 1: duration_min = 1
            
            description = f"{eclipse_type}. Duration: {int(duration_min)} mins."
             
            events_list.append({
                'type': 'lunar_eclipse',
                'summary': eclipse_type,
                'start_time': dt_start, # Use calculated start? Or peak? 
                # Ideally Start. Eclipse usually defined by start/end.
                # But peak is useful. Let's use Start.
                'start_time': dt_start,
                'duration_minutes': int(duration_min),
                'description': description,
                'calendar': 'Astro: Lunar Eclipses'
            })
            
        return events_list

    def _find_duration(self, ts, t_peak, sep_func, limit):
        # Helper binary search
        found_start = False
        t_search = t_peak
        t_start = t_peak
        
        # Backwards
        for _ in range(35): 
            t_prev = ts.utc(t_search.utc_datetime() - datetime.timedelta(minutes=10))
            if sep_func(t_prev) > limit:
                low = t_prev
                high = t_search
                for _ in range(10): 
                    mid = ts.utc(low.utc_datetime() + (high.utc_datetime() - low.utc_datetime()) / 2)
                    if sep_func(mid) > limit: low = mid
                    else: high = mid
                t_start = high
                found_start = True
                break
            t_search = t_prev
        
        if not found_start: t_start = t_peak
        
        # Forwards
        found_end = False
        t_search = t_peak
        t_end = t_peak
        for _ in range(35):
            t_next = ts.utc(t_search.utc_datetime() + datetime.timedelta(minutes=10))
            if sep_func(t_next) > limit:
                low = t_search
                high = t_next
                for _ in range(10):
                    mid = ts.utc(low.utc_datetime() + (high.utc_datetime() - low.utc_datetime()) / 2)
                    if sep_func(mid) < limit: low = mid
                    else: high = mid
                t_end = low
                found_end = True
                break
            t_search = t_next
            
        if not found_end: t_end = t_peak
        return t_start, t_end
