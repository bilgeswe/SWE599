"""
Advanced SUMO to OpenDRIVE converter with enhanced features.

This module provides advanced conversion capabilities from SUMO network format (.net.xml)
to OpenDRIVE format (.xodr), including:
- Complex geometry handling (curves, spirals)
- Proper reference line calculation
- Traffic signal conversion
- Enhanced junction connections
- Validation checks
"""

import os
import math
import logging
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple, Any
from xml.etree import ElementTree as ET
from lxml import etree
from datetime import datetime

import numpy as np
from scipy.interpolate import splprep, splev

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class Point:
    """Represents a 2D point with x, y coordinates."""
    x: float
    y: float

@dataclass
class Lane:
    """Represents a lane in the network."""
    id: str
    index: int
    width: float
    speed: float
    type: str
    length: float = 0.0
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get a lane attribute with a default value."""
        return getattr(self, key, default)

@dataclass
class Edge:
    """Represents a road edge with lanes and geometry."""
    id: str
    from_node: str
    to_node: str
    priority: str
    type: str
    lanes: List[Lane]
    shape: List[Point]
    speed: str
    
    @property
    def length(self) -> float:
        """Calculate the length of the edge from its lanes."""
        if self.lanes and len(self.lanes) > 0:
            # Get length from the first lane
            return float(self.lanes[0].get('length', 0.0))
        return 0.0

@dataclass
class Junction:
    """Represents a junction with connections."""
    id: str
    type: str
    connections: List[Tuple[str, str, str]]  # (from_edge, to_edge, via_lane)
    shape: List[Point]

@dataclass
class TrafficSignal:
    """Represents a traffic signal with timing information."""
    id: str
    type: str
    location: Point
    phases: List[Dict[str, str]]
    connections: List[Tuple[str, str]]  # (incoming_edge, outgoing_edge)

class AdvancedSumoNetworkParser:
    """Parser for SUMO network files with enhanced geometry handling."""
    
    def __init__(self, net_file: str):
        """Initialize the parser with a SUMO network file."""
        self.net_file = net_file
        self.edges: Dict[str, Edge] = {}
        self.junctions: Dict[str, Junction] = {}
        self.traffic_signals: Dict[str, TrafficSignal] = {}
        
    def parse(self) -> None:
        """Parse the SUMO network file with enhanced geometry handling."""
        try:
            tree = etree.parse(self.net_file)
            root = tree.getroot()
            
            # Parse edges with enhanced geometry
            self._parse_edges(root)
            
            # Parse junctions with enhanced connection handling
            self._parse_junctions(root)
            
            # Parse traffic signals with enhanced timing information
            self._parse_traffic_signals(root)
            
            # Validate the parsed network
            self._validate_network()
            
        except ValidationError:
            # Let ValidationError propagate for testability
            raise
        except Exception as e:
            logger.error(f"Error parsing SUMO network: {str(e)}")
            raise

    def _parse_edges(self, root: etree.Element) -> None:
        """Parse edges with enhanced geometry handling."""
        for edge in root.findall(".//edge"):
            edge_id = edge.get("id")
            from_node = edge.get("from")
            to_node = edge.get("to")
            priority = edge.get("priority", "0")  # Store as string, validate later
            edge_type = edge.get("type", "highway.local")
            
            # Parse lanes
            lanes = []
            for lane in edge.findall(".//lane"):
                lane_id = lane.get("id")
                lane_index = lane.get("index")  # No default
                lane_speed = lane.get("speed")  # No default
                lane_width = lane.get("width")  # No default
                lane_length = lane.get("length", "0.0")  # Optional
                
                lanes.append(Lane(
                    id=lane_id,
                    index=lane_index,  # Will convert in validation
                    width=lane_width,  # Will convert in validation
                    speed=lane_speed,  # Will convert in validation
                    type="driving",
                    length=lane_length  # Will convert in validation if needed
                ))
            
            # Parse shape
            shape = []
            for lane in edge.findall(".//lane"):
                shape_str = lane.find("shape").text if lane.find("shape") is not None else None
                if shape_str:
                    points = [tuple(map(float, p.split(","))) for p in shape_str.split()]
                    shape = [Point(x, y) for x, y in points]
                    print(f"DEBUG: Parsed shape for edge {edge_id}: {shape}")
                    break  # Use first lane's shape
            
            self.edges[edge_id] = Edge(
                id=edge_id,
                from_node=from_node,
                to_node=to_node,
                priority=priority,  # Will validate/convert later
                type=edge_type,
                lanes=lanes,
                shape=shape,
                speed=edge.get("speed", "13.89")  # Store as string, validate later
            )

    def _parse_junctions(self, root: etree.Element) -> None:
        """Parse junctions with enhanced connection handling."""
        # First pass: Create junction objects
        for junction in root.findall(".//junction"):
            junction_id = junction.get("id")
            if junction_id.startswith(":"):  # Skip internal junctions
                continue
                
            junction_type = junction.get("type", "priority")
            
            # Create junction with empty connections
            self.junctions[junction_id] = Junction(
                id=junction_id,
                type=junction_type,
                connections=[],
                shape=[]  # Shape will be added later if needed
            )
        
        # Second pass: Add connections
        for connection in root.findall(".//connection"):
            from_edge = connection.get("from")
            to_edge = connection.get("to")
            from_lane = connection.get("fromLane")
            to_lane = connection.get("toLane")
            via_lane = connection.get("via", "")

            # Check for invalid connections
            valid_from = (from_edge in self.edges) or (from_edge in self.junctions)
            valid_to = (to_edge in self.edges) or (to_edge in self.junctions)
            if not valid_from or not valid_to:
                raise ValidationError(f"Invalid connection: from='{from_edge}' to='{to_edge}'")

            if from_edge and to_edge:
                # Case 1: Connection between two edges
                if from_edge in self.edges and to_edge in self.edges:
                    junction_id = self.edges[from_edge].to_node
                    if junction_id in self.junctions:
                        # Construct via lane if not provided
                        if not via_lane and from_lane is not None and to_lane is not None:
                            via_lane = f"{from_edge}_{from_lane}_{to_edge}_{to_lane}"
                        self.junctions[junction_id].connections.append((from_edge, to_edge, via_lane))
                # Case 2: Connection from junction to edge
                elif from_edge in self.junctions and to_edge in self.edges:
                    junction_id = from_edge
                    if junction_id in self.junctions:
                        self.junctions[junction_id].connections.append((from_edge, to_edge, via_lane))
                # Case 3: Connection from edge to junction
                elif from_edge in self.edges and to_edge in self.junctions:
                    junction_id = to_edge
                    if junction_id in self.junctions:
                        self.junctions[junction_id].connections.append((from_edge, to_edge, via_lane))
                # Case 4: Connection between junctions
                elif from_edge in self.junctions and to_edge in self.junctions:
                    junction_id = from_edge
                    if junction_id in self.junctions:
                        self.junctions[junction_id].connections.append((from_edge, to_edge, via_lane))
                        
        # Third pass: Add connections for junctions without any
        for junction_id, junction in self.junctions.items():
            if not junction.connections:
                # Find edges that connect to this junction
                incoming_edges = []
                outgoing_edges = []
                for edge_id, edge in self.edges.items():
                    if edge.to_node == junction_id:
                        incoming_edges.append(edge_id)
                    if edge.from_node == junction_id:
                        outgoing_edges.append(edge_id)
                
                # Add default connections between incoming and outgoing edges
                for from_edge in incoming_edges:
                    for to_edge in outgoing_edges:
                        # Add a connection for each lane
                        from_edge_obj = self.edges[from_edge]
                        to_edge_obj = self.edges[to_edge]
                        for i in range(min(len(from_edge_obj.lanes), len(to_edge_obj.lanes))):
                            via_lane = f"{from_edge}_{i}_{to_edge}_{i}"
                            junction.connections.append((from_edge, to_edge, via_lane))

    def _parse_traffic_signals(self, root: etree.Element) -> None:
        """Parse traffic signals with enhanced timing information."""
        for tls in root.findall(".//tlLogic"):
            signal_id = tls.get("id")
            signal_type = tls.get("type", "static")
            
            # Parse phases
            phases = []
            for phase in tls.findall(".//phase"):
                phases.append({
                    "duration": phase.get("duration", "30"),
                    "state": phase.get("state", "")
                })
            
            # Create traffic signal
            self.traffic_signals[signal_id] = TrafficSignal(
                id=signal_id,
                type=signal_type,
                location=Point(0, 0),  # Location will be updated later
                phases=phases,
                connections=[]  # Connections will be added later
            )

    def _validate_network(self) -> bool:
        """Validate the entire network."""
        self._validate_network_structure()
        self._validate_geometry()
        self._validate_junctions()
        self._validate_traffic_signals()
        self._validate_lane_connections()
        self._validate_lane_properties()
        self._validate_junction_types()
        self._validate_road_properties()
        self._validate_elevation_profiles()
        logger.info("Network validation completed successfully")
        return True

    def _validate_network_structure(self) -> bool:
        """Validate basic network structure."""
        try:
            # Check if we have any edges
            if not self.edges:
                logger.warning("Network has no edges")
                return False
                
            # Check if we have any junctions
            if not self.junctions:
                logger.warning("Network has no junctions")
                return False
                
            # Check edge-junction connections
            for edge_id, edge in self.edges.items():
                if edge.from_node not in self.junctions:
                    logger.warning(f"Edge {edge_id} is not properly connected to junctions")
                    return False
                if edge.to_node not in self.junctions:
                    logger.warning(f"Edge {edge_id} is not properly connected to junctions")
                    return False
                    
            # Check junction connections
            for junction_id, junction in self.junctions.items():
                if not junction.connections:
                    logger.warning(f"Junction {junction_id} has no connections")
                    return False
                    
            return True
            
        except Exception as e:
            logger.error(f"Error validating network structure: {str(e)}")
            return False

    def _validate_geometry(self) -> bool:
        print("DEBUG: _validate_geometry called")
        try:
            for edge_id, edge in self.edges.items():
                print(f"Validating geometry for edge: {edge_id}, shape: {[ (p.x, p.y) for p in edge.shape ]}")
                if not edge.shape:
                    print(f"Edge {edge_id} has no shape, returning False")
                    logger.warning(f"Edge {edge_id} has no shape")
                    return False
                # Check for self-intersecting roads
                if self._is_self_intersecting(edge.shape):
                    print(f"Edge {edge_id} is self-intersecting!")
                    raise ValidationError(f"Edge {edge_id} has a self-intersecting shape")
                # Check for sharp angles
                if self._has_sharp_angle(edge.shape):
                    print(f"Edge {edge_id} has a sharp angle!")
                    raise ValidationError(f"Edge {edge_id} has a sharp angle (less than 30 degrees)")
                # Check for minimum number of points
                if len(edge.shape) < 2:
                    print(f"Edge {edge_id} has insufficient shape points, returning False")
                    logger.warning(f"Edge {edge_id} has insufficient shape points")
                    return False
            return True
        except ValidationError:
            # Let ValidationError propagate for testability
            raise
        except Exception as e:
            logger.error(f"Error validating geometry: {str(e)}")
            return False

    def _has_sharp_angle(self, shape: List[Point]) -> bool:
        """Check if a road shape contains any sharp angles (less than 30 degrees).
        
        Args:
            shape: List of points defining the road shape
            
        Returns:
            bool: True if the shape contains a sharp angle, False otherwise
        """
        if len(shape) < 3:  # Need at least 3 points to form an angle
            return False
            
        for i in range(1, len(shape) - 1):
            p1 = shape[i - 1]
            p2 = shape[i]
            p3 = shape[i + 1]
            
            # Calculate vectors
            v1x = p1.x - p2.x
            v1y = p1.y - p2.y
            v2x = p3.x - p2.x
            v2y = p3.y - p2.y
            
            # Calculate angle using dot product
            dot_product = v1x * v2x + v1y * v2y
            mag1 = math.sqrt(v1x * v1x + v1y * v1y)
            mag2 = math.sqrt(v2x * v2x + v2y * v2y)
            
            # Avoid division by zero
            if mag1 == 0 or mag2 == 0:
                continue
                
            cos_angle = dot_product / (mag1 * mag2)
            cos_angle = max(-1.0, min(1.0, cos_angle))  # Clamp to [-1, 1]
            angle = math.degrees(math.acos(cos_angle))
            print(f"DEBUG: Angle at {i} ({(p1.x, p1.y)}, {(p2.x, p2.y)}, {(p3.x, p3.y)}): {angle} degrees")
            
            # Check if angle is sharp (less than 30 degrees)
            if angle < 30:
                print(f"Sharp angle detected: {angle} degrees at index {i}")
                return True
                
        return False

    def _is_self_intersecting(self, shape: List[Point]) -> bool:
        """Check if a road shape is self-intersecting.
        
        Args:
            shape: List of points defining the road shape
            
        Returns:
            bool: True if the shape is self-intersecting, False otherwise
        """
        print("DEBUG: _is_self_intersecting called")
        if len(shape) < 4:  # Need at least 4 points to form a self-intersection
            return False
        # Debug print
        print(f"Checking self-intersection for shape: {[ (p.x, p.y) for p in shape ]}")
        # Check each line segment against all other segments
        for i in range(len(shape) - 1):
            p1 = shape[i]
            p2 = shape[i + 1]
            for j in range(i + 2, len(shape) - 1):
                p3 = shape[j]
                p4 = shape[j + 1]
                print(f"Checking segments ({p1.x},{p1.y})-({p2.x},{p2.y}) and ({p3.x},{p3.y})-({p4.x},{p4.y})")
                if self._do_segments_intersect(p1, p2, p3, p4):
                    print("Intersection detected!")
                    return True
        return False

    def _do_segments_intersect(self, p1: Point, p2: Point, p3: Point, p4: Point) -> bool:
        """Check if two line segments intersect.
        
        Args:
            p1, p2: Endpoints of first line segment
            p3, p4: Endpoints of second line segment
            
        Returns:
            bool: True if segments intersect, False otherwise
        """
        def ccw(A: Point, B: Point, C: Point) -> bool:
            return (C.y - A.y) * (B.x - A.x) > (B.y - A.y) * (C.x - A.x)
        result = ccw(p1, p3, p4) != ccw(p2, p3, p4) and ccw(p1, p2, p3) != ccw(p1, p2, p4)
        print(f"Segments ({p1.x},{p1.y})-({p2.x},{p2.y}) and ({p3.x},{p3.y})-({p4.x},{p4.y}) intersect: {result}")
        return result

    def _validate_junctions(self) -> bool:
        """Validate junction properties and connections."""
        try:
            for junction_id, junction in self.junctions.items():
                # Check junction type
                if not junction.type:
                    logger.warning(f"Junction {junction_id} has no type")
                    return False
                
                # Check connections
                if not junction.connections:
                    logger.warning(f"Junction {junction_id} has no connections")
                    return False
                
                # Validate each connection
                for from_edge, to_edge, via_lane in junction.connections:
                    # Case 1: Connection between two edges
                    if from_edge in self.edges and to_edge in self.edges:
                        # Check via lane
                        if via_lane and not self._is_valid_via_lane(from_edge, to_edge, via_lane):
                            logger.warning(f"Junction {junction_id} has invalid via_lane: {via_lane}")
                            return False
                    # Case 2: Connection from junction to edge
                    elif from_edge == junction_id and to_edge in self.edges:
                        continue  # Valid case
                    # Case 3: Connection from edge to junction
                    elif from_edge in self.edges and to_edge == junction_id:
                        continue  # Valid case
                    # Case 4: Connection between junctions
                    elif from_edge == junction_id and to_edge in self.junctions:
                        continue  # Valid case
                    else:
                        logger.warning(f"Junction {junction_id} has invalid connection: {from_edge} -> {to_edge}")
                        return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error validating junctions: {str(e)}")
            return False

    def _is_valid_via_lane(self, from_edge: str, to_edge: str, via_lane: str) -> bool:
        """Check if a via lane is valid for the given edges."""
        if from_edge not in self.edges or to_edge not in self.edges:
            return False
            
        # Parse via lane information
        try:
            # Check if via lane has the correct format: from_edge_from_lane_to_edge_to_lane
            expected_prefix = f"{from_edge}_"
            expected_suffix = f"_{to_edge}_"
            
            if not via_lane.startswith(expected_prefix) or expected_suffix not in via_lane:
                return False
                
            # Extract lane indices from the via lane string
            # Format: edge1_0_edge2_0 -> from_lane=0, to_lane=0
            parts = via_lane.split('_')
            if len(parts) != 4:  # Need exactly: edge1_0_edge2_0
                return False
                
            # Verify edge names in via lane
            if parts[0] != from_edge or parts[2] != to_edge:
                return False
                
            try:
                from_lane_idx = int(parts[1])  # Second part is from_lane
                to_lane_idx = int(parts[3])    # Fourth part is to_lane
            except ValueError:
                return False
                
            # Check if lanes exist in their respective edges
            from_edge_data = self.edges[from_edge]
            to_edge_data = self.edges[to_edge]
            
            # Check if the lane indices are within the valid range
            from_lane_exists = 0 <= from_lane_idx < len(from_edge_data.lanes)
            to_lane_exists = 0 <= to_lane_idx < len(to_edge_data.lanes)
            
            # Check if the lane indices match the actual lane indices in the edges
            if from_lane_exists:
                from_lane = from_edge_data.lanes[from_lane_idx]
                if from_lane.index != from_lane_idx:
                    return False
                    
            if to_lane_exists:
                to_lane = to_edge_data.lanes[to_lane_idx]
                if to_lane.index != to_lane_idx:
                    return False
                    
            return from_lane_exists and to_lane_exists
            
        except (ValueError, IndexError, AttributeError):
            return False

    def _validate_traffic_signals(self) -> bool:
        """Validate traffic signal properties and timing."""
        try:
            for tl_id, signal in self.traffic_signals.items():
                # Check signal type
                if not signal.type:
                    logger.warning(f"Traffic signal {tl_id} has no type")
                    return False
                
                # Check phases
                if not signal.phases:
                    logger.warning(f"Traffic signal {tl_id} has no phases")
                    return False
                
                # Validate each phase
                total_duration = 0
                for phase in signal.phases:
                    try:
                        duration = float(phase.get("duration", 0))
                        if duration <= 0:
                            logger.warning(f"Traffic signal {tl_id} has invalid phase duration")
                            return False
                        total_duration += duration
                        
                        # Check state
                        state = phase.get("state", "")
                        if not state:
                            logger.warning(f"Traffic signal {tl_id} has empty phase state")
                            return False
                        if not all(c in "rRgGyY" for c in state):
                            logger.warning(f"Traffic signal {tl_id} has invalid phase state")
                            return False
                    except ValueError:
                        logger.warning(f"Traffic signal {tl_id} has invalid phase duration format")
                        return False
                
                # Check cycle time
                if total_duration > 300:  # 5 minutes
                    logger.warning(f"Traffic signal {tl_id} has long cycle time: {total_duration} seconds")
                    return False
                    
            return True
            
        except Exception as e:
            logger.error(f"Error validating traffic signals: {str(e)}")
            return False

    def _validate_lane_connections(self) -> bool:
        """Validate lane connections and properties."""
        try:
            for edge_id, edge in self.edges.items():
                # Check lane properties
                for lane in edge.lanes:
                    if lane.width <= 0:
                        logger.warning(f"Edge {edge_id}, lane {lane.id} has invalid width")
                        return False
                    if lane.speed <= 0:
                        logger.warning(f"Edge {edge_id}, lane {lane.id} has invalid speed")
                        return False
                    
                    # Check lane type
                    if not lane.type:
                        logger.warning(f"Edge {edge_id}, lane {lane.id} has no type")
                        return False
                
                # Check lane continuity
                if edge.lanes:
                    indices = [lane.index for lane in edge.lanes]
                    if sorted(indices) != list(range(min(indices), max(indices) + 1)):
                        logger.warning(f"Edge {edge_id} has discontinuous lane indices")
                        return False
            
            # Check junction connections
            for junction_id, junction in self.junctions.items():
                for from_edge, to_edge, via_lane in junction.connections:
                    # Check if the connection is between edges
                    if from_edge in self.edges and to_edge in self.edges:
                        # Check if the via lane is valid
                        if not self._is_valid_via_lane(from_edge, to_edge, via_lane):
                            logger.warning(f"Invalid via lane {via_lane} in junction {junction_id}")
                            return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error validating lane connections: {str(e)}")
            return False

    def _validate_lane_properties(self) -> bool:
        """Validate lane properties including width, speed, and indices. Convert to correct types."""
        for edge_id, edge in self.edges.items():
            # Convert lane indices to int and check for discontinuity
            lane_indices = []
            for lane in edge.lanes:
                # Check for missing required attributes
                if lane.id is None or lane.id == "" or lane.index is None or lane.index == "" or lane.speed is None or lane.speed == "" or lane.width is None or lane.width == "":
                    raise ValidationError(f"Missing required attributes for lane {lane.id}")
                try:
                    lane.index = int(lane.index)
                except Exception:
                    raise ValidationError(f"Invalid lane index '{lane.index}' for lane {lane.id}")
                lane_indices.append(lane.index)
            if not self._is_continuous_sequence(lane_indices):
                raise ValidationError(f"Edge {edge_id} has discontinuous lane indices: {lane_indices}")

            for lane in edge.lanes:
                # Convert and validate lane width
                try:
                    lane.width = float(lane.width)
                except Exception:
                    raise ValidationError(f"Invalid lane width '{lane.width}' for lane {lane.id}")
                if lane.width <= 0:
                    raise ValidationError(f"Invalid lane width {lane.width} for lane {lane.id}")

                # Convert and validate speed limit
                try:
                    lane.speed = float(lane.speed)
                except Exception:
                    raise ValidationError(f"Invalid speed limit '{lane.speed}' for lane {lane.id}")
                if lane.speed <= 0:
                    raise ValidationError(f"Invalid speed limit {lane.speed} for lane {lane.id}")

                # Convert and validate lane length if present
                if hasattr(lane, 'length') and lane.length is not None:
                    try:
                        lane.length = float(lane.length)
                    except Exception:
                        raise ValidationError(f"Invalid lane length '{lane.length}' for lane {lane.id}")

        return True

    def _validate_junction_types(self) -> bool:
        """Validate junction types."""
        valid_types = {'priority', 'traffic_light', 'right_before_left', 'unregulated', 'dead_end', 'rail_signal'}
        for junction_id, junction in self.junctions.items():
            if junction.type not in valid_types:
                raise ValidationError(f"Invalid junction type '{junction.type}' for junction {junction_id}")
        return True

    def _validate_road_properties(self) -> bool:
        """Validate road properties including priority and type. Convert to correct types."""
        for edge_id, edge in self.edges.items():
            # Convert and validate road priority
            try:
                edge.priority = int(edge.priority)
            except Exception:
                raise ValidationError(f"Invalid road priority '{edge.priority}' for edge {edge_id}")
            if edge.priority < -1 or edge.priority > 78:  # SUMO's priority range
                raise ValidationError(f"Invalid road priority {edge.priority} for edge {edge_id}")

            # Convert and validate edge speed
            try:
                edge.speed = float(edge.speed)
            except Exception:
                raise ValidationError(f"Invalid edge speed '{edge.speed}' for edge {edge_id}")
            if edge.speed <= 0:
                raise ValidationError(f"Invalid edge speed {edge.speed} for edge {edge_id}")

            # Validate road type
            if not edge.type:
                raise ValidationError(f"Missing road type for edge {edge_id}")
        return True

    def _is_continuous_sequence(self, numbers: List[int]) -> bool:
        """Check if a list of numbers forms a continuous sequence."""
        if not numbers:
            return True
        sorted_numbers = sorted(numbers)
        return sorted_numbers == list(range(min(numbers), max(numbers) + 1))

    def _validate_elevation_profiles(self) -> bool:
        """Validate elevation profiles."""
        try:
            for edge_id, edge in self.edges.items():
                if not edge.shape:
                    continue
                    
                # Check for extreme elevation changes
                if len(edge.shape) > 1:
                    z_values = [p.z for p in edge.shape if hasattr(p, 'z')]
                    if z_values:
                        max_change = max(abs(z_values[i] - z_values[i-1]) 
                                       for i in range(1, len(z_values)))
                        if max_change > 0.1:  # 10% grade
                            logger.warning(f"Edge {edge_id} has steep elevation changes")
                            return False
                            
            return True
            
        except Exception as e:
            logger.error(f"Error validating elevation profiles: {str(e)}")
            return False

    def _calculate_reference_line(self, edge: Edge) -> Tuple[List[Point], List[float]]:
        """Calculate the reference line and its properties for a road edge."""
        if not edge.shape:
            return [], []
            
        # Convert shape points to numpy array
        points = np.array([(p.x, p.y) for p in edge.shape])
        
        # Calculate cumulative distances
        distances = np.zeros(len(points))
        for i in range(1, len(points)):
            dx = points[i][0] - points[i-1][0]
            dy = points[i][1] - points[i-1][1]
            distances[i] = distances[i-1] + np.sqrt(dx*dx + dy*dy)
        
        # Ensure we have enough points for spline interpolation
        if len(points) < 4:
            # For small number of points, use linear interpolation
            s_new = np.linspace(0, distances[-1], 100)
            x_new = np.interp(s_new, distances, points[:, 0])
            y_new = np.interp(s_new, distances, points[:, 1])
        else:
            # Use cubic spline interpolation
            tck, u = splprep(points.T, u=distances, s=0, k=min(3, len(points)-1))
            s_new = np.linspace(0, distances[-1], 100)
            x_new, y_new = splev(s_new, tck)
        
        # Convert back to Point objects
        reference_points = [Point(x, y) for x, y in zip(x_new, y_new)]
        
        return reference_points, s_new.tolist()

    def _calculate_road_properties(self, reference_points: List[Point], s_values: List[float]) -> Tuple[List[float], List[float], List[float]]:
        """Calculate road properties along the reference line."""
        if not reference_points:
            return [], [], []
            
        # Convert to numpy arrays
        points = np.array([(p.x, p.y) for p in reference_points])
        
        # Calculate first derivatives
        dx = np.gradient(points[:, 0], s_values)
        dy = np.gradient(points[:, 1], s_values)
        
        # Calculate second derivatives
        d2x = np.gradient(dx, s_values)
        d2y = np.gradient(dy, s_values)
        
        # Calculate curvature
        curvature = np.abs(dx * d2y - dy * d2x) / (dx**2 + dy**2)**1.5
        
        # Calculate heading
        heading = np.arctan2(dy, dx)
        
        # Calculate superelevation (simplified version)
        superelevation = np.zeros_like(curvature)
        for i in range(len(curvature)):
            if abs(curvature[i]) > 0.01:  # Only apply superelevation on curves
                superelevation[i] = min(0.1, abs(curvature[i]) * 2)  # Max 10% superelevation
        
        return curvature.tolist(), heading.tolist(), superelevation.tolist()

    def _convert_signal_state(self, state: str) -> str:
        """Convert SUMO signal state to OpenDRIVE signal state."""
        state_mapping = {
            'r': '0',  # Red
            'y': '1',  # Yellow
            'g': '2',  # Green
            'G': '2',  # Green (capital)
            'Y': '1',  # Yellow (capital)
            'R': '0'   # Red (capital)
        }
        return ''.join(state_mapping.get(c, '0') for c in state)

    def _get_signal_type(self, signal_type: str) -> str:
        """Convert SUMO signal type to OpenDRIVE signal type."""
        type_mapping = {
            "static": "1000001",  # Standard traffic light
            "actuated": "1000002",  # Actuated traffic light
            "delay_based": "1000003",  # Delay-based traffic light
            "sotl": "1000004",  # Self-organizing traffic light
            "default": "1000001"  # Default to standard
        }
        return type_mapping.get(signal_type.lower(), type_mapping["default"])

    def _points_equal(self, p1: Point, p2: Point, tolerance: float = 1e-6) -> bool:
        """Check if two points are equal within a tolerance."""
        return (abs(p1.x - p2.x) < tolerance and 
                abs(p1.y - p2.y) < tolerance)
    
    def _calculate_angle(self, p1: Point, p2: Point, p3: Point) -> float:
        """Calculate the angle between three points."""
        # Calculate vectors
        v1x = p1.x - p2.x
        v1y = p1.y - p2.y
        v2x = p3.x - p2.x
        v2y = p3.y - p2.y
        
        # Calculate dot product
        dot_product = v1x * v2x + v1y * v2y
        
        # Calculate magnitudes
        mag1 = math.sqrt(v1x * v1x + v1y * v1y)
        mag2 = math.sqrt(v2x * v2x + v2y * v2y)
        
        # Calculate angle
        cos_angle = dot_product / (mag1 * mag2)
        cos_angle = max(-1.0, min(1.0, cos_angle))  # Clamp to [-1, 1]
        
        return math.acos(cos_angle)

    def _add_geometry(self, plan_view: etree.Element, edge: Edge) -> None:
        """Add geometry elements to the plan view."""
        if not edge.shape:
            return
            
        # Calculate reference line and its properties
        reference_points, s_values = self._calculate_reference_line(edge)
        curvatures, headings, superelevations = self._calculate_road_properties(reference_points, s_values)
        
        # Add geometry elements
        for i in range(len(reference_points) - 1):
            point = reference_points[i]
            next_point = reference_points[i + 1]
            
            # Calculate segment properties
            s = s_values[i]
            hdg = headings[i]
            length = s_values[i + 1] - s_values[i]
            curvature = curvatures[i]
            superelevation = superelevations[i]
            
            # Add geometry element
            geometry = etree.SubElement(plan_view, "geometry")
            geometry.set("s", str(s))
            geometry.set("x", str(point.x))
            geometry.set("y", str(point.y))
            geometry.set("hdg", str(hdg))
            geometry.set("length", str(length))
            
            # Determine geometry type based on curvature
            if abs(curvature) > 0.001:
                # Add arc
                arc = etree.SubElement(geometry, "arc")
                arc.set("curvature", str(curvature))
            else:
                # Add line element for straight segments
                line = etree.SubElement(geometry, "line")
            print(f"Segment {i}: curvature={curvature}")

class ValidationError(Exception):
    """Custom exception for validation errors."""
    pass

class AdvancedSumoToOpenDriveConverter:
    """Converter class to transform SUMO network to OpenDRIVE format."""
    
    def __init__(self, input_file: str, output_file: str):
        """Initialize the converter with input and output file paths."""
        self.input_file = input_file
        self.output_file = output_file
        self.parser = AdvancedSumoNetworkParser(input_file)
        
    def convert(self) -> None:
        """Convert SUMO network to OpenDRIVE format."""
        try:
            # Parse the SUMO network
            self.parser.parse()
            
            # Create OpenDRIVE XML structure
            root = self._create_opendrive_root()
            
            # Add header
            self._add_header(root)
            
            # Add roads
            self._add_roads(root)
            
            # Add junctions
            self._add_junctions(root)
            
            # Add controllers
            self._add_controllers(root)
            
            # Write to file
            tree = etree.ElementTree(root)
            tree.write(self.output_file, pretty_print=True, xml_declaration=True, encoding="UTF-8")
            
        except Exception as e:
            logger.error(f"Error during conversion: {str(e)}")
            raise
            
    def _create_opendrive_root(self) -> etree.Element:
        """Create the root element of OpenDRIVE XML."""
        NSMAP = {
            'xsi': 'http://www.w3.org/2001/XMLSchema-instance'
        }
        root = etree.Element("OpenDRIVE", nsmap=NSMAP)
        root.set('{http://www.w3.org/2001/XMLSchema-instance}noNamespaceSchemaLocation', 
                'http://www.opendrive.org/xsd/1.4/OpenDRIVE_1.4H.xsd')
        return root
        
    def _add_header(self, root: etree.Element) -> None:
        """Add header information to OpenDRIVE XML."""
        header = etree.SubElement(root, "header")
        header.set("revMajor", "1")
        header.set("revMinor", "4")
        header.set("name", os.path.basename(self.input_file))
        header.set("version", "1.00")
        header.set("date", datetime.now().strftime("%Y-%m-%d"))
        header.set("north", "0.0")
        header.set("south", "0.0")
        header.set("east", "0.0")
        header.set("west", "0.0")
        
    def _add_roads(self, root: etree.Element) -> None:
        """Add road elements to OpenDRIVE XML."""
        for edge_id, edge in self.parser.edges.items():
            road = etree.SubElement(root, "road")
            road.set("name", edge_id)
            road.set("length", str(edge.length))
            road.set("id", edge_id)
            road.set("junction", "-1")
            
            # Add road type
            type_elem = etree.SubElement(road, "type")
            type_elem.set("s", "0")
            type_elem.set("type", edge.type if hasattr(edge, "type") else "town")
            
            # Add planView
            plan_view = etree.SubElement(road, "planView")
            self.parser._add_geometry(plan_view, edge)
            
            # Add elevation profile
            elevation = etree.SubElement(road, "elevationProfile")
            
            # Add lanes
            lanes = etree.SubElement(road, "lanes")
            lane_section = etree.SubElement(lanes, "laneSection")
            lane_section.set("s", "0")
            
            # Add center lane
            center = etree.SubElement(lane_section, "center")
            
            # Add right lanes
            right = etree.SubElement(lane_section, "right")
            for lane in edge.lanes:
                lane_elem = etree.SubElement(right, "lane")
                lane_elem.set("id", str(lane.index))
                lane_elem.set("type", "driving")
                lane_elem.set("level", "false")
                
                width = etree.SubElement(lane_elem, "width")
                width.set("sOffset", "0")
                width.set("a", str(lane.width if hasattr(lane, "width") else 3.5))
                width.set("b", "0")
                width.set("c", "0")
                width.set("d", "0")
                
                speed = etree.SubElement(lane_elem, "speed")
                speed.set("sOffset", "0")
                speed.set("max", str(lane.speed))
            
    def _add_junctions(self, root: etree.Element) -> None:
        """Add junction elements to OpenDRIVE XML."""
        for junction_id, junction in self.parser.junctions.items():
            if junction.type != "internal":
                junction_elem = etree.SubElement(root, "junction")
                junction_elem.set("name", junction_id)
                junction_elem.set("id", junction_id)
                
                for connection in junction.connections:
                    connection_elem = etree.SubElement(junction_elem, "connection")
                    connection_elem.set("id", f"{connection[0]}_{connection[1]}")
                    connection_elem.set("incomingRoad", connection[0])
                    connection_elem.set("connectingRoad", connection[1])
                    connection_elem.set("contactPoint", "start")
                    
                    lane_link = etree.SubElement(connection_elem, "laneLink")
                    lane_link.set("from", "0")
                    lane_link.set("to", "0")
            
    def _add_controllers(self, root: etree.Element) -> None:
        """Add traffic signal controllers to OpenDRIVE XML."""
        for signal_id, signal in self.parser.traffic_signals.items():
            controller = etree.SubElement(root, "controller")
            controller.set("name", signal_id)
            controller.set("id", signal_id)
            controller.set("sequence", "0")
            
            control = etree.SubElement(controller, "control")
            control.set("signalId", signal_id)
            
            # Add signal phases
            for i, phase in enumerate(signal.phases):
                signal_phase = etree.SubElement(control, "phase")
                signal_phase.set("duration", phase["duration"])
                signal_phase.set("state", self.parser._convert_signal_state(phase["state"]))
                signal_phase.set("type", self.parser._get_signal_type(signal.type))
                signal_phase.set("id", str(i))

def main():
    """Main function for testing the converter."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Convert SUMO network to OpenDRIVE format")
    parser.add_argument("input_file", help="Input SUMO network file (.net.xml)")
    parser.add_argument("output_file", help="Output OpenDRIVE file (.xodr)")
    
    args = parser.parse_args()
    
    try:
        # Parse SUMO network
        sumo_parser = AdvancedSumoNetworkParser(args.input_file)
        sumo_parser.parse()
        
        # Generate OpenDRIVE
        converter = AdvancedSumoToOpenDriveConverter(args.input_file, args.output_file)
        converter.convert()
        
        logger.info(f"Successfully converted {args.input_file} to {args.output_file}")
        
    except Exception as e:
        logger.error(f"Error during conversion: {str(e)}")
        raise

if __name__ == "__main__":
    main() 