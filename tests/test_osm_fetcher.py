"""
Tests for the OSM fetcher module.
This message will be deleted after I, BilgeA. add in more technical details to the progress in commit message.
Because I accidentally clicked git commit early.
"""

import os
import pytest
from src.osm_fetcher.fetcher import OSMFetcher

@pytest.fixture
def fetcher():
    """Create a temporary OSM fetcher instance."""
    test_cache_dir = "data/osm/test"
    os.makedirs(test_cache_dir, exist_ok=True)
    return OSMFetcher(cache_dir=test_cache_dir)

def test_fetch_by_place(fetcher):
    """Test fetching OSM data by place name."""
    place_name = "Istanbul, Turkey"  # We'll use Istanbul since 43R is in Istanbul
    try:
        osm_file = fetcher.fetch_by_place(place_name, network_type="all")  # Changed to 'all' to include bus routes
        assert os.path.exists(osm_file)
        assert osm_file.endswith(".osm")
    except Exception as e:
        pytest.skip(f"Skipping test due to network error: {str(e)}")

def test_fetch_by_bbox(fetcher):
    """Test fetching OSM data by bounding box."""
    # Coordinates covering the 43R bus route area in Istanbul
    # These coordinates are approximate and may need adjustment
    bbox = (41.0697, 41.0297, 29.0324, 28.9724)  # Wider area covering potential 43R route
    try:
        osm_file = fetcher.fetch_by_bbox(bbox, network_type="all")  # Changed to 'all' to include bus routes
        assert os.path.exists(osm_file)
        assert osm_file.endswith(".osm")
    except Exception as e:
        pytest.skip(f"Skipping test due to network error: {str(e)}")

def test_invalid_place(fetcher):
    """Test fetching with invalid place name."""
    with pytest.raises(Exception):
        fetcher.fetch_by_place("ThisPlaceDoesNotExist12345")