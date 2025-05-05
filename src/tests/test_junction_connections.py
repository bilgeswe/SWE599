"""Tests for junction connection handling."""

import unittest
import os
import tempfile
import shutil
from lxml import etree
from src.converter.advanced_sumo_to_xodr import AdvancedSumoNetworkParser
from src.tests.test_data import (
    create_simple_network,
    create_network_with_invalid_connections
)

class TestJunctionConnections(unittest.TestCase):
    """Test cases for junction connection handling."""
    
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
        
    def test_valid_via_lane(self):
        """Test validation of valid via lanes."""
        # Create and write simple network
        network = create_simple_network()
        self._write_network_to_file(network)
        
        # Parse network
        parser = AdvancedSumoNetworkParser(self.test_net_file)
        parser.parse()
        
        # Test valid via lane
        self.assertTrue(parser._is_valid_via_lane("edge1", "edge2", "edge1_0_edge2_0"))
        
    def test_invalid_via_lane(self):
        """Test validation of invalid via lanes."""
        # Create and write network with invalid connections
        network = create_network_with_invalid_connections()
        self._write_network_to_file(network)
        
        # Parse network
        parser = AdvancedSumoNetworkParser(self.test_net_file)
        parser.parse()
        
        # Test various invalid cases
        test_cases = [
            ("edge1", "edge2", "invalid_lane"),
            ("edge1", "edge2", "edge1_2_edge2_0"),  # Lane 2 doesn't exist
            ("edge1", "edge2", "edge1_0_edge2_2"),  # Lane 2 doesn't exist
            ("edge1", "edge2", "edge1_0"),          # Incomplete via lane
            ("edge1", "edge2", "edge1_0_edge2"),    # Incomplete via lane
            ("edge1", "edge2", "edge1_edge2_0"),    # Missing lane index
            ("edge1", "edge2", "edge1_0_edge2_"),   # Missing lane index
        ]
        
        for from_edge, to_edge, via_lane in test_cases:
            with self.subTest(from_edge=from_edge, to_edge=to_edge, via_lane=via_lane):
                self.assertFalse(parser._is_valid_via_lane(from_edge, to_edge, via_lane))
                
    def test_nonexistent_edges(self):
        """Test validation with nonexistent edges."""
        # Create and write simple network
        network = create_simple_network()
        self._write_network_to_file(network)
        
        # Parse network
        parser = AdvancedSumoNetworkParser(self.test_net_file)
        parser.parse()
        
        # Test with nonexistent edges
        self.assertFalse(parser._is_valid_via_lane("nonexistent1", "edge2", "nonexistent1_0_edge2_0"))
        self.assertFalse(parser._is_valid_via_lane("edge1", "nonexistent2", "edge1_0_nonexistent2_0"))
        self.assertFalse(parser._is_valid_via_lane("nonexistent1", "nonexistent2", "nonexistent1_0_nonexistent2_0"))

if __name__ == "__main__":
    unittest.main() 