"""Network validator for validating converted road network data."""

from typing import List, Dict, Set, Optional, Tuple
import math
from dataclasses import dataclass
from enum import Enum
import numpy as np
from collections import defaultdict

class ValidationError(Exception):
    """Exception raised for network validation errors."""
    pass

class JunctionType(Enum):
    """Valid junction types."""
    PRIORITY = "priority"
    TRAFFIC_LIGHT = "traffic_light"
    DEAD_END = "dead_end"
    UNREGULATED = "unregulated"

class ConnectionDirection(Enum):
    """Valid connection directions."""
    STRAIGHT = "s"
    TURN = "t"
    LEFT = "l"
    RIGHT = "r"
    LEFT_TURN = "L"
    RIGHT_TURN = "R"

class ConnectionState(Enum):
    """Valid connection states."""
    MERGING = "M"
    DIVERGING = "m"
    EQUAL = "="
    MINOR = "-"
    ZERO = "0"

@dataclass
class ValidationResult:
    """Result of network validation."""
    is_valid: bool
    errors: List[str]
    warnings: List[str]
    statistics: Dict[str, float] = None

class NetworkValidator:
    """Validates converted road network data."""
    
    # Constants for validation
    MIN_SPEED = 0.0  # km/h
    MAX_SPEED = 200.0  # km/h
    MIN_LENGTH = 0.1  # meters
    MAX_LENGTH = 10000.0  # meters
    MIN_LANE_WIDTH = 2.5  # meters
    MAX_LANE_WIDTH = 5.0  # meters
    MIN_POINT_SPACING = 0.1  # meters
    MAX_POINT_SPACING = 100.0  # meters
    MIN_ANGLE = 0.0  # degrees
    MAX_ANGLE = 180.0  # degrees
    MIN_ELEVATION = -1000.0  # meters
    MAX_ELEVATION = 10000.0  # meters
    MIN_CURVATURE = 0.0  # 1/meters
    MAX_CURVATURE = 0.1  # 1/meters
    MIN_SLOPE = -0.3  # -30%
    MAX_SLOPE = 0.3  # 30%
    
    def __init__(self):
        """Initialize the network validator."""
        self.edge_ids: Set[str] = set()
        self.lane_ids: Set[str] = set()
        self.junction_ids: Set[str] = set()
        self.edge_connections: Dict[str, Set[str]] = {}
        self.lane_connections: Dict[str, Set[str]] = {}
        self.edge_priorities: Dict[str, int] = {}
        self.edge_functions: Dict[str, str] = {}
        self.statistics: Dict[str, float] = defaultdict(float)
    
    def validate_network(self, network_data: Dict) -> ValidationResult:
        """Validate the entire network.
        
        Args:
            network_data: Dictionary containing the converted network data
            
        Returns:
            ValidationResult containing validation status and any errors/warnings
        """
        self.edge_ids.clear()
        self.lane_ids.clear()
        self.junction_ids.clear()
        self.edge_connections.clear()
        self.lane_connections.clear()
        self.edge_priorities.clear()
        self.edge_functions.clear()
        self.statistics.clear()
        
        errors = []
        warnings = []
        
        # Validate basic structure
        if not self._validate_structure(network_data, errors):
            return ValidationResult(False, errors, warnings, dict(self.statistics))
        
        # Collect all IDs and attributes
        self._collect_ids(network_data)
        
        # Validate edges and lanes
        self._validate_edges(network_data["edges"], errors, warnings)
        
        # Validate junctions
        self._validate_junctions(network_data["junctions"], errors, warnings)
        
        # Validate connections
        self._validate_connections(network_data["connections"], errors, warnings)
        
        # Validate network connectivity
        self._validate_connectivity(network_data, errors, warnings)
        
        # Validate geometric consistency
        self._validate_geometry(network_data, errors, warnings)
        
        # Validate traffic rules
        self._validate_traffic_rules(network_data, errors, warnings)
        
        # Validate network topology
        self._validate_topology(network_data, errors, warnings)
        
        # Validate road characteristics
        self._validate_road_characteristics(network_data, errors, warnings)
        
        # Calculate network statistics
        self._calculate_statistics(network_data)
        
        return ValidationResult(len(errors) == 0, errors, warnings, dict(self.statistics))
    
    def _validate_structure(self, network_data: Dict, errors: List[str]) -> bool:
        """Validate basic network structure.
        
        Args:
            network_data: Network data dictionary
            errors: List to collect errors
            
        Returns:
            True if structure is valid, False otherwise
        """
        required_sections = {"edges", "junctions", "connections"}
        missing_sections = required_sections - set(network_data.keys())
        
        if missing_sections:
            errors.append(
                f"Missing required sections: {', '.join(missing_sections)}. "
                "Network data must contain edges, junctions, and connections."
            )
            return False
        
        if not isinstance(network_data["edges"], list):
            errors.append("Edges section must be a list")
            return False
        
        if not isinstance(network_data["junctions"], list):
            errors.append("Junctions section must be a list")
            return False
        
        if not isinstance(network_data["connections"], list):
            errors.append("Connections section must be a list")
            return False
        
        # Validate section sizes
        if len(network_data["edges"]) == 0:
            errors.append("Network must contain at least one edge")
            return False
        
        if len(network_data["junctions"]) == 0:
            errors.append("Network must contain at least one junction")
            return False
        
        return True
    
    def _collect_ids(self, network_data: Dict) -> None:
        """Collect all IDs and attributes from the network.
        
        Args:
            network_data: Network data dictionary
        """
        for edge in network_data["edges"]:
            self.edge_ids.add(edge["id"])
            self.edge_priorities[edge["id"]] = edge.get("priority", 0)
            self.edge_functions[edge["id"]] = edge.get("function", "normal")
            for lane in edge["lanes"]:
                self.lane_ids.add(lane["id"])
        
        for junction in network_data["junctions"]:
            self.junction_ids.add(junction["id"])
    
    def _validate_edges(self, edges: List[Dict], errors: List[str], warnings: List[str]) -> None:
        """Validate edges and their lanes.
        
        Args:
            edges: List of edge dictionaries
            errors: List to collect errors
            warnings: List to collect warnings
        """
        for edge in edges:
            # Validate edge attributes
            if not edge.get("id"):
                errors.append("Edge missing required 'id' attribute")
                continue
            
            if not edge.get("from") or not edge.get("to"):
                errors.append(f"Edge '{edge['id']}' missing required 'from' or 'to' attributes")
            
            # Validate edge function
            if edge.get("function") and edge["function"] not in {"normal", "internal", "connector"}:
                errors.append(
                    f"Invalid edge function '{edge['function']}' in edge '{edge['id']}'. "
                    "Must be one of: normal, internal, connector"
                )
            
            # Validate edge priority
            if edge.get("priority") is not None:
                try:
                    priority = int(edge["priority"])
                    if priority < -1 or priority > 78:
                        errors.append(
                            f"Invalid priority value {priority} in edge '{edge['id']}'. "
                            "Priority must be between -1 and 78"
                        )
                except ValueError:
                    errors.append(
                        f"Invalid priority value '{edge['priority']}' in edge '{edge['id']}'. "
                        "Priority must be an integer"
                    )
            
            # Validate lanes
            if not edge.get("lanes"):
                errors.append(f"Edge '{edge['id']}' has no lanes")
                continue
            
            # Validate lane sequence
            lane_indices = [lane["index"] for lane in edge["lanes"]]
            if sorted(lane_indices) != list(range(len(lane_indices))):
                errors.append(
                    f"Edge '{edge['id']}' has non-sequential lane indices. "
                    f"Found indices: {lane_indices}"
                )
            
            # Validate lane attributes
            for lane in edge["lanes"]:
                if not lane.get("id"):
                    errors.append(f"Lane missing required 'id' attribute in edge '{edge['id']}'")
                
                # Validate lane speed
                if lane.get("speed") is not None:
                    try:
                        speed = float(lane["speed"])
                        if speed < self.MIN_SPEED or speed > self.MAX_SPEED:
                            errors.append(
                                f"Invalid speed value {speed} km/h in lane '{lane.get('id')}'. "
                                f"Speed must be between {self.MIN_SPEED} and {self.MAX_SPEED} km/h"
                            )
                    except ValueError:
                        errors.append(
                            f"Invalid speed value '{lane['speed']}' in lane '{lane.get('id')}'. "
                            "Speed must be a number"
                        )
                
                # Validate lane length
                if lane.get("length") is not None:
                    try:
                        length = float(lane["length"])
                        if length < self.MIN_LENGTH or length > self.MAX_LENGTH:
                            errors.append(
                                f"Invalid length value {length} meters in lane '{lane.get('id')}'. "
                                f"Length must be between {self.MIN_LENGTH} and {self.MAX_LENGTH} meters"
                            )
                    except ValueError:
                        errors.append(
                            f"Invalid length value '{lane['length']}' in lane '{lane.get('id')}'. "
                            "Length must be a number"
                        )
                
                # Validate lane width
                if lane.get("width") is not None:
                    try:
                        width = float(lane["width"])
                        if width < self.MIN_LANE_WIDTH or width > self.MAX_LANE_WIDTH:
                            errors.append(
                                f"Invalid width value {width} meters in lane '{lane.get('id')}'. "
                                f"Width must be between {self.MIN_LANE_WIDTH} and {self.MAX_LANE_WIDTH} meters"
                            )
                    except ValueError:
                        errors.append(
                            f"Invalid width value '{lane['width']}' in lane '{lane.get('id')}'. "
                            "Width must be a number"
                        )
                
                # Validate lane shape
                if not lane.get("shape") or len(lane["shape"]) < 2:
                    errors.append(
                        f"Lane '{lane.get('id')}' in edge '{edge['id']}' "
                        "must have at least two shape points"
                    )
                else:
                    self._validate_lane_geometry(lane, edge["id"], errors, warnings)
    
    def _validate_junctions(self, junctions: List[Dict], errors: List[str], warnings: List[str]) -> None:
        """Validate junctions.
        
        Args:
            junctions: List of junction dictionaries
            errors: List to collect errors
            warnings: List to collect warnings
        """
        for junction in junctions:
            # Validate junction attributes
            if not junction.get("id"):
                errors.append("Junction missing required 'id' attribute")
                continue
            
            if not junction.get("type"):
                errors.append(f"Junction '{junction['id']}' missing required 'type' attribute")
            elif junction["type"] not in [t.value for t in JunctionType]:
                errors.append(
                    f"Invalid junction type '{junction['type']}' in junction '{junction['id']}'. "
                    f"Must be one of: {', '.join(t.value for t in JunctionType)}"
                )
            
            # Validate coordinates
            if not isinstance(junction.get("x"), (int, float)) or not isinstance(junction.get("y"), (int, float)):
                errors.append(f"Junction '{junction['id']}' must have valid x,y coordinates")
            else:
                x, y = junction["x"], junction["y"]
                if not (-90 <= x <= 90) or not (-180 <= y <= 180):
                    errors.append(
                        f"Coordinates ({x}, {y}) out of valid range in junction '{junction['id']}'. "
                        "X must be between -90 and 90, Y must be between -180 and 180"
                    )
            
            # Validate elevation if present
            if junction.get("z") is not None:
                try:
                    z = float(junction["z"])
                    if z < self.MIN_ELEVATION or z > self.MAX_ELEVATION:
                        errors.append(
                            f"Invalid elevation value {z} meters in junction '{junction['id']}'. "
                            f"Elevation must be between {self.MIN_ELEVATION} and {self.MAX_ELEVATION} meters"
                        )
                except ValueError:
                    errors.append(
                        f"Invalid elevation value '{junction['z']}' in junction '{junction['id']}'. "
                        "Elevation must be a number"
                    )
            
            # Validate lane references
            for lane_id in junction.get("incLanes", []):
                if lane_id not in self.lane_ids:
                    errors.append(
                        f"Junction '{junction['id']}' references non-existent lane '{lane_id}' "
                        "in incLanes"
                    )
            
            for lane_id in junction.get("intLanes", []):
                if lane_id not in self.lane_ids:
                    errors.append(
                        f"Junction '{junction['id']}' references non-existent lane '{lane_id}' "
                        "in intLanes"
                    )
            
            # Validate junction shape if present
            if junction.get("shape"):
                self._validate_junction_shape(junction, errors, warnings)
    
    def _validate_connections(self, connections: List[Dict], errors: List[str], warnings: List[str]) -> None:
        """Validate connections.
        
        Args:
            connections: List of connection dictionaries
            errors: List to collect errors
            warnings: List to collect warnings
        """
        connection_set = set()
        
        for connection in connections:
            # Validate required attributes
            required_attrs = {"from", "to", "fromLane", "toLane", "dir", "state"}
            missing_attrs = required_attrs - set(connection.keys())
            if missing_attrs:
                errors.append(
                    f"Connection missing required attributes: {', '.join(missing_attrs)}"
                )
                continue
            
            # Validate edge references
            if connection["from"] not in self.edge_ids:
                errors.append(
                    f"Connection references non-existent edge '{connection['from']}'"
                )
            if connection["to"] not in self.edge_ids:
                errors.append(
                    f"Connection references non-existent edge '{connection['to']}'"
                )
            
            # Validate lane references
            from_lane = f"{connection['from']}_{connection['fromLane']}"
            to_lane = f"{connection['to']}_{connection['toLane']}"
            
            if from_lane not in self.lane_ids:
                errors.append(
                    f"Connection references non-existent lane '{from_lane}'"
                )
            if to_lane not in self.lane_ids:
                errors.append(
                    f"Connection references non-existent lane '{to_lane}'"
                )
            
            # Track connections
            if from_lane not in self.lane_connections:
                self.lane_connections[from_lane] = set()
            self.lane_connections[from_lane].add(to_lane)
            
            # Check for duplicate connections
            connection_key = (connection["from"], connection["to"], 
                            connection["fromLane"], connection["toLane"])
            if connection_key in connection_set:
                errors.append(
                    f"Duplicate connection: {connection['from']}->{connection['to']} "
                    f"({connection['fromLane']}->{connection['toLane']})"
                )
            connection_set.add(connection_key)
            
            # Validate direction
            if connection["dir"] not in [d.value for d in ConnectionDirection]:
                errors.append(
                    f"Invalid connection direction '{connection['dir']}'. "
                    f"Must be one of: {', '.join(d.value for d in ConnectionDirection)}"
                )
            
            # Validate state
            if connection["state"] not in [s.value for s in ConnectionState]:
                errors.append(
                    f"Invalid connection state '{connection['state']}'. "
                    f"Must be one of: {', '.join(s.value for s in ConnectionState)}"
                )
            
            # Validate via lane if present
            if connection.get("via") and connection["via"] not in self.lane_ids:
                errors.append(
                    f"Connection references non-existent via lane '{connection['via']}'"
                )
            
            # Validate connection visibility if present
            if connection.get("visibility") is not None:
                try:
                    visibility = float(connection["visibility"])
                    if visibility < 0:
                        errors.append(
                            f"Invalid visibility value {visibility} in connection "
                            f"{connection['from']}->{connection['to']}. "
                            "Visibility must be non-negative"
                        )
                except ValueError:
                    errors.append(
                        f"Invalid visibility value '{connection['visibility']}' in connection "
                        f"{connection['from']}->{connection['to']}. "
                        "Visibility must be a number"
                    )
    
    def _validate_connectivity(self, network_data: Dict, errors: List[str], warnings: List[str]) -> None:
        """Validate network connectivity.
        
        Args:
            network_data: Network data dictionary
            errors: List to collect errors
            warnings: List to collect warnings
        """
        # Check for isolated edges
        for edge in network_data["edges"]:
            edge_id = edge["id"]
            if edge_id not in self.edge_connections:
                errors.append(
                    f"Edge '{edge_id}' is isolated. "
                    "Each edge must be connected to at least one other edge."
                )
        
        # Check for disconnected junctions
        junction_connections = {junction["id"]: set() for junction in network_data["junctions"]}
        for connection in network_data["connections"]:
            from_edge = connection["from"]
            to_edge = connection["to"]
            junction_connections[network_data["edges"][from_edge]["from"]].add(to_edge)
            junction_connections[network_data["edges"][to_edge]["to"]].add(from_edge)
        
        for junction_id, connections in junction_connections.items():
            if not connections:
                errors.append(
                    f"Junction '{junction_id}' is disconnected. "
                    "Each junction must be connected to at least one edge."
                )
        
        # Check for isolated lanes
        for edge in network_data["edges"]:
            for lane in edge["lanes"]:
                lane_id = lane["id"]
                if lane_id not in self.lane_connections:
                    warnings.append(
                        f"Lane '{lane_id}' in edge '{edge['id']}' has no connections. "
                        "This may be intentional for dead-end lanes."
                    )
    
    def _validate_geometry(self, network_data: Dict, errors: List[str], warnings: List[str]) -> None:
        """Validate geometric consistency.
        
        Args:
            network_data: Network data dictionary
            errors: List to collect errors
            warnings: List to collect warnings
        """
        for edge in network_data["edges"]:
            for lane in edge["lanes"]:
                self._validate_lane_geometry(lane, edge["id"], errors, warnings)
    
    def _validate_lane_geometry(self, lane: Dict, edge_id: str, errors: List[str], warnings: List[str]) -> None:
        """Validate lane geometry.
        
        Args:
            lane: Lane dictionary
            edge_id: Parent edge ID
            errors: List to collect errors
            warnings: List to collect warnings
        """
        if not lane.get("shape"):
            return
        
        points = lane["shape"]
        
        # Check minimum number of points
        if len(points) < 2:
            errors.append(
                f"Lane '{lane.get('id')}' in edge '{edge_id}' "
                "must have at least two shape points"
            )
            return
        
        # Check point spacing
        for i in range(len(points) - 1):
            dist = self._calculate_distance(points[i], points[i + 1])
            if dist < self.MIN_POINT_SPACING:
                errors.append(
                    f"Points too close together in lane '{lane.get('id')}' of edge '{edge_id}'. "
                    f"Points {i} and {i+1} are only {dist:.2f} meters apart. "
                    f"Minimum spacing between points is {self.MIN_POINT_SPACING} meters."
                )
            elif dist > self.MAX_POINT_SPACING:
                warnings.append(
                    f"Points far apart in lane '{lane.get('id')}' of edge '{edge_id}'. "
                    f"Points {i} and {i+1} are {dist:.2f} meters apart. "
                    f"Maximum recommended spacing is {self.MAX_POINT_SPACING} meters."
                )
        
        # Check shape length matches lane length
        if lane.get("length"):
            shape_length = sum(self._calculate_distance(points[i], points[i + 1])
                             for i in range(len(points) - 1))
            if abs(shape_length - lane["length"]) > self.MIN_POINT_SPACING:
                errors.append(
                    f"Shape length does not match lane length in lane '{lane.get('id')}' of edge '{edge_id}'. "
                    f"Shape length: {shape_length:.2f}m, Lane length: {lane['length']:.2f}m. "
                    f"Difference exceeds tolerance of {self.MIN_POINT_SPACING} meters."
                )
        
        # Check for sharp angles
        for i in range(1, len(points) - 1):
            angle = self._calculate_angle(points[i-1], points[i], points[i+1])
            if angle < self.MIN_ANGLE or angle > self.MAX_ANGLE:
                errors.append(
                    f"Sharp angle detected in lane '{lane.get('id')}' of edge '{edge_id}'. "
                    f"Angle at point {i} is {angle:.1f} degrees. "
                    f"Angles must be between {self.MIN_ANGLE} and {self.MAX_ANGLE} degrees."
                )
    
    def _validate_junction_shape(self, junction: Dict, errors: List[str], warnings: List[str]) -> None:
        """Validate junction shape.
        
        Args:
            junction: Junction dictionary
            errors: List to collect errors
            warnings: List to collect warnings
        """
        points = junction["shape"]
        
        # Check minimum number of points
        if len(points) < 3:
            errors.append(
                f"Junction '{junction['id']}' shape must have at least 3 points. "
                f"Found {len(points)} points."
            )
            return
        
        # Check if shape is closed
        if points[0] != points[-1]:
            errors.append(
                f"Junction '{junction['id']}' shape must be closed. "
                "First and last points do not match."
            )
        
        # Check point spacing
        for i in range(len(points) - 1):
            dist = self._calculate_distance(points[i], points[i + 1])
            if dist < self.MIN_POINT_SPACING:
                errors.append(
                    f"Points too close together in junction '{junction['id']}' shape. "
                    f"Points {i} and {i+1} are only {dist:.2f} meters apart. "
                    f"Minimum spacing between points is {self.MIN_POINT_SPACING} meters."
                )
            elif dist > self.MAX_POINT_SPACING:
                warnings.append(
                    f"Points far apart in junction '{junction['id']}' shape. "
                    f"Points {i} and {i+1} are {dist:.2f} meters apart. "
                    f"Maximum recommended spacing is {self.MAX_POINT_SPACING} meters."
                )
        
        # Check for sharp angles
        for i in range(1, len(points) - 1):
            angle = self._calculate_angle(points[i-1], points[i], points[i+1])
            if angle < self.MIN_ANGLE or angle > self.MAX_ANGLE:
                errors.append(
                    f"Sharp angle detected in junction '{junction['id']}' shape. "
                    f"Angle at point {i} is {angle:.1f} degrees. "
                    f"Angles must be between {self.MIN_ANGLE} and {self.MAX_ANGLE} degrees."
                )
    
    def _validate_traffic_rules(self, network_data: Dict, errors: List[str], warnings: List[str]) -> None:
        """Validate traffic rules and regulations.
        
        Args:
            network_data: Network data dictionary
            errors: List to collect errors
            warnings: List to collect warnings
        """
        # Check for traffic light timing if junction type is traffic_light
        for junction in network_data["junctions"]:
            if junction["type"] == "traffic_light":
                if not junction.get("tl"):
                    errors.append(
                        f"Traffic light junction '{junction['id']}' missing traffic light ID"
                    )
                if not junction.get("tlOffset"):
                    warnings.append(
                        f"Traffic light junction '{junction['id']}' missing offset value"
                    )
                
                # Validate traffic light timing
                if junction.get("tl"):
                    tl_id = junction["tl"]
                    tl_connections = [c for c in network_data["connections"] 
                                   if c.get("tl") == tl_id]
                    if not tl_connections:
                        errors.append(
                            f"Traffic light '{tl_id}' in junction '{junction['id']}' "
                            "has no associated connections"
                        )
        
        # Check for speed consistency in connected lanes
        for connection in network_data["connections"]:
            from_lane = f"{connection['from']}_{connection['fromLane']}"
            to_lane = f"{connection['to']}_{connection['toLane']}"
            
            from_edge = next(edge for edge in network_data["edges"] if edge["id"] == connection["from"])
            to_edge = next(edge for edge in network_data["edges"] if edge["id"] == connection["to"])
            
            from_lane_data = next(lane for lane in from_edge["lanes"] if lane["id"] == from_lane)
            to_lane_data = next(lane for lane in to_edge["lanes"] if lane["id"] == to_lane)
            
            # Check speed consistency
            if from_lane_data.get("speed") and to_lane_data.get("speed"):
                from_speed = float(from_lane_data["speed"])
                to_speed = float(to_lane_data["speed"])
                speed_diff = abs(from_speed - to_speed)
                
                if speed_diff > 20:
                    warnings.append(
                        f"Large speed difference between connected lanes: "
                        f"{from_lane} ({from_speed} km/h) -> "
                        f"{to_lane} ({to_speed} km/h)"
                    )
                
                # Check for sudden speed changes
                if speed_diff > 0.5 * from_speed:
                    errors.append(
                        f"Sudden speed change between connected lanes: "
                        f"{from_lane} ({from_speed} km/h) -> "
                        f"{to_lane} ({to_speed} km/h). "
                        "Speed difference exceeds 50% of initial speed"
                    )
            
            # Check for valid connection states
            if connection["state"] == "M":  # Merging
                # Check if there are multiple incoming lanes
                incoming_lanes = [c for c in network_data["connections"] 
                                if c["to"] == connection["to"] and c["toLane"] == connection["toLane"]]
                if len(incoming_lanes) < 2:
                    errors.append(
                        f"Invalid merging connection state for connection "
                        f"{connection['from']}->{connection['to']}. "
                        "Merging state requires multiple incoming lanes"
                    )
            
            elif connection["state"] == "m":  # Diverging
                # Check if there are multiple outgoing lanes
                outgoing_lanes = [c for c in network_data["connections"] 
                                if c["from"] == connection["from"] and c["fromLane"] == connection["fromLane"]]
                if len(outgoing_lanes) < 2:
                    errors.append(
                        f"Invalid diverging connection state for connection "
                        f"{connection['from']}->{connection['to']}. "
                        "Diverging state requires multiple outgoing lanes"
                    )
    
    def _validate_topology(self, network_data: Dict, errors: List[str], warnings: List[str]) -> None:
        """Validate network topology.
        
        Args:
            network_data: Network data dictionary
            errors: List to collect errors
            warnings: List to collect warnings
        """
        # Check for dead-end roads
        dead_end_junctions = {junction["id"] for junction in network_data["junctions"] 
                            if junction["type"] == "dead_end"}
        
        for edge in network_data["edges"]:
            if edge["from"] in dead_end_junctions and edge["to"] in dead_end_junctions:
                errors.append(
                    f"Edge '{edge['id']}' connects two dead-end junctions. "
                    "This creates an isolated road segment."
                )
        
        # Check for parallel edges
        edge_pairs = set()
        for edge1 in network_data["edges"]:
            for edge2 in network_data["edges"]:
                if edge1["id"] < edge2["id"]:  # Avoid duplicate checks
                    if (edge1["from"] == edge2["from"] and edge1["to"] == edge2["to"]) or \
                       (edge1["from"] == edge2["to"] and edge1["to"] == edge2["from"]):
                        edge_pairs.add((edge1["id"], edge2["id"]))
                        
                        # Check if parallel edges have consistent attributes
                        if edge1.get("function") != edge2.get("function"):
                            warnings.append(
                                f"Parallel edges '{edge1['id']}' and '{edge2['id']}' "
                                "have different functions"
                            )
                        if edge1.get("priority") != edge2.get("priority"):
                            warnings.append(
                                f"Parallel edges '{edge1['id']}' and '{edge2['id']}' "
                                "have different priorities"
                            )
        
        for edge1_id, edge2_id in edge_pairs:
            warnings.append(
                f"Parallel edges detected: '{edge1_id}' and '{edge2_id}'. "
                "This may be intentional for bidirectional roads."
            )
        
        # Check for disconnected subgraphs
        visited = set()
        def dfs(node):
            visited.add(node)
            for edge in network_data["edges"]:
                if edge["from"] == node and edge["to"] not in visited:
                    dfs(edge["to"])
                elif edge["to"] == node and edge["from"] not in visited:
                    dfs(edge["from"])
        
        # Start DFS from first junction
        if network_data["junctions"]:
            dfs(network_data["junctions"][0]["id"])
            unvisited = set(j["id"] for j in network_data["junctions"]) - visited
            if unvisited:
                errors.append(
                    f"Network contains {len(unvisited)} disconnected subgraphs. "
                    f"Unreachable junctions: {', '.join(unvisited)}"
                )
        
        # Check for minimum distance between junctions
        junction_positions = {junction["id"]: (junction["x"], junction["y"]) 
                            for junction in network_data["junctions"]}
        
        for j1_id, pos1 in junction_positions.items():
            for j2_id, pos2 in junction_positions.items():
                if j1_id < j2_id:  # Avoid duplicate checks
                    dist = self._calculate_distance(pos1, pos2)
                    if dist < self.MIN_POINT_SPACING:
                        errors.append(
                            f"Junctions '{j1_id}' and '{j2_id}' are too close together. "
                            f"Distance: {dist:.2f} meters (minimum: {self.MIN_POINT_SPACING} meters)"
                        )
        
        # Check for minimum distance between edges
        edge_shapes = {}
        for edge in network_data["edges"]:
            shapes = []
            for lane in edge["lanes"]:
                if lane.get("shape"):
                    shapes.append(lane["shape"])
            if shapes:
                edge_shapes[edge["id"]] = shapes
        
        for e1_id, shapes1 in edge_shapes.items():
            for e2_id, shapes2 in edge_shapes.items():
                if e1_id < e2_id:  # Avoid duplicate checks
                    for shape1 in shapes1:
                        for shape2 in shapes2:
                            min_dist = float('inf')
                            for p1 in shape1:
                                for p2 in shape2:
                                    dist = self._calculate_distance(p1, p2)
                                    min_dist = min(min_dist, dist)
                            
                            if min_dist < self.MIN_POINT_SPACING:
                                errors.append(
                                    f"Edges '{e1_id}' and '{e2_id}' are too close together. "
                                    f"Minimum distance: {min_dist:.2f} meters "
                                    f"(minimum required: {self.MIN_POINT_SPACING} meters)"
                                )
    
    def _validate_road_characteristics(self, network_data: Dict, errors: List[str], warnings: List[str]) -> None:
        """Validate road characteristics like curvature and slope.
        
        Args:
            network_data: Network data dictionary
            errors: List to collect errors
            warnings: List to collect warnings
        """
        for edge in network_data["edges"]:
            for lane in edge["lanes"]:
                if not lane.get("shape"):
                    continue
                
                points = lane["shape"]
                if len(points) < 3:
                    continue
                
                # Calculate curvature
                curvatures = self._calculate_curvatures(points)
                max_curvature = max(curvatures)
                if max_curvature > self.MAX_CURVATURE:
                    errors.append(
                        f"Lane '{lane.get('id')}' in edge '{edge['id']}' has excessive curvature. "
                        f"Maximum curvature: {max_curvature:.3f} 1/m (limit: {self.MAX_CURVATURE} 1/m)"
                    )
                
                # Calculate slope
                if len(points) >= 2 and all(len(p) >= 3 for p in points):  # Check if z-coordinates exist
                    slopes = self._calculate_slopes(points)
                    max_slope = max(abs(s) for s in slopes)
                    if max_slope > self.MAX_SLOPE:
                        errors.append(
                            f"Lane '{lane.get('id')}' in edge '{edge['id']}' has excessive slope. "
                            f"Maximum slope: {max_slope:.1%} (limit: {self.MAX_SLOPE:.1%})"
                        )
    
    def _calculate_curvatures(self, points: List[Tuple[float, float]]) -> List[float]:
        """Calculate curvature at each point of a curve.
        
        Args:
            points: List of (x,y) coordinates
            
        Returns:
            List of curvature values
        """
        if len(points) < 3:
            return [0.0]
        
        curvatures = []
        for i in range(1, len(points) - 1):
            p1, p2, p3 = points[i-1], points[i], points[i+1]
            
            # Calculate vectors
            v1 = (p2[0] - p1[0], p2[1] - p1[1])
            v2 = (p3[0] - p2[0], p3[1] - p2[1])
            
            # Calculate angle between vectors
            dot_product = v1[0] * v2[0] + v1[1] * v2[1]
            v1_mag = math.sqrt(v1[0]**2 + v1[1]**2)
            v2_mag = math.sqrt(v2[0]**2 + v2[1]**2)
            
            if v1_mag == 0 or v2_mag == 0:
                curvatures.append(0.0)
                continue
            
            cos_angle = dot_product / (v1_mag * v2_mag)
            cos_angle = max(-1.0, min(1.0, cos_angle))
            angle = math.acos(cos_angle)
            
            # Calculate radius of curvature
            if angle == 0:
                curvatures.append(0.0)
            else:
                radius = (v1_mag + v2_mag) / (2 * math.sin(angle))
                curvature = 1 / radius if radius != 0 else float('inf')
                curvatures.append(curvature)
        
        return curvatures
    
    def _calculate_slopes(self, points: List[Tuple[float, float, float]]) -> List[float]:
        """Calculate slope between consecutive points.
        
        Args:
            points: List of (x,y,z) coordinates
            
        Returns:
            List of slope values
        """
        slopes = []
        for i in range(len(points) - 1):
            p1, p2 = points[i], points[i+1]
            dx = p2[0] - p1[0]
            dy = p2[1] - p1[1]
            dz = p2[2] - p1[2]
            
            horizontal_dist = math.sqrt(dx**2 + dy**2)
            if horizontal_dist == 0:
                slopes.append(0.0)
            else:
                slope = dz / horizontal_dist
                slopes.append(slope)
        
        return slopes
    
    def _calculate_statistics(self, network_data: Dict) -> None:
        """Calculate network statistics.
        
        Args:
            network_data: Network data dictionary
        """
        # Basic counts
        self.statistics["total_edges"] = len(network_data["edges"])
        self.statistics["total_junctions"] = len(network_data["junctions"])
        self.statistics["total_connections"] = len(network_data["connections"])
        
        # Lane statistics
        total_lanes = 0
        total_lane_length = 0.0
        total_lane_width = 0.0
        speed_distribution = defaultdict(int)
        
        for edge in network_data["edges"]:
            for lane in edge["lanes"]:
                total_lanes += 1
                if lane.get("length"):
                    total_lane_length += float(lane["length"])
                if lane.get("width"):
                    total_lane_width += float(lane["width"])
                if lane.get("speed"):
                    speed = round(float(lane["speed"]))
                    speed_distribution[speed] += 1
        
        self.statistics["total_lanes"] = total_lanes
        self.statistics["average_lane_length"] = total_lane_length / total_lanes if total_lanes > 0 else 0
        self.statistics["average_lane_width"] = total_lane_width / total_lanes if total_lanes > 0 else 0
        
        # Junction type distribution
        junction_types = defaultdict(int)
        for junction in network_data["junctions"]:
            junction_types[junction["type"]] += 1
        
        self.statistics["junction_type_distribution"] = dict(junction_types)
        
        # Connection type distribution
        connection_directions = defaultdict(int)
        connection_states = defaultdict(int)
        for connection in network_data["connections"]:
            connection_directions[connection["dir"]] += 1
            connection_states[connection["state"]] += 1
        
        self.statistics["connection_direction_distribution"] = dict(connection_directions)
        self.statistics["connection_state_distribution"] = dict(connection_states)
        
        # Speed distribution
        self.statistics["speed_distribution"] = dict(speed_distribution)
        
        # Network density
        if total_lane_length > 0:
            # Calculate bounding box
            x_coords = []
            y_coords = []
            for edge in network_data["edges"]:
                for lane in edge["lanes"]:
                    if lane.get("shape"):
                        for point in lane["shape"]:
                            x_coords.append(point[0])
                            y_coords.append(point[1])
            
            if x_coords and y_coords:
                area = (max(x_coords) - min(x_coords)) * (max(y_coords) - min(y_coords))
                self.statistics["network_density"] = total_lane_length / area if area > 0 else 0
    
    def _calculate_distance(self, point1: Tuple[float, float], point2: Tuple[float, float]) -> float:
        """Calculate Euclidean distance between two points.
        
        Args:
            point1: First point (x, y)
            point2: Second point (x, y)
            
        Returns:
            Distance between points
        """
        return math.sqrt((point2[0] - point1[0])**2 + (point2[1] - point1[1])**2)
    
    def _calculate_angle(self, p1: Tuple[float, float], p2: Tuple[float, float], 
                        p3: Tuple[float, float]) -> float:
        """Calculate angle between three points.
        
        Args:
            p1: First point
            p2: Middle point
            p3: Last point
            
        Returns:
            Angle in degrees
        """
        v1 = (p1[0] - p2[0], p1[1] - p2[1])
        v2 = (p3[0] - p2[0], p3[1] - p2[1])
        
        dot_product = v1[0] * v2[0] + v1[1] * v2[1]
        v1_mag = math.sqrt(v1[0]**2 + v1[1]**2)
        v2_mag = math.sqrt(v2[0]**2 + v2[1]**2)
        
        cos_angle = dot_product / (v1_mag * v2_mag)
        cos_angle = max(-1.0, min(1.0, cos_angle))  # Clamp to [-1, 1]
        
        return math.degrees(math.acos(cos_angle)) 