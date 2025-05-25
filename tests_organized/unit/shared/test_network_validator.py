"""Tests for the NetworkValidator class."""

import unittest
from src.validation.network_validator import NetworkValidator, ValidationResult

class TestNetworkValidator(unittest.TestCase):
    """Test cases for NetworkValidator."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.validator = NetworkValidator()
        
        # Create a valid network for testing
        self.valid_network = {
            "edges": [
                {
                    "id": "edge1",
                    "from": "junction1",
                    "to": "junction2",
                    "lanes": [
                        {
                            "id": "edge1_0",
                            "index": 0,
                            "speed": 50.0,
                            "length": 100.0,
                            "shape": [(0, 0), (100, 0)]
                        }
                    ]
                }
            ],
            "junctions": [
                {
                    "id": "junction1",
                    "type": "priority",
                    "x": 0.0,
                    "y": 0.0,
                    "incLanes": [],
                    "intLanes": []
                },
                {
                    "id": "junction2",
                    "type": "priority",
                    "x": 100.0,
                    "y": 0.0,
                    "incLanes": ["edge1_0"],
                    "intLanes": []
                }
            ],
            "connections": [
                {
                    "from": "edge1",
                    "to": "edge2",
                    "fromLane": 0,
                    "toLane": 0,
                    "dir": "s",
                    "state": "="
                }
            ]
        }
    
    def test_valid_network(self):
        """Test validation of a valid network."""
        result = self.validator.validate_network(self.valid_network)
        self.assertTrue(result.is_valid)
        self.assertEqual(len(result.errors), 0)
        self.assertEqual(len(result.warnings), 0)
    
    def test_missing_sections(self):
        """Test validation with missing required sections."""
        network = {"edges": []}  # Missing junctions and connections
        result = self.validator.validate_network(network)
        self.assertFalse(result.is_valid)
        self.assertTrue(any("Missing required sections" in error for error in result.errors))
    
    def test_invalid_edge_attributes(self):
        """Test validation of edges with invalid attributes."""
        network = self.valid_network.copy()
        network["edges"][0].pop("id")  # Remove required id attribute
        
        result = self.validator.validate_network(network)
        self.assertFalse(result.is_valid)
        self.assertTrue(any("Edge missing required 'id' attribute" in error for error in result.errors))
    
    def test_invalid_lane_sequence(self):
        """Test validation of non-sequential lane indices."""
        network = self.valid_network.copy()
        network["edges"][0]["lanes"].append({
            "id": "edge1_2",
            "index": 2,  # Skip index 1
            "speed": 50.0,
            "length": 100.0,
            "shape": [(0, 0), (100, 0)]
        })
        
        result = self.validator.validate_network(network)
        self.assertFalse(result.is_valid)
        self.assertTrue(any("non-sequential lane indices" in error for error in result.errors))
    
    def test_invalid_junction_type(self):
        """Test validation of invalid junction type."""
        network = self.valid_network.copy()
        network["junctions"][0]["type"] = "invalid_type"
        
        result = self.validator.validate_network(network)
        self.assertFalse(result.is_valid)
        self.assertTrue(any("Invalid junction type" in error for error in result.errors))
    
    def test_invalid_connection_direction(self):
        """Test validation of invalid connection direction."""
        network = self.valid_network.copy()
        network["connections"][0]["dir"] = "invalid"
        
        result = self.validator.validate_network(network)
        self.assertFalse(result.is_valid)
        self.assertTrue(any("Invalid connection direction" in error for error in result.errors))
    
    def test_duplicate_connection(self):
        """Test validation of duplicate connections."""
        network = self.valid_network.copy()
        network["connections"].append(network["connections"][0])  # Add duplicate connection
        
        result = self.validator.validate_network(network)
        self.assertFalse(result.is_valid)
        self.assertTrue(any("Duplicate connection" in error for error in result.errors))
    
    def test_isolated_edge(self):
        """Test validation of isolated edges."""
        network = self.valid_network.copy()
        network["edges"].append({
            "id": "isolated_edge",
            "from": "junction1",
            "to": "junction2",
            "lanes": [
                {
                    "id": "isolated_edge_0",
                    "index": 0,
                    "speed": 50.0,
                    "length": 100.0,
                    "shape": [(0, 0), (100, 0)]
                }
            ]
        })
        
        result = self.validator.validate_network(network)
        self.assertFalse(result.is_valid)
        self.assertTrue(any("is isolated" in error for error in result.errors))
    
    def test_invalid_lane_geometry(self):
        """Test validation of invalid lane geometry."""
        network = self.valid_network.copy()
        network["edges"][0]["lanes"][0]["shape"] = [(0, 0), (0.05, 0)]  # Points too close
        
        result = self.validator.validate_network(network)
        self.assertFalse(result.is_valid)
        self.assertTrue(any("Points too close together" in error for error in result.errors))
    
    def test_invalid_junction_shape(self):
        """Test validation of invalid junction shape."""
        network = self.valid_network.copy()
        network["junctions"][0]["shape"] = [(0, 0), (1, 0), (1, 1)]  # Not closed
        
        result = self.validator.validate_network(network)
        self.assertFalse(result.is_valid)
        self.assertTrue(any("shape must be closed" in error for error in result.errors))
    
    def test_mismatched_shape_length(self):
        """Test validation of mismatched shape and lane lengths."""
        network = self.valid_network.copy()
        network["edges"][0]["lanes"][0]["length"] = 200.0  # Different from shape length
        
        result = self.validator.validate_network(network)
        self.assertFalse(result.is_valid)
        self.assertTrue(any("Shape length does not match lane length" in error for error in result.errors))
    
    def test_invalid_coordinates(self):
        """Test validation of invalid junction coordinates."""
        network = self.valid_network.copy()
        network["junctions"][0]["x"] = "invalid"  # Non-numeric coordinate
        
        result = self.validator.validate_network(network)
        self.assertFalse(result.is_valid)
        self.assertTrue(any("must have valid x,y coordinates" in error for error in result.errors))
    
    def test_invalid_lane_references(self):
        """Test validation of invalid lane references in junctions."""
        network = self.valid_network.copy()
        network["junctions"][0]["incLanes"] = ["nonexistent_lane"]
        
        result = self.validator.validate_network(network)
        self.assertFalse(result.is_valid)
        self.assertTrue(any("references non-existent lane" in error for error in result.errors))
    
    def test_warning_isolated_lane(self):
        """Test warning for isolated lanes."""
        network = self.valid_network.copy()
        network["edges"][0]["lanes"].append({
            "id": "edge1_1",
            "index": 1,
            "speed": 50.0,
            "length": 100.0,
            "shape": [(0, 0), (100, 0)]
        })
        
        result = self.validator.validate_network(network)
        self.assertTrue(result.is_valid)  # Should be valid
        self.assertTrue(any("has no connections" in warning for warning in result.warnings))

if __name__ == "__main__":
    unittest.main() 