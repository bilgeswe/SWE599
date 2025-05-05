"""Tests for traffic signal handling."""

import unittest
import os
import tempfile
import shutil
from lxml import etree
from src.converter.advanced_sumo_to_xodr import AdvancedSumoNetworkParser
from src.tests.test_data import create_network_with_traffic_signals

class TestTrafficSignals(unittest.TestCase):
    """Test cases for traffic signal handling."""
    
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
        
    def test_traffic_signal_parsing(self):
        """Test parsing of traffic signals."""
        # Create and write network with traffic signals
        network = create_network_with_traffic_signals()
        self._write_network_to_file(network)
        
        # Parse network
        parser = AdvancedSumoNetworkParser(self.test_net_file)
        parser.parse()
        
        # Verify traffic signal data
        self.assertIn("j2", parser.traffic_signals)
        signal = parser.traffic_signals["j2"]
        
        self.assertEqual(signal.type, "static")
        self.assertEqual(len(signal.phases), 1)
        self.assertEqual(signal.phases[0]["duration"], "31")
        self.assertEqual(signal.phases[0]["state"], "GGrr")
        
    def test_signal_state_conversion(self):
        """Test conversion of signal states."""
        # Create and write network with traffic signals
        network = create_network_with_traffic_signals()
        self._write_network_to_file(network)
        
        # Parse network
        parser = AdvancedSumoNetworkParser(self.test_net_file)
        parser.parse()
        
        # Test state conversion
        test_cases = [
            ("GGrr", "2200"),  # Green, Green, Red, Red
            ("yy", "11"),      # Yellow, Yellow
            ("rr", "00"),      # Red, Red
            ("g", "2"),        # Green
            ("y", "1"),        # Yellow
            ("r", "0"),        # Red
        ]
        
        for sumo_state, expected_state in test_cases:
            with self.subTest(sumo_state=sumo_state, expected_state=expected_state):
                converted = parser._convert_signal_state(sumo_state)
                self.assertEqual(converted, expected_state)
                
    def test_signal_type_conversion(self):
        """Test conversion of signal types."""
        # Create and write network with traffic signals
        network = create_network_with_traffic_signals()
        self._write_network_to_file(network)
        
        # Parse network
        parser = AdvancedSumoNetworkParser(self.test_net_file)
        parser.parse()
        
        # Test type conversion
        test_cases = [
            ("static", "1000001"),
            ("actuated", "1000002"),
            ("delay_based", "1000003"),
            ("sotl", "1000004"),
            ("unknown", "1000001"),  # Default type
        ]
        
        for sumo_type, expected_type in test_cases:
            with self.subTest(sumo_type=sumo_type, expected_type=expected_type):
                converted = parser._get_signal_type(sumo_type)
                self.assertEqual(converted, expected_type)
                
    def test_traffic_signal_validation(self):
        """Test validation of traffic signals."""
        # Create and write network with traffic signals
        network = create_network_with_traffic_signals()
        self._write_network_to_file(network)
        
        # Parse network
        parser = AdvancedSumoNetworkParser(self.test_net_file)
        parser.parse()
        
        # Test validation
        self.assertTrue(parser._validate_traffic_signals())

if __name__ == "__main__":
    unittest.main() 