import os
import sys
import subprocess
import requests
import lxml.etree as ET
import osmnx as ox
import matplotlib.pyplot as plt
from sumolib import checkBinary
from unittest.mock import patch, MagicMock

def test_python_environment():
    """Test Python environment and required libraries"""
    print("\n=== Testing Python Environment ===")
    
    # Test Python version
    print(f"Python version: {sys.version}")
    
    # Test required libraries
    libraries = {
        'requests': 'HTTP requests',
        'lxml': 'XML processing',
        'osmnx': 'OSM data handling',
        'matplotlib': 'Visualization',
        'sumolib': 'SUMO Python interface'
    }
    
    for lib, purpose in libraries.items():
        try:
            __import__(lib)
            print(f"✓ {lib} ({purpose}) is installed")
        except ImportError:
            pytest.fail(f"{lib} ({purpose}) is NOT installed")

def test_sumo_installation():
    """Test SUMO installation and tools"""
    print("\n=== Testing SUMO Installation ===")
    
    # Mock checkBinary to avoid actual system calls
    with patch('sumolib.checkBinary') as mock_check:
        mock_check.return_value = "/path/to/sumo"
        netconvert = checkBinary('netconvert')
        assert netconvert == "/path/to/sumo"
        
        sumo_gui = checkBinary('sumo-gui')
        assert sumo_gui == "/path/to/sumo"

@patch('osmnx.graph_from_place')
@patch('requests.get')
def test_osm_access(mock_requests, mock_graph):
    """Test access to OSM and Overpass API with mocked responses"""
    # Mock OSMnx response
    mock_graph.return_value = MagicMock()
    
    # Mock Overpass API response
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_requests.return_value = mock_response
    
    # Test OSMnx
    G = ox.graph_from_place("Levent, Istanbul, Turkey", network_type='drive', simplify=False)
    assert G is not None
    
    # Test Overpass API
    response = requests.get("https://overpass-api.de/api/interpreter")
    assert response.status_code == 200

def test_xml_processing():
    """Test XML processing capabilities"""
    print("\n=== Testing XML Processing ===")
    
    try:
        # Create a simple XML file
        root = ET.Element("test")
        child = ET.SubElement(root, "child")
        child.text = "test content"
        tree = ET.ElementTree(root)
        
        # Test XML creation and parsing
        xml_str = ET.tostring(root, encoding='unicode')
        parsed = ET.fromstring(xml_str)
        assert parsed.tag == "test"
        assert parsed.find("child").text == "test content"
    except Exception as e:
        pytest.fail(f"XML processing test failed: {e}")

def main():
    """Run all tests"""
    print("Starting comprehensive environment test...")
    
    test_python_environment()
    test_sumo_installation()
    test_osm_access()
    test_xml_processing()
    
    print("\nTest completed!")

if __name__ == "__main__":
    main() 