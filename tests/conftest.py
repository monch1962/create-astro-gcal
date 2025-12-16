import pytest
import sys
import os

# Add project root to sys.path so we can import 'astro' module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from astro.engine import AstroEngine

@pytest.fixture(scope="session")
def engine():
    """
    Shared AstroEngine instance to avoid reloading Ephemeris (17MB) 
    multiple times. Scope is session-wide.
    """
    print("\n[Fixture] Initializing AstroEngine...")
    return AstroEngine()
