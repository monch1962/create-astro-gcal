from skyfield.api import load, wgs84
from skyfield import almanac
import datetime
import pytz

def get_eclipses(year_start, year_end):
    """
    Calculates solar eclipses using New Moon events and angular separation.
    """
    ts = load.timescale()
    eph = load('de421.bsp')
    earth = eph['earth']
    sun = eph['sun']
    moon = eph['moon']
    
    t0 = ts.utc(year_start, 1, 1)
    t1 = ts.utc(year_end + 1, 1, 1)

    events_list = []

    # 1. Find New Moons
    # Phase function: 0 = New, 1 = First, 2 = Full, 3 = Last
    f = almanac.moon_phases(eph)
    times, phases = almanac.find_discrete(t0, t1, f)
    
    for t, phase in zip(times, phases):
        # --- Solar Eclipse (New Moon) ---
        if phase == 0: 
            # Sun/Moon radii ~0.26 deg each. Contact ~ 0.53 deg.
            # We use 0.8 to catch everything safely.
            SEP_LIMIT_SOLAR = 0.8
            
            def get_solar_sep(time):
                astrometric = earth.at(time).observe(sun)
                apparent = astrometric.apparent()
                moon_apparent = earth.at(time).observe(moon).apparent()
                return apparent.separation_from(moon_apparent).degrees

            sep_t = get_solar_sep(t)
            
            if sep_t < SEP_LIMIT_SOLAR:
                # Classify based on max separation at peak
                # Note: precise logic for Total/Annular requires radii, 
                # but typically < 0.05 is central (Total/Annular). > 0.5 is Partial.
                eclipse_type = "Partial Solar Eclipse"
                if sep_t < 0.1:
                   eclipse_type = "Total Solar Eclipse" # or Annular
                
                # Binary search for duration
                t_start, t_end = find_duration(ts, t, get_solar_sep, SEP_LIMIT_SOLAR)
                
                dt_start = t_start.utc_datetime()
                dt_end = t_end.utc_datetime()
                duration_min = (dt_end - dt_start).total_seconds() / 60.0
                
                description = f"{eclipse_type}. Max separation: {sep_t:.3f} deg. Duration: {int(duration_min)} mins."
                
                events_list.append({
                    'type': 'solar_eclipse',
                    'summary': eclipse_type,
                    'start_time': dt_start,
                    'duration_minutes': int(duration_min),
                    'description': description,
                    'calendar': 'Astro: Solar Eclipses'
                })

        # --- Lunar Eclipse (Full Moon) ---
        elif phase == 2:
            # Earth Shadow (Anti-Sun). 
            # Umbra radius ~0.7 deg. Penumbra ~1.2 deg. Moon radius ~0.26 deg.
            # Contact limit: Penumbra radius + Moon radius ~ 1.5 deg.
            SEP_LIMIT_LUNAR = 1.5
            
            def get_lunar_sep(time):
                # Anti-Sun vector
                # Observe Sun from Earth, get apparent, rotate 180 lon?
                # Better: Observe Earth from Sun? No, perspective matters.
                # Standard way: Apparent position of shadow center is (Sun Lon + 180, -Sun Lat).
                
                # Get Sun Apparent (Ecliptic)
                sun_obs = earth.at(time).observe(sun)
                sun_lat, sun_lon, _ = sun_obs.apparent().ecliptic_latlon()
                
                # Anti-Sun (Shadow Center)
                shadow_lon = (sun_lon.degrees + 180) % 360
                shadow_lat = -sun_lat.degrees
                
                # Moon Apparent
                moon_obs = earth.at(time).observe(moon)
                moon_lat, moon_lon, _ = moon_obs.apparent().ecliptic_latlon()
                
                # Great circle distance
                # Since we are close to ecliptic, simple approximation or vector math.
                # Let's use skyfield separation if possible? 
                # We can construct a position?
                # Easier: angular separation of (lon, lat) vs (shadow_lon, shadow_lat)
                # Approximation for small angles: sqrt(dLon^2 + dLat^2)
                
                d_lon = abs(moon_lon.degrees - shadow_lon)
                if d_lon > 180: d_lon = 360 - d_lon
                
                d_lat = abs(moon_lat.degrees - shadow_lat)
                
                dist = (d_lon**2 + d_lat**2)**0.5
                return dist

            sep_t = get_lunar_sep(t)
            
            if sep_t < SEP_LIMIT_LUNAR:
                # Classify
                # Umbra radius ~0.7 + Moon ~0.26 ~= 0.96 for Partial Umbral
                # If < ~0.4, likely Total.
                eclipse_type = "Penumbral Lunar Eclipse"
                if sep_t < 1.0:
                    eclipse_type = "Partial Lunar Eclipse"
                if sep_t < 0.4:
                    eclipse_type = "Total Lunar Eclipse"
                    
                t_start, t_end = find_duration(ts, t, get_lunar_sep, SEP_LIMIT_LUNAR)
                
                dt_start = t_start.utc_datetime()
                dt_end = t_end.utc_datetime()
                duration_min = (dt_end - dt_start).total_seconds() / 60.0

                description = f"{eclipse_type}. Max separation to Shadow Center: {sep_t:.3f} deg. Duration: {int(duration_min)} mins."
                
                events_list.append({
                    'type': 'lunar_eclipse',
                    'summary': eclipse_type,
                    'start_time': dt_start,
                    'duration_minutes': int(duration_min),
                    'description': description,
                    'calendar': 'Astro: Lunar Eclipses'
                })

    return events_list

def find_duration(ts, t_peak, sep_func, limit):
    """
    Generic binary search to find duration where sep_func(t) < limit.
    Searches backwards and forwards from t_peak.
    """
    # Search Start
    found_start = False
    
    # Coarse search back
    t_search = t_peak
    t_start = t_peak
    for _ in range(35): # 35 * 10 = ~6 hours back
        t_prev = ts.utc(t_search.utc_datetime() - datetime.timedelta(minutes=10))
        if sep_func(t_prev) > limit:
            # Start is between t_prev and t_search
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
        
    if not found_start: t_start = t_peak # should not happen if event is valid

    # Search End
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
