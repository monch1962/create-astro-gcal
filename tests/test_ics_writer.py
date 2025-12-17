import os
import pytest
from utils.ics_writer import write_ics
from datetime import datetime

def test_write_ics_splitting(tmp_path):
    # Mock events
    events = []
    base_time = datetime(2024, 1, 1, 12, 0)
    for i in range(2000):
        events.append({
            'summary': f'Event {i}',
            'start_time': base_time,
            'duration_minutes': 60,
            'description': 'Test description'
        })
        
    output_dir = tmp_path / "ics_out"
    cal_name = "Test Calendar"
    
    # Run writer
    write_ics(cal_name, events, output_dir=str(output_dir), file_prefix="TEST")
    
    # Check output
    # Expecting Part1 and Part2 (since 2000 > 1500)
    files = list(output_dir.glob("*.ics"))
    files.sort()
    
    assert len(files) == 2
    assert "TEST_Test_Calendar_Part1.ics" in [f.name for f in files]
    assert "TEST_Test_Calendar_Part2.ics" in [f.name for f in files]
    
    # Verify content roughly
    with open(files[0], 'r') as f:
        content = f.read()
        assert "Event 0" in content
        assert "Event 1499" in content
        assert "Event 1500" not in content # Should be in part 2

    with open(files[1], 'r') as f:
        content = f.read()
        assert "Event 1500" in content
        assert "Event 1999" in content

def test_write_ics_small(tmp_path):
    events = [{'summary': 'Single', 'start_time': datetime(2024,1,1)}]
    output_dir = tmp_path / "ics_out_small"
    write_ics("SmallCal", events, output_dir=str(output_dir))
    
    files = list(output_dir.glob("*.ics"))
    assert len(files) == 1
    assert "SmallCal.ics" in [f.name for f in files] # No Part suffix
    
def test_write_ics_empty(tmp_path):
    events = []
    output_dir = tmp_path / "ics_out_empty"
    write_ics("EmptyCal", events, output_dir=str(output_dir))
    
    files = list(output_dir.glob("*.ics"))
    assert len(files) == 1
    assert "EmptyCal.ics" in [f.name for f in files]
