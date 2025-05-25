"""Test cases for error handling during network conversion."""

import unittest
from lxml import etree
from typing import List, Tuple
import pytest
from src.converter.network_converter import NetworkConverter
from src.validation.network_validator import NetworkValidator

class TestConversionErrors(unittest.TestCase):
    def setUp(self):
        self.converter = NetworkConverter()
        self.validator = NetworkValidator()
    
    def test_invalid_xml_structure(self):
        """Test handling of invalid XML structure."""
        # Create invalid XML (missing required elements)
        root = etree.Element("net")
        with pytest.raises(ValueError) as exc_info:
            self.converter.convert_network(root)
        assert "Missing required element" in str(exc_info.value)
    
    def test_missing_lane_attributes(self):
        """Test handling of missing lane attributes."""
        root = etree.Element("net")
        edges = etree.SubElement(root, "edges")
        edge = etree.SubElement(edges, "edge", id="test_road")
        lanes = etree.SubElement(edge, "lanes")
        # Create lane without required attributes
        lane = etree.SubElement(lanes, "lane")
        
        with pytest.raises(ValueError) as exc_info:
            self.converter.convert_network(root)
        assert "Missing required lane attribute" in str(exc_info.value)
    
    def test_invalid_lane_geometry(self):
        """Test handling of invalid lane geometry."""
        root = etree.Element("net")
        edges = etree.SubElement(root, "edges")
        edge = etree.SubElement(edges, "edge", id="test_road")
        lanes = etree.SubElement(edge, "lanes")
        lane = etree.SubElement(lanes, "lane",
                              id="test_lane",
                              index="0",
                              speed="13.89",
                              length="100")
        shape = etree.SubElement(lane, "shape")
        # Invalid shape (single point instead of two points)
        shape.text = "0,0"
        
        with pytest.raises(ValueError) as exc_info:
            self.converter.convert_network(root)
        assert "Invalid lane geometry" in str(exc_info.value)
    
    def test_invalid_junction_connections(self):
        """Test handling of invalid junction connections."""
        root = etree.Element("net")
        edges = etree.SubElement(root, "edges")
        junctions = etree.SubElement(root, "junctions")
        connections = etree.SubElement(root, "connections")
        
        # Create edge
        edge = etree.SubElement(edges, "edge",
                              id="test_road",
                              **{"from": "start_j",
                                 "to": "end_j"})
        
        # Create junction with invalid connection
        junction = etree.SubElement(junctions, "junction",
                                  id="start_j",
                                  type="priority",
                                  x="0",
                                  y="0",
                                  incLanes="non_existent_lane",
                                  intLanes="")
        
        with pytest.raises(ValueError) as exc_info:
            self.converter.convert_network(root)
        assert "Invalid junction connection" in str(exc_info.value)
    
    def test_invalid_speed_values(self):
        """Test handling of invalid speed values."""
        root = etree.Element("net")
        edges = etree.SubElement(root, "edges")
        edge = etree.SubElement(edges, "edge", id="test_road")
        lanes = etree.SubElement(edge, "lanes")
        # Create lane with negative speed
        lane = etree.SubElement(lanes, "lane",
                              id="test_lane",
                              index="0",
                              speed="-13.89",  # Invalid negative speed
                              length="100")
        
        with pytest.raises(ValueError) as exc_info:
            self.converter.convert_network(root)
        assert "Invalid speed value" in str(exc_info.value)
    
    def test_invalid_lane_index(self):
        """Test handling of invalid lane indices."""
        root = etree.Element("net")
        edges = etree.SubElement(root, "edges")
        edge = etree.SubElement(edges, "edge", id="test_road")
        lanes = etree.SubElement(edge, "lanes")
        # Create lane with invalid index
        lane = etree.SubElement(lanes, "lane",
                              id="test_lane",
                              index="invalid",  # Non-numeric index
                              speed="13.89",
                              length="100")
        
        with pytest.raises(ValueError) as exc_info:
            self.converter.convert_network(root)
        assert "Invalid lane index" in str(exc_info.value)
    
    def test_duplicate_lane_ids(self):
        """Test handling of duplicate lane IDs."""
        root = etree.Element("net")
        edges = etree.SubElement(root, "edges")
        edge = etree.SubElement(edges, "edge", id="test_road")
        lanes = etree.SubElement(edge, "lanes")
        # Create two lanes with same ID
        lane1 = etree.SubElement(lanes, "lane",
                               id="duplicate_lane",
                               index="0",
                               speed="13.89",
                               length="100")
        lane2 = etree.SubElement(lanes, "lane",
                               id="duplicate_lane",
                               index="1",
                               speed="13.89",
                               length="100")
        
        with pytest.raises(ValueError) as exc_info:
            self.converter.convert_network(root)
        assert "Duplicate lane ID" in str(exc_info.value)
    
    def test_invalid_junction_type(self):
        """Test handling of invalid junction types."""
        root = etree.Element("net")
        junctions = etree.SubElement(root, "junctions")
        # Create junction with invalid type
        junction = etree.SubElement(junctions, "junction",
                                  id="test_junction",
                                  type="invalid_type",  # Invalid junction type
                                  x="0",
                                  y="0")
        
        with pytest.raises(ValueError) as exc_info:
            self.converter.convert_network(root)
        assert "Invalid junction type" in str(exc_info.value)
    
    def test_missing_connection_attributes(self):
        """Test handling of missing connection attributes."""
        root = etree.Element("net")
        connections = etree.SubElement(root, "connections")
        # Create connection without required attributes
        connection = etree.SubElement(connections, "connection")
        
        with pytest.raises(ValueError) as exc_info:
            self.converter.convert_network(root)
        assert "Missing required connection attribute" in str(exc_info.value)
    
    def test_invalid_connection_direction(self):
        """Test handling of invalid connection directions."""
        root = etree.Element("net")
        connections = etree.SubElement(root, "connections")
        # Create connection with invalid direction
        connection = etree.SubElement(connections, "connection",
                                    **{"from": "road1",
                                       "to": "road2",
                                       "fromLane": "0",
                                       "toLane": "0",
                                       "dir": "invalid",  # Invalid direction
                                       "state": "M"})
        
        with pytest.raises(ValueError) as exc_info:
            self.converter.convert_network(root)
        assert "Invalid connection direction" in str(exc_info.value)
    
    def test_invalid_connection_state(self):
        """Test handling of invalid connection states."""
        root = etree.Element("net")
        connections = etree.SubElement(root, "connections")
        # Create connection with invalid state
        connection = etree.SubElement(connections, "connection",
                                    **{"from": "road1",
                                       "to": "road2",
                                       "fromLane": "0",
                                       "toLane": "0",
                                       "dir": "s",
                                       "state": "invalid"})  # Invalid state
        
        with pytest.raises(ValueError) as exc_info:
            self.converter.convert_network(root)
        assert "Invalid connection state" in str(exc_info.value)
    
    def test_non_sequential_lane_indices(self):
        """Test handling of non-sequential lane indices."""
        root = etree.Element("net")
        edges = etree.SubElement(root, "edges")
        edge = etree.SubElement(edges, "edge", id="test_road")
        lanes = etree.SubElement(edge, "lanes")
        # Create lanes with non-sequential indices
        lane1 = etree.SubElement(lanes, "lane",
                               id="lane1",
                               index="0",
                               speed="13.89",
                               length="100")
        lane2 = etree.SubElement(lanes, "lane",
                               id="lane2",
                               index="2",  # Skipping index 1
                               speed="13.89",
                               length="100")
        
        with pytest.raises(ValueError) as exc_info:
            self.converter.convert_network(root)
        assert "Non-sequential lane indices" in str(exc_info.value)
    
    def test_invalid_coordinate_values(self):
        """Test handling of invalid coordinate values."""
        root = etree.Element("net")
        junctions = etree.SubElement(root, "junctions")
        # Create junction with invalid coordinates
        junction = etree.SubElement(junctions, "junction",
                                  id="test_junction",
                                  type="priority",
                                  x="invalid",  # Invalid x coordinate
                                  y="0")
        
        with pytest.raises(ValueError) as exc_info:
            self.converter.convert_network(root)
        assert "Invalid coordinate value" in str(exc_info.value)

if __name__ == '__main__':
    unittest.main() 