from skyfield.api import load

class AstroEngine:
    """
    Central engine for Skyfield astronomy calculations.
    
    Purpose:
        - Loads and caches heavy astronomical data files (Ephemeris 'de421.bsp').
        - Initializes the TimeScale object used for all time conversions.
        - Acts as the single source of truth for 'ts' and 'eph' to avoid redundant loading
          and ensure consistency across different calculators.

    Usage:
        from astro.engine import AstroEngine
        
        # Initialize once (shared across application)
        engine = AstroEngine()
        
        # Access properties
        ts = engine.ts
        eph = engine.eph
        
        # Pass 'engine' to other calculators
        # calc = SomeCalculator(engine)
        
        # Output:
        #   An initialized engine instance with .ts (Timescale) and .eph (Ephemeris) attributes.
    """
    def __init__(self, ephemeris_file='de421.bsp'):
        self.ts = load.timescale()
        self.eph = load(ephemeris_file)
