from skyfield.api import load
from skyfield import almanac

class MoonPhaseCalculator:
    def __init__(self, engine):
        self.engine = engine

    def get_moon_phases(self, year_start, year_end):
        """
        Generates events for New Moon, First Quarter, Full Moon, and Last Quarter.
        """
        ts = self.engine.ts
        eph = self.engine.eph
        
        t0 = ts.utc(year_start, 1, 1)
        t1 = ts.utc(year_end + 1, 1, 1)
        
        # 0 = New Moon, 1 = First Quarter, 2 = Full Moon, 3 = Last Quarter
        f = almanac.moon_phases(eph)
        times, phases = almanac.find_discrete(t0, t1, f)
        
        phase_names = {
            0: 'New Moon',
            1: 'First Quarter Moon',
            2: 'Full Moon',
            3: 'Last Quarter Moon'
        }
        
        events_list = []
        
        for t, phase_code in zip(times, phases):
            name = phase_names.get(phase_code, "Unknown Phase")
            dt = t.utc_datetime()
            
            events_list.append({
                'type': 'moon_phase',
                'summary': name,
                'start_time': dt,
                'duration_minutes': 0, # Point event
                'description': f"{name}.",
                'calendar': 'Astro: Moon Phases'
            })
            
        return events_list
