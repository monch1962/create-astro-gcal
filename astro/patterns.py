from astro.aspects import AspectCalculator
from collections import defaultdict
import datetime

class PatternCalculator:
    """
    Identifies compound astrological patterns.

    Purpose:
        - Detects complex patterns formed by multiple aspects occurring simultaneously.
        - Currently supports "Square + Trine" pattern: One planet simultaneously Square a second AND Trine a third.

    Usage:
        calc = PatternCalculator(engine)
        events = calc.get_square_trine_patterns(2024, 2024, bodies=['Mars', 'Jupiter', 'Saturn'])
        
        # Output:
        #   List of dictionaries, e.g.:
        #   [
        #     {'type': 'pattern_square_trine', 'summary': 'Mars: Sq Jupiter & Tri Saturn', 'start_time': <datetime>, 'duration_minutes': <int>, ...},
        #   ]
    """
    def __init__(self, engine):
        self.engine = engine
        self.aspect_calc = AspectCalculator(engine)

    def get_square_trine_patterns(self, year_start, year_end, bodies):
        """
        Finds occurrences where a body is simultaneously Square one planet and Trine another.
        """
        # 1. Fetch ALL Square and Trine aspects for these bodies
        # We use orb=1.0 from config logic
        raw_aspects = self.aspect_calc.get_aspects(
            year_start, 
            year_end, 
            planets_to_check=bodies, 
            aspects_to_check=['square', 'trine'],
            orb=1.0, 
            center_body='earth'
        )
        
        # 2. Organize by Body
        aspects_by_body = defaultdict(list)
        
        for event in raw_aspects:
            p1, p2 = event['participants']
            aspect_type = event['summary'].split(':')[0].lower() # 'square' or 'trine'
            
            # Add entry for p1
            aspects_by_body[p1].append({
                'partner': p2,
                'type': aspect_type,
                'start': event['start_time'],
                'end': event['start_time'] + datetime.timedelta(minutes=event['duration_minutes']),
                'summary': event['summary']
            })
            
            # Add entry for p2
            aspects_by_body[p2].append({
                'partner': p1,
                'type': aspect_type,
                'start': event['start_time'],
                'end': event['start_time'] + datetime.timedelta(minutes=event['duration_minutes']),
                'summary': event['summary']
            })
            
        pattern_events = []
        
        # 3. Find Overlaps
        for body, aspect_list in aspects_by_body.items():
            squares = [a for a in aspect_list if 'square' in a['type']]
            trines = [a for a in aspect_list if 'trine' in a['type']]
            
            for sq in squares:
                for tr in trines:
                    # Check Overlap
                    start_overlap = max(sq['start'], tr['start'])
                    end_overlap = min(sq['end'], tr['end'])
                    
                    if start_overlap < end_overlap:
                        # Found pattern!
                        duration = (end_overlap - start_overlap).total_seconds() / 60.0
                        
                        partner_sq = sq['partner']
                        partner_tr = tr['partner']
                        
                        summary = f"{body.title()}: Sq {partner_sq.title()} & Tri {partner_tr.title()}"
                        description = (f"{body.title()} is simultaneously:\n"
                                       f"- Square {partner_sq.title()}\n"
                                       f"- Trine {partner_tr.title()}\n"
                                       f"Overlap Duration: {int(duration)} mins.")
                        
                        pattern_events.append({
                            'type': 'pattern_square_trine',
                            'summary': summary,
                            'start_time': start_overlap,
                            'duration_minutes': int(duration),
                            'description': description,
                            'calendar': 'Astro: Square and Trine'
                        })
                        
        # Sort by time
        pattern_events.sort(key=lambda x: x['start_time'])
        
        return pattern_events
