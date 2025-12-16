def test_engine_initialization(engine):
    assert engine.eph is not None
    assert engine.ts is not None
    # Verify we can load 'earth'
    assert engine.eph['earth'] is not None
