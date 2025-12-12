from ics import Calendar, Event
import os
from datetime import datetime

def write_ics(calendar_name, events, output_dir='ics_calendars'):
    """
    Writes a list of event dictionaries to an ICS file.
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    c = Calendar()
    c.creator = "Astro GCal Generator"
    
    for e in events:
        evt = Event()
        evt.name = e.get('summary', 'Unknown Event')
        evt.begin = e.get('start_time')
        
        # Duration handling
        # If duration_minutes is 0, it might be a point event
        duration = e.get('duration_minutes', 0)
        if duration > 0:
            # ics library handles duration, or we can set end
            # evt.duration = timedelta(minutes=duration) 
            # Note: ics library usually prefers direct datetime objects for begin/end
            from datetime import timedelta
            evt.end = evt.begin + timedelta(minutes=duration)
        else:
            # Point event
            pass
            
        evt.description = e.get('description', '')
        
        c.events.add(evt)
        
    # Sanitize filename
    safe_name = calendar_name.replace(':', '').replace('/', '-').replace(' ', '_')
    filename = os.path.join(output_dir, f"{safe_name}.ics")
    
    with open(filename, 'w') as f:
        f.writelines(c.serialize_iter())
        
    print(f"  Exported {len(events)} events to {filename}")
