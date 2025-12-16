import config
import logging
import sys
import datetime
import concurrent.futures
from collections import defaultdict
from utils import ics_writer
from astro.engine import AstroEngine
from astro.eclipses import EclipseCalculator
from astro.almanac import AlmanacCalculator
from astro.aspects import AspectCalculator
from astro.retrograde import RetrogradeCalculator
from astro.seasons import SeasonCalculator
from astro.moon_features import MoonFeatureCalculator
from astro.zodiac import ZodiacCalculator
from astro.moon_phases import MoonPhaseCalculator
from astro.year_progress import YearProgressCalculator
from astro.patterns import PatternCalculator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# --- Worker Functions (Must be top-level for pickling) ---

def task_generate_eclipses(start_year, end_year):
    logger.info("  [Task] Eclipses started...")
    engine = AstroEngine()
    calc = EclipseCalculator(engine)
    events = calc.get_eclipses(start_year, end_year)
    
    processed_events = []
    if events:
        for e in events:
            if e['type'] == 'solar_eclipse':
                e['calendar'] = config.CALENDAR_NAMES['solar_eclipse']
            elif e['type'] == 'lunar_eclipse':
                e['calendar'] = config.CALENDAR_NAMES['lunar_eclipse']
            processed_events.append(e)
    logger.info(f"  [Task] Eclipses finished ({len(processed_events)} events).")
    return processed_events

def task_generate_aspects(start_year, end_year, bodies, aspects_list, orb, center_body):
    sys_label = "geocentric" if center_body == 'earth' else "heliocentric"
    logger.info(f"  [Task] Aspects ({sys_label}) started...")
    
    engine = AstroEngine()
    calc = AspectCalculator(engine)
    events = calc.get_aspects(
        start_year, end_year, 
        planets_to_check=bodies,
        aspects_to_check=aspects_list,
        orb=orb,
        center_body=center_body
    )
    processed_events = []
    if events:
        for e in events:
            if center_body == 'sun':
                e['summary'] = f"{e['summary']} (Helio)"
                e['description'] = f"(Heliocentric) {e['description']}"
                
                if 'participants' in e:
                        for p in e['participants']:
                            p_clean = p.replace(' barycenter', '').title()
                            e_copy = e.copy()
                            e_copy['calendar'] = f"Astro: {p_clean} Helio"
                            processed_events.append(e_copy)
                else:
                        e['calendar'] = "Astro: Aspects Helio"
                        processed_events.append(e)
            else:
                if 'participants' in e:
                    for p in e['participants']:
                        p_clean = p.replace(' barycenter', '').title()
                        e_copy = e.copy()
                        e_copy['calendar'] = f"Astro: {p_clean} Geo"
                        processed_events.append(e_copy)
                else:
                    e['calendar'] = "Astro: Aspects Geo"
                    processed_events.append(e)
    logger.info(f"  [Task] Aspects ({sys_label}) finished ({len(events)} raw events).")
    return processed_events

def task_generate_almanac(start_year, end_year, bodies, location_name, lat, lon):
    logger.info("  [Task] Almanac started...")
    engine = AstroEngine()
    calc = AlmanacCalculator(engine)
    events = calc.get_almanac_events(
        start_year, end_year, 
        bodies=bodies,
        location_name=location_name,
        observer_lat=lat,
        observer_lon=lon
    )
    processed_events = []
    if events:
        for e in events:
            parts = e['summary'].split()
            planet = parts[0] if parts else "Unknown"
            if "(Rise-Set)" in e['summary']:
                    e['calendar'] = f"Astro: {planet} Divisions"
            else:
                    e['calendar'] = f"Astro: {planet} Almanac"
            processed_events.append(e)
    logger.info(f"  [Task] Almanac finished ({len(processed_events)} events).")
    return processed_events

def task_generate_retrograde(start_year, end_year, planets):
    logger.info("  [Task] Retrograde started...")
    engine = AstroEngine()
    calc = RetrogradeCalculator(engine)
    events = calc.get_retrograde_events(start_year, end_year, planets)
    processed_events = []
    if events:
            for e in events:
                cal = e.get('calendar', 'Astro: Retrograde')
                if cal.startswith('Astro: ') and not cal.endswith(' Geo') and 'Retrograde' not in cal:
                    e['calendar'] = f"{cal} Geo"
                elif 'calendar' not in e:
                    e['calendar'] = 'Astro: Retrograde Geo'
                processed_events.append(e)
    logger.info(f"  [Task] Retrograde finished ({len(processed_events)} events).")
    return processed_events

