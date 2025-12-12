import config
from astro import eclipses, almanac
from collections import defaultdict
import sys
import datetime

def main():
    print("Starting Astro GCal Generator...")
    
    print(f"Output Mode: {config.OUTPUT_MODE}")
    
    # 2. Resolve Location
    lat, lon = config.OBSERVER_LAT, config.OBSERVER_LON
    if config.OBSERVER_CITY:
        from utils import geocoding
        print(f"Resolving location for '{config.OBSERVER_CITY}'...")
        coords = geocoding.get_lat_lon(config.OBSERVER_CITY)
        if coords:
            lat, lon = coords
            print(f"  Found coordinates: {lat}, {lon}")
        else:
            print(f"  Could not find '{config.OBSERVER_CITY}'. Using default: {lat}, {lon}")
    
    # 3. Generate Events
    all_events = []
    
    # --- Eclipses ---
    if config.ENABLE_ECLIPSES:
        print("Processing Eclipses...")
        events = eclipses.get_eclipses(config.START_YEAR, config.END_YEAR)
        if events:
            # Type to Calendar Mapping
            for e in events:
                if e['type'] == 'solar_eclipse':
                    e['calendar'] = config.CALENDAR_NAMES['solar_eclipse']
                elif e['type'] == 'lunar_eclipse':
                    e['calendar'] = config.CALENDAR_NAMES['lunar_eclipse']
                all_events.append(e)
            print(f"  Found {len(events)} eclipse events.")
        else:
            print("  No eclipses found.")

    # --- Aspects ---
    if config.ENABLE_ASPECTS:
        print("Processing Planetary Aspects...")
        from astro import aspects
        
        systems = ['geocentric', 'heliocentric']
        
        for sys_name in systems:
            print(f"  Generating {sys_name} aspects...")
            events = aspects.get_aspects(
                config.START_YEAR, config.END_YEAR, 
                planets_to_check=config.CONJUNCTION_PLANETS,
                aspects_to_check=config.ASPECTS_TO_TRACK,
                orb=config.ASPECT_ORB,
                center_body=sys_name
            )
            
            if events:
                for e in events:
                    # Heliocentric Modifications
                    if sys_name == 'heliocentric':
                        e['summary'] = f"{e['summary']} (Helio)"
                        e['description'] = f"(Heliocentric) {e['description']}"
                        
                        # Calendar Logic
                        if 'participants' in e:
                             for p in e['participants']:
                                 p_clean = p.replace(' barycenter', '').title()
                                 # We need a new dictionary to not reference original
                                 e_copy = e.copy()
                                 e_copy['calendar'] = f"Astro: {p_clean} Helio"
                                 all_events.append(e_copy)
                        else:
                             e['calendar'] = "Astro: Aspects Helio"
                             all_events.append(e)

                    else:
                        # Geocentric Logic (Standard)
                        if 'participants' in e:
                            for p in e['participants']:
                                p_clean = p.replace(' barycenter', '').title()
                                e_copy = e.copy()
                                e_copy['calendar'] = f"Astro: {p_clean} Geo"
                                all_events.append(e_copy)
                        else:
                            e['calendar'] = "Astro: Aspects Geo"
                            all_events.append(e)
                print(f"    Found {len(events)} {sys_name} events.")
            else:
                 print(f"    No {sys_name} aspects found.")

    # --- Almanac ---
    if config.ENABLE_ALMANAC:
        print("Processing Almanac (Rise/Set/MC/IC)...")
        events = almanac.get_almanac_events(
            config.START_YEAR, config.END_YEAR,
            lat, lon,
            bodies=config.ALMANAC_BODIES,
            location_name=config.OBSERVER_CITY if config.OBSERVER_CITY else "Local Location"
        )
        if events:
            for e in events:
                parts = e['summary'].split()
                planet = parts[0] if parts else "Unknown"
                if "(Rise-Set)" in e['summary']:
                     e['calendar'] = f"Astro: {planet} Divisions"
                else:
                     e['calendar'] = f"Astro: {planet} Almanac"
                all_events.append(e)
            print(f"  Found {len(events)} almanac events.")
        else:
            print("  No almanac events found.")

    # --- Retrograde ---
    if config.ENABLE_RETROGRADE:
        print("Processing Retrograde Motion...")
        from astro import retrograde
        events = retrograde.get_retrograde_full(
            config.START_YEAR, config.END_YEAR,
            config.RETROGRADE_PLANETS
        )
        if events:
             for e in events:
                 cal = e.get('calendar', 'Astro: Retrograde')
                 # If it's a planet-specific calendar (e.g. Astro: Mars), append Geo
                 if cal.startswith('Astro: ') and not cal.endswith(' Geo') and 'Retrograde' not in cal:
                      e['calendar'] = f"{cal} Geo"
                 # Capture just in case
                 elif 'calendar' not in e:
                      e['calendar'] = 'Astro: Retrograde Geo'
                 
                 all_events.append(e)
             print(f"  Found {len(events)} retrograde events.")
        else:
             print("  No retrograde events found.")

    # --- Seasons ---
    if getattr(config, 'ENABLE_SEASONS', False):
        print("Processing Seasonal Events...")
        from astro import seasons
        events = seasons.get_seasons(config.START_YEAR, config.END_YEAR)
        if events:
            for e in events:
                if 'calendar' not in e:
                    e['calendar'] = 'Astro: Seasons'
                all_events.append(e)
            print(f"  Found {len(events)} seasonal events.")
        else:
            print("  No seasonal events found.")

    # --- Moon Features (Nodes/Extremes) ---
    if getattr(config, 'ENABLE_MOON_FEATURES', False):
        print("Processing Moon Features (Nodes/Extremes)...")
        from astro import moon_features
        events = moon_features.get_moon_features(config.START_YEAR, config.END_YEAR)
        if events:
            for e in events:
                if 'calendar' not in e:
                    e['calendar'] = 'Astro: Moon Features'
                all_events.append(e)
            print(f"  Found {len(events)} moon feature events.")
        else:
            print("  No moon feature events found.")

    # --- Zodiac Ingress ---
    if getattr(config, 'ENABLE_ZODIAC', False):
        print("Processing Zodiac Ingress...")
        from astro import zodiac
        events = zodiac.get_zodiac_ingress(
            config.START_YEAR, config.END_YEAR,
            bodies=config.ALMANAC_BODIES # Reuse list of major bodies
        )
        if events:
            for e in events:
                all_events.append(e)
            print(f"  Found {len(events)} zodiac ingress events.")
        else:
            print("  No zodiac ingress events found.")

    # --- Moon Phases ---
    if getattr(config, 'ENABLE_MOON_PHASES', False):
        print("Processing Moon Phases...")
        from astro import moon_phases
        events = moon_phases.get_moon_phases(config.START_YEAR, config.END_YEAR)
        if events:
            for e in events:
                all_events.append(e)
            print(f"  Found {len(events)} moon phase events.")
        else:
            print("  No moon phase events found.")

    # 4. Output Logic
    print(f"\nTotal Events Generated: {len(all_events)}")
    
    # Convert datetimes to isoformat strings if JSON output
    if config.OUTPUT_MODE == 'json':
        import json
        output_file = 'demo_output.json'
        # Deep copy
        json_events = []
        for e in all_events:
            e_copy = e.copy()
            for k, v in e_copy.items():
                if hasattr(v, 'isoformat'):
                    e_copy[k] = v.isoformat()
            json_events.append(e_copy)
            
        with open(output_file, 'w') as f:
            json.dump(json_events, f, indent=2)
        print(f"Written events to '{output_file}'.")

    elif config.OUTPUT_MODE == 'ics':
        from utils import ics_writer
        # Group by calendar
        events_by_cal = defaultdict(list)
        for e in all_events:
            cal_name = e.get('calendar', 'Astro: General')
            events_by_cal[cal_name].append(e)
            
        print("Exporting ICS files...")
        for cal_name, evts in events_by_cal.items():
            ics_writer.write_ics(cal_name, evts)
    
    else:
        print(f"Unknown output mode: {config.OUTPUT_MODE}")

if __name__ == "__main__":
    main()

