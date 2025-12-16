from skyfield.api import load
from skyfield.framelib import ecliptic_frame
from skyfield import almanac
import numpy as np

ZODIAC_SIGNS = [
    'Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo',
    'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces'
]

def get_zodiac_ingress(year_start, year_end, bodies=None, ephemeris=None):
    """
    Calculates when planets enter a new Zodiac sign (Geocentric Ecliptic Longitude).
    """
    ts = load.timescale()
    if ephemeris:
        eph = ephemeris
    else:
        eph = load('de421.bsp')
    t0 = ts.utc(year_start, 1, 1)
    t1 = ts.utc(year_end + 1, 1, 1)
    earth = eph['earth']
    
    if bodies is None:
        bodies = ['Sun', 'Moon', 'Mercury', 'Venus', 'Mars', 'Jupiter', 'Saturn', 'Uranus', 'Neptune', 'Pluto']
        
    events_list = []
    
    for body_name in bodies:
        try:
            # Handle naming differences (e.g. Earth vs Sun logic?)
            # Skyfield: earth.at(t).observe(sun) -> Apparent Sun Longitude
            # earth.at(t).observe(mars) -> Apparent Mars Longitude
            
            if body_name.lower() == 'sun':
                target = eph['sun']
            elif body_name.lower() == 'moon':
                target = eph['moon']
            else:
                target = eph[f"{body_name.lower()} barycenter"]

            def zodiac_sign(t):
                # Calculate apparent geocentric ecliptic longitude
                lat, lon, dist = earth.at(t).observe(target).apparent().frame_latlon(ecliptic_frame)
                return np.floor(lon.degrees / 30.0).astype(int)

            zodiac_sign.step_days = 0.5 if body_name.lower() != 'moon' else 0.1
            
            # find_discrete returns the time and the NEW value
            t_changes, y_changes = almanac.find_discrete(t0, t1, zodiac_sign)
            
            for ti, yi in zip(t_changes, y_changes):
                # yi is the index of the NEW sign (0-11)
                sign_name = ZODIAC_SIGNS[int(yi) % 12]
                dt = ti.utc_datetime()
                
                summary = f"{body_name.title()} enters {sign_name}"
                description = f"{body_name.title()} enters {sign_name} at 0°."
                
                events_list.append({
                    'type': 'zodiac_ingress',
                    'summary': summary,
                    'start_time': dt,
                    'duration_minutes': 0,
                    'description': description,
                    'calendar': f"Astro: {body_name.title()} Zodiac"
                })
                
        except Exception as e:
            print(f"Error calculating zodiac ingress for {body_name}: {e}")
            
    return events_list