def task_generate_seasons(start_year, end_year):
    logger.info("  [Task] Seasons started...")
    engine = AstroEngine()
    calc = SeasonCalculator(engine)
    events = calc.get_seasons(start_year, end_year)
    processed_events = []
    if events:
        for e in events:
            if 'calendar' not in e:
                e['calendar'] = 'Astro: Seasons'
            processed_events.append(e)
    logger.info(f"  [Task] Seasons finished ({len(processed_events)} events).")
    return processed_events

def task_generate_moon_features(start_year, end_year):
    logger.info("  [Task] Moon Features started...")
    engine = AstroEngine()
    calc = MoonFeatureCalculator(engine)
    events = calc.get_moon_features(start_year, end_year)
    processed_events = []
    if events:
        for e in events:
            if 'calendar' not in e:
                e['calendar'] = 'Astro: Moon Features'
            processed_events.append(e)
    logger.info(f"  [Task] Moon Features finished ({len(processed_events)} events).")
    return processed_events

def task_generate_zodiac(start_year, end_year, bodies):
    logger.info("  [Task] Zodiac Ingress started...")
    engine = AstroEngine()
    calc = ZodiacCalculator(engine)
    events = calc.get_zodiac_ingress(start_year, end_year, bodies)
    logger.info(f"  [Task] Zodiac Ingress finished ({len(events) if events else 0} events).")
    return events or []

def task_generate_moon_phases(start_year, end_year):
    logger.info("  [Task] Moon Phases started...")
    engine = AstroEngine()
    calc = MoonPhaseCalculator(engine)
    events = calc.get_moon_phases(start_year, end_year)
    logger.info(f"  [Task] Moon Phases finished ({len(events) if events else 0} events).")
    return events or []

def task_generate_calendar_year(start_year, end_year):
    logger.info("  [Task] Calendar Year Progress started...")
    engine = AstroEngine()
    calc = YearProgressCalculator(engine)
    events = calc.get_calendar_year_events(start_year, end_year)
    logger.info(f"  [Task] Calendar Year Progress finished ({len(events) if events else 0} events).")
    return events or []

def task_generate_solar_year(start_year, end_year):
    logger.info("  [Task] Solar Year Progress started...")
    engine = AstroEngine()
    calc = YearProgressCalculator(engine)
    events = calc.get_solar_year_events(start_year, end_year)
    logger.info(f"  [Task] Solar Year Progress finished ({len(events) if events else 0} events).")
    return events or []

def task_generate_patterns(start_year, end_year, bodies):
    logger.info("  [Task] Patterns (Square/Trine) started...")
    engine = AstroEngine()
    calc = PatternCalculator(engine)
    events = calc.get_square_trine_patterns(start_year, end_year, bodies)
    logger.info(f"  [Task] Patterns finished ({len(events) if events else 0} events).")
    return events or []


