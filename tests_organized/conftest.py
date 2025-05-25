"""
🧪 Test Configuration for Üsküdar AV Simulation Project
======================================================

This file contains pytest configuration and shared fixtures for all test categories:
- Unit Tests: Individual component testing
- Integration Tests: Component interaction testing  
- Functional Tests: End-to-end workflow testing
- Performance Tests: Speed and memory benchmarks

Test Structure:
- v1_basic/: Tests for basic OSM data processing and conversion
- v2_advanced/: Tests for advanced export algorithms and AV simulation
- shared/: Tests that apply to both versions
"""

import os
import sys
import pytest
import tempfile
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "v1_basic_method"))
sys.path.insert(0, str(project_root / "v2_advanced_method"))


@pytest.fixture(scope="session")
def project_root_path():
    """Return the project root directory path."""
    return Path(__file__).parent.parent


@pytest.fixture(scope="session")
def test_data_dir():
    """Return the test data directory path."""
    return Path(__file__).parent / "data"


@pytest.fixture(scope="session")
def temp_output_dir():
    """Create a temporary directory for test outputs."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)


@pytest.fixture(scope="session")
def sample_osm_data():
    """Provide sample OSM data for testing."""
    return {
        'nodes': [
            {'id': '1', 'lat': 41.0370, 'lon': 29.0448},
            {'id': '2', 'lat': 41.0375, 'lon': 29.0450},
            {'id': '3', 'lat': 41.0380, 'lon': 29.0452}
        ],
        'edges': [
            {
                'id': 'way1',
                'from_node': '1', 
                'to_node': '2',
                'highway_type': 'primary',
                'name': 'Test Road'
            }
        ],
        'traffic_lights': [
            {
                'id': 'tl_1',
                'position': [29.0448, 41.0370],
                'cycle_time': 90
            }
        ]
    }


@pytest.fixture(scope="session") 
def sample_sumo_network():
    """Provide sample SUMO network data for testing."""
    return {
        'edges': [
            {
                'id': 'edge1',
                'from': 'junction1',
                'to': 'junction2', 
                'lanes': [
                    {'id': 'edge1_0', 'speed': 13.89, 'width': 3.5, 'length': 100.0},
                    {'id': 'edge1_1', 'speed': 13.89, 'width': 3.5, 'length': 100.0}
                ]
            }
        ],
        'junctions': [
            {
                'id': 'junction1',
                'x': 0.0,
                'y': 0.0,
                'type': 'priority'
            }
        ]
    }


@pytest.fixture(scope="function")
def mock_uskudar_data():
    """Provide mock Üsküdar district data for testing."""
    return {
        'bounds': {
            'min_lat': 40.992,
            'max_lat': 41.078,
            'min_lon': 29.006,
            'max_lon': 29.092
        },
        'statistics': {
            'nodes': 9421,
            'edges': 24157,
            'traffic_lights': 42
        },
        'utm_zone': '35N',
        'utm_offset': (-668686.91, -4539963.74)
    }


@pytest.fixture(scope="function")
def create_temp_osm_file(temp_output_dir):
    """Create a temporary OSM file for testing."""
    def _create_osm(content=""):
        osm_file = temp_output_dir / "test.osm"
        if not content:
            content = '''<?xml version="1.0" encoding="UTF-8"?>
<osm version="0.6" generator="test">
  <node id="1" lat="41.0370" lon="29.0448"/>
  <node id="2" lat="41.0375" lon="29.0450"/>
  <way id="1">
    <nd ref="1"/>
    <nd ref="2"/>
    <tag k="highway" v="primary"/>
    <tag k="name" v="Test Road"/>
  </way>
</osm>'''
        osm_file.write_text(content)
        return str(osm_file)
    return _create_osm


@pytest.fixture(scope="function") 
def create_temp_sumo_file(temp_output_dir):
    """Create a temporary SUMO network file for testing."""
    def _create_sumo(content=""):
        sumo_file = temp_output_dir / "test.net.xml"
        if not content:
            content = '''<?xml version="1.0" encoding="UTF-8"?>
<net version="1.16" junctionCornerDetail="5" lefthand="false" limitTurnSpeed="5.50" rightOfWay="edgePriority">
    <edge id="edge1" from="junction1" to="junction2" priority="2">
        <lane id="edge1_0" index="0" speed="13.89" length="100.00" width="3.50" shape="0.00,0.00 100.00,0.00"/>
    </edge>
    <junction id="junction1" type="priority" x="0.00" y="0.00" incLanes="" intLanes="" shape="-0.00,1.60 -0.00,-1.60"/>
    <junction id="junction2" type="priority" x="100.00" y="0.00" incLanes="edge1_0" intLanes="" shape="100.00,-1.60 100.00,1.60"/>
</net>'''
        sumo_file.write_text(content)
        return str(sumo_file)
    return _create_sumo


# Performance test markers
def pytest_configure(config):
    """Configure pytest markers."""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "unit: marks tests as unit tests"
    )
    config.addinivalue_line(
        "markers", "functional: marks tests as functional tests"
    )
    config.addinivalue_line(
        "markers", "performance: marks tests as performance benchmarks"
    )
    config.addinivalue_line(
        "markers", "v1_basic: marks tests specific to Version 1 (basic method)"
    )
    config.addinivalue_line(
        "markers", "v2_advanced: marks tests specific to Version 2 (advanced method)"
    )


# Test collection customization
def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers based on file paths."""
    for item in items:
        # Add markers based on file path
        if "unit" in str(item.fspath):
            item.add_marker(pytest.mark.unit)
        elif "integration" in str(item.fspath):
            item.add_marker(pytest.mark.integration)
        elif "functional" in str(item.fspath):
            item.add_marker(pytest.mark.functional)
        elif "performance" in str(item.fspath):
            item.add_marker(pytest.mark.performance)
            
        # Add version markers
        if "v1_basic" in str(item.fspath):
            item.add_marker(pytest.mark.v1_basic)
        elif "v2_advanced" in str(item.fspath):
            item.add_marker(pytest.mark.v2_advanced)


@pytest.fixture(autouse=True)
def setup_test_environment(monkeypatch):
    """Set up test environment variables."""
    monkeypatch.setenv("TESTING", "1")
    monkeypatch.setenv("SUMO_HOME", "/opt/homebrew/share/sumo")  # Default macOS path 