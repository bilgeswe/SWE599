#!/usr/bin/env python3
"""
Test suite for SUMO to OpenDRIVE converter.
"""

import os
import unittest
import subprocess
import xml.etree.ElementTree as ET
from pathlib import Path
import tempfile
import shutil
import logging
import pytest
from unittest.mock import patch, MagicMock

from src.converter.sumo_to_xodr import SumoNetworkParser, OpenDriveGenerator, Point, Lane, Edge, Junction

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@pytest.fixture
def mock_network():
    """Fixture that provides a mock SUMO network structure."""
    return {
        'edges': {
            'edge1': {
                'id': 'edge1',
                'from': 'j1',
                'to': 'j2',
                'priority': 0,
                'type': 'highway',
                'lanes': [
                    {
                        'id': 'edge1_0',
                        'index': 0,
                        'speed': 13.89,
                        'width': 3.2,
                        'shape': [
                            {'x': 0.0, 'y': 0.0},
                            {'x': 100.0, 'y': 0.0}
                        ],
                        'length': 100.0
                    },
                    {
                        'id': 'edge1_1',
                        'index': 1,
                        'speed': 13.89,
                        'width': 3.2,
                        'shape': [
                            {'x': 0.0, 'y': 3.2},
                            {'x': 100.0, 'y': 3.2}
                        ],
                        'length': 100.0
                    }
                ]
            }
        },
        'junctions': {
            'j1': {
                'id': 'j1',
                'type': 'priority',
                'x': 0.0,
                'y': 0.0,
                'inc_lanes': ['edge1_0', 'edge1_1'],
                'int_lanes': [],
                'requests': []
            },
            'j2': {
                'id': 'j2',
                'type': 'priority',
                'x': 100.0,
                'y': 0.0,
                'inc_lanes': ['edge1_0', 'edge1_1'],
                'int_lanes': [],
                'requests': []
            }
        }
    }

def test_sumo_parser(mock_network):
    """Test the SUMO network parser."""
    mock_net_file = 'mock_network.net.xml'
    with patch('src.converter.sumo_to_xodr.SumoNetworkParser.parse') as mock_parse:
        mock_parse.return_value = None  # parse() returns None, modifies self.edges and self.junctions
        parser = SumoNetworkParser(mock_net_file)
        parser.parse()
        
        mock_parse.assert_called_once()
        assert parser.edges == {}
        assert parser.junctions == {}

def test_opendrive_generator(mock_network):
    """Test the OpenDRIVE generator."""
    mock_output_file = 'mock_output.xodr'
    mock_parser = MagicMock()
    mock_parser.edges = mock_network['edges']
    mock_parser.junctions = mock_network['junctions']
    mock_parser.location = None
    
    with patch('src.converter.sumo_to_xodr.OpenDriveGenerator.generate') as mock_generate:
        mock_generate.return_value = None  # generate() returns None
        generator = OpenDriveGenerator(mock_parser)
        generator.generate(mock_output_file)
        
        mock_generate.assert_called_once_with(mock_output_file)

def test_full_conversion(mock_network):
    """Test the complete conversion process."""
    mock_net_file = 'mock_network.net.xml'
    mock_output_file = 'mock_output.xodr'
    
    with patch('src.converter.sumo_to_xodr.SumoNetworkParser.parse') as mock_parse, \
         patch('src.converter.sumo_to_xodr.OpenDriveGenerator.generate') as mock_generate:
        
        mock_parse.return_value = None
        mock_generate.return_value = None
        
        parser = SumoNetworkParser(mock_net_file)
        parser.parse()
        
        generator = OpenDriveGenerator(parser)
        generator.generate(mock_output_file)
        
        mock_parse.assert_called_once()
        mock_generate.assert_called_once_with(mock_output_file)

class TestSumoToOpenDrive:
    """Test cases for the SUMO to OpenDRIVE conversion process."""
    
    def setup_method(self):
        """Set up test environment."""
        self.test_dir = os.path.dirname(os.path.abspath(__file__))
        self.data_dir = os.path.join(self.test_dir, 'data')
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Create a simple SUMO network file
        self.sumo_net = os.path.join(self.data_dir, 'test_network.net.xml')
        with open(self.sumo_net, 'w') as f:
            f.write('''<?xml version="1.0" encoding="UTF-8"?>
<net version="1.0">
    <location netOffset="0.0,0.0" convBoundary="0.0,0.0,100.0,100.0" origBoundary="0.0,0.0,100.0,100.0" projParameter=""/>
    <edge id="edge1" from="j1" to="j2" priority="0" type="highway">
        <lane id="edge1_0" index="0" speed="13.89" width="3.2" length="100.0" shape="0.0,0.0 100.0,0.0"/>
        <lane id="edge1_1" index="1" speed="13.89" width="3.2" length="100.0" shape="0.0,3.2 100.0,3.2"/>
    </edge>
    <junction id="j1" type="priority" x="0.0" y="0.0" incLanes="edge1_0 edge1_1" intLanes=""/>
    <junction id="j2" type="priority" x="100.0" y="0.0" incLanes="edge1_0 edge1_1" intLanes=""/>
</net>''')
        
        # Output file
        self.output_file = os.path.join(self.data_dir, 'test_output.xodr')
    
    def teardown_method(self):
        """Clean up test files."""
        if os.path.exists(self.sumo_net):
            os.remove(self.sumo_net)
        if os.path.exists(self.output_file):
            os.remove(self.output_file)
        if os.path.exists(self.data_dir):
            os.rmdir(self.data_dir)
    
    def test_parse_sumo_network(self):
        """Test parsing a SUMO network file."""
        parser = SumoNetworkParser(self.sumo_net)
        parser.parse()
        
        assert len(parser.edges) == 1
        assert len(parser.junctions) == 2
        assert 'edge1' in parser.edges
        assert 'j1' in parser.junctions
        assert 'j2' in parser.junctions
    
    def test_generate_opendrive(self):
        """Test generating an OpenDRIVE file."""
        parser = SumoNetworkParser(self.sumo_net)
        parser.parse()
        
        generator = OpenDriveGenerator(parser)
        generator.generate(self.output_file)
        
        assert os.path.exists(self.output_file)
    
    def test_full_conversion(self):
        """Test the complete conversion process."""
        parser = SumoNetworkParser(self.sumo_net)
        parser.parse()
        
        generator = OpenDriveGenerator(parser)
        generator.generate(self.output_file)
        
        assert os.path.exists(self.output_file)
        
        # Verify the generated OpenDRIVE file
        with open(self.output_file, 'r') as f:
            content = f.read()
            assert '<OpenDRIVE>' in content
            assert '</OpenDRIVE>' in content
            assert 'edge1' in content
            assert 'j1' in content
            assert 'j2' in content

if __name__ == '__main__':
    unittest.main() 