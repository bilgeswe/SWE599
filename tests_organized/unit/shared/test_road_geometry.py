"""Tests for road geometry handling."""

import unittest
import os
import tempfile
import shutil
from lxml import etree
from src.converter.advanced_sumo_to_xodr import AdvancedSumoNetworkParser
from src.tests.test_data import (
    create_simple_network,
    create_network_with_curved_geometry,
    create_network_with_elevation
)

class TestRoadGeometry(unittest.TestCase):
    """Test cases for road geometry handling."""
    
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
        
    def test_reference_line_calculation(self):
        """Test reference line calculation for straight roads."""
        # Create and write simple network
        network = create_simple_network()
        self._write_network_to_file(network)
        
        # Parse network
        parser = AdvancedSumoNetworkParser(self.test_net_file)
        parser.parse()
        
        # Test reference line calculation
        edge = parser.edges["edge1"]
        reference_points, s_values = parser._calculate_reference_line(edge)
        
        self.assertGreater(len(reference_points), 0)
        self.assertGreater(len(s_values), 0)
        self.assertEqual(len(reference_points), len(s_values))
        
    def test_curved_geometry(self):
        """Test geometry handling for curved roads."""
        # Create and write network with curved geometry
        network = create_network_with_curved_geometry()
        self._write_network_to_file(network)
        
        # Parse network
        parser = AdvancedSumoNetworkParser(self.test_net_file)
        parser.parse()
        
        # Test road properties calculation
        edge = parser.edges["edge1"]
        reference_points, s_values = parser._calculate_reference_line(edge)
        curvature, heading, superelevation = parser._calculate_road_properties(reference_points, s_values)
        
        self.assertEqual(len(curvature), len(reference_points))
        self.assertEqual(len(heading), len(reference_points))
        self.assertEqual(len(superelevation), len(reference_points))
        
        # Verify curvature values
        self.assertTrue(any(abs(c) > 0 for c in curvature))  # Should have some curvature
        
    def test_elevation_handling(self):
        """Test elevation profile handling."""
        # Create and write network with elevation
        network = create_network_with_elevation()
        self._write_network_to_file(network)
        
        # Parse network
        parser = AdvancedSumoNetworkParser(self.test_net_file)
        parser.parse()
        
        # Test elevation validation
        self.assertTrue(parser._validate_elevation_profiles())
        
    def test_geometry_validation(self):
        """Test geometry validation checks."""
        # Create and write simple network
        network = create_simple_network()
        self._write_network_to_file(network)
        
        # Parse network
        parser = AdvancedSumoNetworkParser(self.test_net_file)
        parser.parse()
        
        # Test geometry validation
        self.assertTrue(parser._validate_geometry())
        
        # Test for sharp angles
        self.assertFalse(parser._has_sharp_angles(parser.edges["edge1"].shape))
        
        # Test for self-intersections
        self.assertFalse(parser._has_self_intersection(parser.edges["edge1"].shape))

if __name__ == "__main__":
    unittest.main() 