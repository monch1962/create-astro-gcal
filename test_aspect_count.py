from astro import aspects
from config import START_YEAR, END_YEAR, CONJUNCTION_PLANETS, ASPECTS_TO_TRACK, ASPECT_ORB
import time

def run_test():
    print(f"Testing Aspect Count for Year: {START_YEAR}")
    
    # 1. Test User's Current Config
    print(f"\n--- Test 1: User's Current Config ---")
    print(f"Planets: {CONJUNCTION_PLANETS}")
    t0 = time.time()
    events_1 = aspects.get_aspects(
        START_YEAR, END_YEAR, 
        CONJUNCTION_PLANETS, 
        ASPECTS_TO_TRACK, 
        orb=ASPECT_ORB, 
        center_body='earth'
    )
    t1 = time.time()
    print(f"Found {len(events_1)} events. Time: {t1-t0:.2f}s")
    
    # 2. Test Expanded Set (Add Sun, Moon)
    print(f"\n--- Test 2: Expanded Set (Sun, Moon, Mercury, Venus, Mars) ---")
    expanded_planets = ['Sun', 'Moon', 'Mercury', 'Venus', 'Mars']
    print(f"Planets: {expanded_planets}")
    t0 = time.time()
    events_2 = aspects.get_aspects(
        START_YEAR, END_YEAR, 
        expanded_planets, 
        ASPECTS_TO_TRACK, 
        orb=ASPECT_ORB, 
        center_body='earth'
    )
    t1 = time.time()
    print(f"Found {len(events_2)} events. Time: {t1-t0:.2f}s")
    
    # Check Moon frequency specifically
    moon_events = [e for e in events_2 if 'Moon' in e['participants'] or 'moon' in e['participants']]
    print(f"Moon events in Test 2: {len(moon_events)}")

if __name__ == "__main__":
    run_test()
