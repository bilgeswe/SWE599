import os
import sys
import subprocess
import requests
import lxml.etree as ET
import osmnx as ox
import matplotlib.pyplot as plt
from sumolib import checkBinary

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
            print(f"✗ {lib} ({purpose}) is NOT installed")

def test_sumo_installation():
    """Test SUMO installation and tools"""
    print("\n=== Testing SUMO Installation ===")
    
    # Test netconvert
    try:
        netconvert = checkBinary('netconvert')
        print("✓ netconvert is available")
    except Exception as e:
        print(f"✗ netconvert is NOT available: {e}")
    
    # Test sumo-gui
    try:
        sumo_gui = checkBinary('sumo-gui')
        print("✓ sumo-gui is available")
    except Exception as e:
        print(f"✗ sumo-gui is NOT available: {e}")

def test_osm_access():
    """Test access to OSM and Overpass API"""
    print("\n=== Testing OSM Access ===")
    
    # Test OSMnx
    try:
        G = ox.graph_from_place("Levent, Istanbul, Turkey", network_type='drive', simplify=False)
        print("✓ Successfully downloaded OSM data using osmnx")
    except Exception as e:
        print(f"✗ Failed to download OSM data: {e}")
    
    # Test Overpass API
    try:
        overpass_url = "https://overpass-api.de/api/interpreter"
        overpass_query = """
        [out:xml][timeout:25];
        area[name="Levent"]->.searchArea;
        (
          way["highway"](area.searchArea);
        );
        out body;
        >;
        out skel qt;
        """
        response = requests.get(overpass_url, params={'data': overpass_query})
        if response.status_code == 200:
            print("✓ Successfully connected to Overpass API")
        else:
            print(f"✗ Overpass API returned status code: {response.status_code}")
    except Exception as e:
        print(f"✗ Failed to connect to Overpass API: {e}")

def test_xml_processing():
    """Test XML processing capabilities"""
    print("\n=== Testing XML Processing ===")
    
    try:
        # Create a simple XML file
        root = ET.Element("test")
        child = ET.SubElement(root, "child")
        child.text = "test content"
        tree = ET.ElementTree(root)
        tree.write("test.xml")
        
        # Read it back
        tree = ET.parse("test.xml")
        print("✓ Successfully created and parsed XML file")
        
        # Clean up
        os.remove("test.xml")
    except Exception as e:
        print(f"✗ XML processing test failed: {e}")

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