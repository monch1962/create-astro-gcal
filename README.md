# Astro Calendar Generator

A powerful Python tool that calculates precise astronomical and astrological events and pushes them to dedicated **ICS** files for easy import.

## Features

### 1. Planetary Almanac
Tracks daily movement events for **Sun, Moon, Mercury, Venus, Mars, Jupiter, Saturn, Uranus, Neptune, and Pluto**.
*   **Events**: Rise, Set, Midheaven (MC), and Nadir (IC).
*   **Calendars**: `Astro: {Planet} Almanac`

### 2. Time Divisions (Planetary Hours)
Calculates special intervals dividing the planetary day (Rise to Set) into specific fractions.
*   **Divisions**: 
    *   **Thirds**: 1/3, 2/3
    *   **Eighths**: 1/8 to 7/8
    *   **Nineteenths**: 1/19 to 18/19
*   **Calendars**: `Astro: {Planet} Divisions`

### 3. Planetary Aspects
Calculates precise geometric angles between planets (Simultaneous **Geocentric** and **Heliocentric**).
*   **Aspects**: Conjunction (0°), Sextile (60°), Quintile (72°), Square (90°), Trine (120°), Biquintile (144°), Opposition (180°).
*   **Precision**: Calculates the exact minute the aspect enters and leaves a **1.0° Orb**, providing accurate durations.
*   **Calendars**: `Astro: {Planet} Geo` and `Astro: {Planet} Helio`

### 4. Eclipses
Comprehensive detection of Solar and Lunar eclipses.
*   **Solar**: Total and Partial Solar Eclipses.
*   **Lunar**: Total, Partial, and Penumbral Lunar Eclipses.
*   **Duration**: Calculated based on the exact start and end contacts.
*   **Calendars**: `Astro: Solar Eclipses`, `Astro: Lunar Eclipses`

### 5. Retrograde Motion
Tracks the apparent retrograde motion of planets.
*   **Events**: Retrograde Station (starts moving backwards), Direct Station (starts moving forwards), Shadow Exit (leaves the retrograde zone).
*   **Calendars**: `Astro: {Planet}`

### 6. Seasonal Events
Tracks the key solar points of the year.
*   **Events**: Vernal Equinox, Summer Solstice, Autumnal Equinox, Winter Solstice.
*   **Calendar**: `Astro: Seasons`

### 7. Moon Features
Tracks specific Lunar events and phases.
*   **Events**: North/South Nodes (Ecliptic Crossings), Lunar Max North/South (Declination Extremes), **Moon Phases** (New, Full, 1st/3rd Quarter).
*   **Calendar**: `Astro: Moon Features` and `Astro: Moon Phases`

### 8. Zodiac Ingress
Tracks when planets enter a new Zodiac Sign (Aries, Taurus, etc.).
*   **Events**: Planet Enters [Sign].
*   **Calendar**: `Astro: {Planet} Zodiac`

### 9. Year Progress
Dividers for both the Calendar Year (Jan 1) and Solar Year (Vernal Equinox).
*   **Events**: 1/16th Intervals (e.g., 6.25%, 50%), Square Number Days (Day 1, 4, 9... 361).
*   **Calendars**: `Astro: Calendar Year Progress` and `Astro: Solar Year Progress`

### 10. Planetary Patterns
Identifies complex aspect patterns.
*   **Events**: Planet is simultaneously Square one body and Trine another.
*   **Calendar**: `Astro: Square and Trine`

---

## Installation

1.  **Clone the repository**:
    ```bash
    git clone https://github.com/yourusername/astro-gcal.git
    cd astro-gcal
    ```

2.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```
    ```

---

## Configuration

All settings are managed in `config.py`.

*   **Location**: Set `OBSERVER_CITY` (e.g., "New York, USA") to automatically resolve coordinates.
*   **Date Range**: `START_YEAR` and `END_YEAR`.
*   **Output Mode**: Set `OUTPUT_MODE` to `'ics'` (Export Files) or `'json'` (Demo Data).
*   **Event Toggles**: Enable/Disable specific features (`ENABLE_ALMANAC`, `ENABLE_ASPECTS`, etc.).

---

## Usage

Run the main script:

```bash
python main.py
```

## Output Files
The script generates `.ics` files in the `ics_calendars/` directory.
Each file is prefixed with the generated year or range (e.g., `2025_Astro_...` or `2025-2027_Astro_...`).
These can be imported into Google Calendar, Apple Calendar, or Outlook.
*   **Demo/JSON Mode**: Check `demo_output.json` for raw event data.

## Calendars Generated

The application organizes events into specific calendars to keep your view clean:

| Calendar Name | Content |
| :--- | :--- |
| **Astro: Seasons** | Equinoxes and Solstices |
| **Astro: Solar Eclipses** | Solar Eclipses |
| **Astro: Lunar Eclipses** | Lunar Eclipses |
| **Astro: Moon Features** | North/South Nodes, Declination Extremes |
| **Astro: Moon Phases** | New, Full, First/Last Quarter |
| **Astro: {Planet} Almanac** | Rise, Set, MC, IC |
| **Astro: {Planet} Divisions** | 1/3, 1/8, 1/19 Intervals |
| **Astro: {Planet} Geo** | Geocentric Aspects, Retrograde Stations |
| **Astro: {Planet} Helio** | Heliocentric Aspects |
| **Astro: {Planet} Zodiac** | Zodiac Sign Entries |
| **Astro: Calendar Year Progress** | Jan 1 Start - 1/16ths, Square Days |
| **Astro: Solar Year Progress** | Equinox Start - 1/16ths, Square Days |
| **Astro: Square and Trine** | Simultaneous Square & Trine Overlaps |

*Note: Replace {Planet} with Mars, Venus, Jupiter, etc.*
