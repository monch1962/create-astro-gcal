from astro.engine import AstroEngine

_ENGINE_INSTANCE = None

def get_shared_engine():
    """
    Returns a process-global singleton instance of AstroEngine.
    This prevents reloading Ephemeris data for every task in a worker process.
    """
    global _ENGINE_INSTANCE
    if _ENGINE_INSTANCE is None:
        _ENGINE_INSTANCE = AstroEngine()
    return _ENGINE_INSTANCE

def reset_engine():
    """
    Resets the global engine instance (useful for testing).
    """
    global _ENGINE_INSTANCE
    _ENGINE_INSTANCE = None
