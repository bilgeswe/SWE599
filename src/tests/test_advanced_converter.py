import unittest
import os
import tempfile
import shutil
from lxml import etree
from src.converter.advanced_sumo_to_xodr import AdvancedSumoNetworkParser, AdvancedSumoToOpenDriveConverter
from src.converter.advanced_sumo_to_xodr import Edge, Junction, TrafficSignal, Point

class TestAdvancedConverter(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.test_net_file = os.path.join(self.test_dir, "test.net.xml")
        self.test_output_file = os.path.join(self.test_dir, "test.xodr")
        
        # Create test network data
        self._create_test_network()
        
    def tearDown(self):
        shutil.rmtree(self.test_dir)
        
    def _create_test_network(self):
        """Create a test SUMO network file."""
        root = etree.Element("net")
        
        # Add edges
        edges = etree.SubElement(root, "edges")
        edge1 = etree.SubElement(edges, "edge", id="edge1", from_="j1", to="j2", priority="1")
        edge2 = etree.SubElement(edges, "edge", id="edge2", from_="j2", to="j3", priority="2")
        
        # Add lanes with shape
        for edge in [edge1, edge2]:
            lanes = etree.SubElement(edge, "lanes")
            for i in range(2):
                lane = etree.SubElement(lanes, "lane", 
                                      id=f"{edge.get('id')}_{i}", 
                                      index=str(i), 
                                      speed="13.89", 
                                      length="100.0")
                shape = etree.SubElement(lane, "shape")
                shape.text = "0,0 100,0"
        
        # Add junctions
        junctions = etree.SubElement(root, "junctions")
        for i in range(1, 4):
            junction = etree.SubElement(junctions, "junction", 
                                      id=f"j{i}", 
                                      type="priority",
                                      x=str((i-1)*100),
                                      y="0")
            if i > 1:
                request = etree.SubElement(junction, "request", 
                                         index="0", 
                                         response="0", 
                                         foes="0", 
                                         cont="0")
        
        # Add connections
        connections = etree.SubElement(root, "connections")
        connection = etree.SubElement(connections, "connection",
                                    from_="edge1",
                                    to="edge2",
                                    fromLane="0",
                                    toLane="0",
                                    via="edge1_0_edge2_0")
        
        # Add traffic signals
        tls = etree.SubElement(root, "tlLogic")
        tls.set("id", "j2")
        tls.set("type", "static")
        tls.set("programID", "0")
        tls.set("offset", "0")
        
        phase = etree.SubElement(tls, "phase", duration="31", state="GGrr")
        
        # Write to file
        tree = etree.ElementTree(root)
        tree.write(self.test_net_file, pretty_print=True, xml_declaration=True, encoding="UTF-8")
        
    def test_geometry_handling(self):
        """Test complex geometry handling."""
        parser = AdvancedSumoNetworkParser(self.test_net_file)
        parser.parse()
        
        # Test reference line calculation
        edge = parser.edges["edge1"]
        reference_points, s_values = parser._calculate_reference_line(edge)
        
        self.assertGreater(len(reference_points), 0)
        self.assertGreater(len(s_values), 0)
        self.assertEqual(len(reference_points), len(s_values))
        
        # Test road properties calculation
        curvature, heading, superelevation = parser._calculate_road_properties(reference_points, s_values)
        
        self.assertEqual(len(curvature), len(reference_points))
        self.assertEqual(len(heading), len(reference_points))
        self.assertEqual(len(superelevation), len(reference_points))
        
    def test_traffic_signal_conversion(self):
        """Test traffic signal conversion."""
        parser = AdvancedSumoNetworkParser(self.test_net_file)
        parser.parse()
        
        # Test signal state conversion
        state = "GGrr"
        converted_state = parser._convert_signal_state(state)
        self.assertEqual(converted_state, "2200")
        
        # Test signal type conversion
        signal_type = "static"
        converted_type = parser._get_signal_type(signal_type)
        self.assertEqual(converted_type, "1000001")
        
    def test_junction_connections(self):
        """Test junction connection handling."""
        parser = AdvancedSumoNetworkParser(self.test_net_file)
        parser.parse()
        
        # Test via lane validation
        # The test network has edge1 with lanes 0,1 and edge2 with lanes 0,1
        # The connection is from edge1_0 to edge2_0
        self.assertTrue(parser._is_valid_via_lane("edge1", "edge2", "edge1_0_edge2_0"))
        
        # Test invalid via lane
        self.assertFalse(parser._is_valid_via_lane("edge1", "edge2", "invalid_lane"))
        self.assertFalse(parser._is_valid_via_lane("edge1", "edge2", "edge1_2_edge2_0"))  # Lane 2 doesn't exist
        self.assertFalse(parser._is_valid_via_lane("edge1", "edge2", "edge1_0_edge2_2"))  # Lane 2 doesn't exist
        
    def test_validation(self):
        """Test network validation."""
        parser = AdvancedSumoNetworkParser(self.test_net_file)
        parser.parse()
        
        # Test should pass with valid network
        self.assertTrue(parser._validate_network())
        
        # Test should fail with invalid network
        parser.edges["edge1"].shape = []  # Make edge1 invalid
        with self.assertRaises(Exception):
            parser._validate_network()
            
    def test_full_conversion(self):
        """Test complete conversion process."""
        converter = AdvancedSumoToOpenDriveConverter(self.test_net_file, self.test_output_file)
        converter.convert()
        
        # Check if output file exists
        self.assertTrue(os.path.exists(self.test_output_file))
        
        # Check if output file is valid XML
        tree = etree.parse(self.test_output_file)
        root = tree.getroot()
        
        # Check for required elements
        self.assertIsNotNone(root.find(".//road"))
        self.assertIsNotNone(root.find(".//junction"))
        self.assertIsNotNone(root.find(".//controller"))

if __name__ == '__main__':
    unittest.main() 