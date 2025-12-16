import datetime

# Year range to generate events for
START_YEAR = datetime.date.today().year
END_YEAR = START_YEAR # Generate for current year only by default

# Output Mode
# Options: 'ics' (Export Files), 'json' (Demo Output)
OUTPUT_MODE = 'ics'

# Observer Location
# You can specify a City Name (e.g., "New York, USA", "London, UK")
# This will be resolved to coordinates automatically.
OBSERVER_CITY = "New York, USA"

# Fallback/Default coordinates (if city lookup fails)
# Default is New York approx.
OBSERVER_LAT = 40.7128
OBSERVER_LON = -74.0060

# Enabled Event Types
ENABLE_ECLIPSES = True
ENABLE_ALMANAC = True # Rise/Set times
ENABLE_ASPECTS = True


# Aspects to track
ASPECTS_TO_TRACK = [
    'conjunction', 
    'square', 
    'trine', 
    'opposition', 
    'sextile', 
    'quintile', 
    'biquintile'
]

# Almanac Bodies
ALMANAC_BODIES = [
    'Sun', 'Moon', 'Mercury', 'Venus', 'Mars', 
    'Jupiter', 'Saturn', 'Uranus', 'Neptune', 'Pluto'
]

# Retrograde
ENABLE_RETROGRADE = True
RETROGRADE_PLANETS = [
    'Mercury', 'Venus', 'Mars', 'Jupiter', 
    'Saturn', 'Uranus', 'Neptune', 'Pluto'
]

ASPECT_ORB = 1.0 # degrees

# Calendar Names
CALENDAR_NAMES = {
    'solar_eclipse': 'Astro: Solar Eclipses',
    'lunar_eclipse': 'Astro: Lunar Eclipses',
    'almanac': 'Astro: Almanac (Rise/Set)',
    'seasons': 'Astro: Seasons',
    'moon_features': 'Astro: Moon Features',
    'aspect': 'Astro: Planetary Aspects' # Shared calendar for aspects
}

ENABLE_SEASONS = True
ENABLE_MOON_FEATURES = True
ENABLE_ZODIAC = True
ENABLE_MOON_PHASES = True
ENABLE_CALENDAR_YEAR_PROGRESS = True
ENABLE_SOLAR_YEAR_PROGRESS = True
ENABLE_PATTERNS = True

# Specific settings
CONJUNCTION_PLANETS = ['mars', 'jupiter', 'saturn', 'venus']
