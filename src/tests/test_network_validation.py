"""Tests for network validation."""

import unittest
import os
import tempfile
import shutil
from lxml import etree
from src.converter.advanced_sumo_to_xodr import AdvancedSumoNetworkParser
from src.tests.test_data import (
    create_simple_network,
    create_network_with_invalid_connections,
    create_network_with_traffic_signals
)

class TestNetworkValidation(unittest.TestCase):
    """Test cases for network validation."""
    
    def setUp(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp()
        self.test_net_file = os.path.join(self.test_dir, "test.net.xml")
        
    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.test_dir)
        
    def _write_network_to_file(self, network: etree.Element) -> None:
        """Write network to test file."""
        tree = etree.ElementTree(network)
        tree.write(self.test_net_file, pretty_print=True, xml_declaration=True, encoding="UTF-8")
        
    def test_valid_network(self):
        """Test validation of a valid network."""
        # Create and write simple network
        network = create_simple_network()
        self._write_network_to_file(network)
        
        # Parse network
        parser = AdvancedSumoNetworkParser(self.test_net_file)
        parser.parse()
        
        # Validate network
        self.assertTrue(parser._validate_network())
        
    def test_invalid_connections(self):
        """Test validation of network with invalid connections."""
        # Create and write network with invalid connections
        network = create_network_with_invalid_connections()
        self._write_network_to_file(network)
        
        # Parse network
        parser = AdvancedSumoNetworkParser(self.test_net_file)
        parser.parse()
        
        # Validate network
        self.assertFalse(parser._validate_network())
        
    def test_network_structure(self):
        """Test validation of network structure."""
        # Create and write simple network
        network = create_simple_network()
        self._write_network_to_file(network)
        
        # Parse network
        parser = AdvancedSumoNetworkParser(self.test_net_file)
        parser.parse()
        
        # Validate network structure
        self.assertTrue(parser._validate_network_structure())
        
    def test_junction_validation(self):
        """Test validation of junctions."""
        # Create and write simple network
        network = create_simple_network()
        self._write_network_to_file(network)
        
        # Parse network
        parser = AdvancedSumoNetworkParser(self.test_net_file)
        parser.parse()
        
        # Validate junctions
        self.assertTrue(parser._validate_junctions())
        
    def test_traffic_signals(self):
        """Test validation of traffic signals."""
        # Create and write network with traffic signals
        network = create_network_with_traffic_signals()
        self._write_network_to_file(network)
        
        # Parse network
        parser = AdvancedSumoNetworkParser(self.test_net_file)
        parser.parse()
        
        # Validate traffic signals
        self.assertTrue(parser._validate_traffic_signals())
        
    def test_lane_connections(self):
        """Test validation of lane connections."""
        # Create and write simple network
        network = create_simple_network()
        self._write_network_to_file(network)
        
        # Parse network
        parser = AdvancedSumoNetworkParser(self.test_net_file)
        parser.parse()
        
        # Validate lane connections
        self.assertTrue(parser._validate_lane_connections())
        
    def test_road_properties(self):
        """Test validation of road properties."""
        # Create and write simple network
        network = create_simple_network()
        self._write_network_to_file(network)
        
        # Parse network
        parser = AdvancedSumoNetworkParser(self.test_net_file)
        parser.parse()
        
        # Validate road properties
        self.assertTrue(parser._validate_road_properties())

if __name__ == "__main__":
    unittest.main() 