def main():
    logger.info("Starting Astro GCal Generator (Parallel Mode)...")
    logger.info(f"Output Mode: {config.OUTPUT_MODE}")
    
    # 2. Resolve Location
    lat, lon = config.OBSERVER_LAT, config.OBSERVER_LON
    location_name = config.OBSERVER_CITY if config.OBSERVER_CITY else "Local Location"
    
    if config.OBSERVER_CITY:
        from utils import geocoding
        logger.info(f"Resolving location for '{config.OBSERVER_CITY}'...")
        coords = geocoding.get_lat_lon(config.OBSERVER_CITY)
        if coords:
            lat, lon = coords
            logger.info(f"  Found coordinates: {lat}, {lon}")
        else:
            logger.warning(f"  Could not find '{config.OBSERVER_CITY}'. Using default: {lat}, {lon}")
            
    # 3. Generate Events in Parallel
    all_events = []
    
    with concurrent.futures.ProcessPoolExecutor() as executor:
        futures = {}
        
        # Submit tasks
        if config.ENABLE_ECLIPSES:
            futures[executor.submit(task_generate_eclipses, config.START_YEAR, config.END_YEAR)] = 'Eclipses'
            
        if config.ENABLE_ASPECTS:
            # Geocentric
            futures[executor.submit(
                task_generate_aspects, 
                config.START_YEAR, config.END_YEAR, 
                config.CONJUNCTION_PLANETS, config.ASPECTS_TO_TRACK, config.ASPECT_ORB, 'earth'
            )] = 'Aspects Geo'
            
            # Heliocentric
            futures[executor.submit(
                task_generate_aspects, 
                config.START_YEAR, config.END_YEAR, 
                config.CONJUNCTION_PLANETS, config.ASPECTS_TO_TRACK, config.ASPECT_ORB, 'sun'
            )] = 'Aspects Helio'
            
        if config.ENABLE_ALMANAC:
            futures[executor.submit(
                task_generate_almanac,
                config.START_YEAR, config.END_YEAR,
                config.ALMANAC_BODIES, location_name, lat, lon
            )] = 'Almanac'
            
        if config.ENABLE_RETROGRADE:
            futures[executor.submit(
                task_generate_retrograde,
                config.START_YEAR, config.END_YEAR, config.RETROGRADE_PLANETS
            )] = 'Retrograde'
            
        if getattr(config, 'ENABLE_SEASONS', False):
            futures[executor.submit(task_generate_seasons, config.START_YEAR, config.END_YEAR)] = 'Seasons'
            
        if getattr(config, 'ENABLE_MOON_FEATURES', False):
            futures[executor.submit(task_generate_moon_features, config.START_YEAR, config.END_YEAR)] = 'Moon Features'
            
        if getattr(config, 'ENABLE_ZODIAC', False):
            futures[executor.submit(
                task_generate_zodiac, config.START_YEAR, config.END_YEAR, config.ALMANAC_BODIES
            )] = 'Zodiac'
            
        if getattr(config, 'ENABLE_MOON_PHASES', False):
            futures[executor.submit(task_generate_moon_phases, config.START_YEAR, config.END_YEAR)] = 'Moon Phases'
            
        if getattr(config, 'ENABLE_CALENDAR_YEAR_PROGRESS', False):
            futures[executor.submit(task_generate_calendar_year, config.START_YEAR, config.END_YEAR)] = 'Calendar Year'
            
        if getattr(config, 'ENABLE_SOLAR_YEAR_PROGRESS', False):
            futures[executor.submit(task_generate_solar_year, config.START_YEAR, config.END_YEAR)] = 'Solar Year'
            
        if getattr(config, 'ENABLE_PATTERNS', False):
            futures[executor.submit(
                task_generate_patterns, config.START_YEAR, config.END_YEAR, config.ALMANAC_BODIES
            )] = 'Patterns'

        logger.info(f"Submitted {len(futures)} tasks to process pool.")
        
        # Collect results
        for future in concurrent.futures.as_completed(futures):
            task_name = futures[future]
            try:
                events = future.result()
                all_events.extend(events)
            except Exception as e:
                logger.error(f"Task '{task_name}' generated an exception: {e}")
                import traceback
                traceback.print_exc()

    # 4. Output Logic
    logger.info(f"Total Events Generated: {len(all_events)}")
    
    if config.OUTPUT_MODE == 'json':
        import json
        output_file = 'demo_output.json'
        json_events = []
        for e in all_events:
            e_copy = e.copy()
            for k, v in e_copy.items():
                if hasattr(v, 'isoformat'):
                    e_copy[k] = v.isoformat()
            json_events.append(e_copy)
            
        with open(output_file, 'w') as f:
            json.dump(json_events, f, indent=2)
        logger.info(f"Written events to '{output_file}'.")

    elif config.OUTPUT_MODE == 'ics':
        # Group by calendar
        events_by_cal = defaultdict(list)
        for e in all_events:
            cal_name = e.get('calendar', 'Astro: General')
            events_by_cal[cal_name].append(e)
            
        if config.START_YEAR == config.END_YEAR:
            file_prefix = str(config.START_YEAR)
        else:
            file_prefix = f"{config.START_YEAR}-{config.END_YEAR}"

        logger.info("Exporting ICS files...")
        for cal_name, evts in events_by_cal.items():
            ics_writer.write_ics(cal_name, evts, file_prefix=file_prefix)
    
    else:
        logger.error(f"Unknown output mode: {config.OUTPUT_MODE}")

if __name__ == "__main__":
    main()


