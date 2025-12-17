from ics import Calendar, Event
import os
from datetime import datetime

def write_ics(calendar_name, events, output_dir='ics_calendars', file_prefix=''):
    """
    Writes a list of event dictionaries to ICS file(s).
    Splits into multiple files if event count exceeds limit to ensure <1MB file size.
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    # Heuristic: ~600 bytes per event average. 1MB limit.
    # 1500 events * 600 bytes = 900KB.
    CHUNK_SIZE = 1500
    
    total_events = len(events)
    if total_events == 0:
        chunks = [[]]
    else:
        chunks = [events[i:i + CHUNK_SIZE] for i in range(0, total_events, CHUNK_SIZE)]
    
    # Sanitize filename base
    safe_name = calendar_name.replace(':', '').replace('/', '-').replace(' ', '_')
    
    for i, chunk in enumerate(chunks):
        c = Calendar()
        c.creator = "Astro GCal Generator"
        
        for e in chunk:
            evt = Event()
            evt.name = e.get('summary', 'Unknown Event')
            evt.begin = e.get('start_time')
            
            # Duration handling
            duration = e.get('duration_minutes', 0)
            if duration > 0:
                from datetime import timedelta
                evt.end = evt.begin + timedelta(minutes=duration)
            else:
                evt.end = evt.begin
                
            evt.description = e.get('description', '')
            c.events.add(evt)
            
        # Determine filename
        if len(chunks) > 1:
            suffix = f"_Part{i+1}"
        else:
            suffix = ""
            
        if file_prefix:
            filename = os.path.join(output_dir, f"{file_prefix}_{safe_name}{suffix}.ics")
        else:
            filename = os.path.join(output_dir, f"{safe_name}{suffix}.ics")
        
        with open(filename, 'w') as f:
            f.writelines(c.serialize_iter())
            
        print(f"  Exported {len(chunk)} events to {filename}")
