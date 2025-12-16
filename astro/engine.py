from skyfield.api import load

class AstroEngine:
    def __init__(self, ephemeris_file='de421.bsp'):
        self.ts = load.timescale()
        self.eph = load(ephemeris_file)
