"""
Tests for the OSM fetcher module.
This message will be deleted after I, BilgeA. add in more technical details to the progress in commit message.
Because I accidentally clicked git commit early.
"""

import os
import pytest
from unittest.mock import patch, MagicMock
from src.examples.download_network import OSMFetcher

@pytest.fixture
def osm_fetcher():
    """Create a temporary OSM fetcher instance"""
    return OSMFetcher()

@patch('osmnx.graph_from_place')
def test_fetch_by_place_name(mock_graph, osm_fetcher):
    """Test fetching OSM data by place name"""
    # Mock OSMnx response
    mock_graph.return_value = MagicMock()
    
    # Test with a place name
    place_name = "Levent, Istanbul, Turkey"
    G = osm_fetcher.fetch_by_place_name(place_name)
    assert G is not None
    mock_graph.assert_called_once_with(place_name, network_type='drive', simplify=False)

@patch('osmnx.graph_from_bbox')
def test_fetch_by_bbox(mock_graph, osm_fetcher):
    """Test fetching OSM data by bounding box"""
    # Mock OSMnx response
    mock_graph.return_value = MagicMock()
    
    # Test with bounding box coordinates
    north, south, east, west = 41.1, 41.0, 29.1, 29.0
    G = osm_fetcher.fetch_by_bbox(north, south, east, west)
    assert G is not None
    mock_graph.assert_called_once_with(north, south, east, west, network_type='drive', simplify=False)

@patch('osmnx.save_graphml')
def test_save_osm_data(mock_save, osm_fetcher):
    """Test saving OSM data to file"""
    # Mock OSMnx save function
    mock_save.return_value = None
    
    # Create a mock graph
    G = MagicMock()
    output_file = "test_network.graphml"
    
    # Test saving
    osm_fetcher.save_osm_data(G, output_file)
    mock_save.assert_called_once_with(G, output_file)
    
    # Clean up
    if os.path.exists(output_file):
        os.remove(output_file)