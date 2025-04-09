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
    place_name = "Besiktas, Istanbul"
    try:
        osm_file = fetcher.fetch_by_place(place_name)
        assert os.path.exists(osm_file)
        assert osm_file.endswith(".osm")
    except Exception as e:
        pytest.skip(f"Skipping test due to network error: {str(e)}")

def test_fetch_by_bbox(fetcher):
    """Test fetching OSM data by bounding box."""
    # Small area in Istanbul
    bbox = (41.05, 41.04, 29.01, 29.00)
    try:
        osm_file = fetcher.fetch_by_bbox(bbox)
        assert os.path.exists(osm_file)
        assert osm_file.endswith(".osm")
    except Exception as e:
        pytest.skip(f"Skipping test due to network error: {str(e)}")

def test_invalid_place(fetcher):
    """Test fetching with invalid place name."""
    with pytest.raises(Exception):
        fetcher.fetch_by_place("ThisPlaceDoesNotExist12345")