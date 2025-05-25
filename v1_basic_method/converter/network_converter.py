"""Network converter for handling road network conversions with error checking."""

from lxml import etree
from typing import List, Dict, Set, Optional, Tuple
import math
from src.validation.network_validator import NetworkValidator

class NetworkConverter:
    """Converts road network XML to internal representation with error checking."""
    
    # Valid junction types
    VALID_JUNCTION_TYPES = {"priority", "traffic_light", "dead_end", "unregulated"}
    
    # Valid connection directions
    VALID_CONNECTION_DIRECTIONS = {"s", "t", "l", "r", "L", "R"}  # straight, turn, left, right
    
    # Valid connection states
    VALID_CONNECTION_STATES = {"M", "m", "=", "-", "0"}  # Merging, diverging, equal, minor, zero
    
    # Maximum allowed values
    MAX_SPEED = 200.0  # km/h
    MAX_LENGTH = 10000.0  # meters
    MAX_LANES = 10
    MIN_LANE_WIDTH = 2.5  # meters
    MAX_LANE_WIDTH = 5.0  # meters
    
    def __init__(self):
        """Initialize the network converter."""
        self.validator = NetworkValidator()
        self.lane_ids: Set[str] = set()
        self.edge_ids: Set[str] = set()
        self.junction_ids: Set[str] = set()
        self.edge_connections: Dict[str, Set[str]] = {}  # Track edge connections
    
    def convert_network(self, root: etree.Element) -> Dict:
        """Convert network XML to internal representation with error checking.
        
        Args:
            root: Root element of the network XML
            
        Returns:
            Dict containing the converted network data
            
        Raises:
            ValueError: If the network XML is invalid or contains errors
        """
        # Reset tracking sets
        self.lane_ids.clear()
        self.edge_ids.clear()
        self.junction_ids.clear()
        self.edge_connections.clear()
        
        # Validate basic XML structure
        self._validate_xml_structure(root)
        
        # Convert and validate edges
        edges = self._convert_edges(root.find("edges"))
        
        # Convert and validate junctions
        junctions = self._convert_junctions(root.find("junctions"))
        
        # Convert and validate connections
        connections = self._convert_connections(root.find("connections"))
        
        # Validate network consistency
        self._validate_network_consistency(edges, junctions, connections)
        
        return {
            "edges": edges,
            "junctions": junctions,
            "connections": connections
        }
    
    def _validate_xml_structure(self, root: etree.Element) -> None:
        """Validate basic XML structure.
        
        Args:
            root: Root element of the network XML
            
        Raises:
            ValueError: If required elements are missing
        """
        if root.tag != "net":
            raise ValueError(
                f"Invalid root element: '{root.tag}'. Expected 'net'. "
                "Please ensure the XML file has the correct root element."
            )
        
        required_elements = {"edges", "junctions", "connections"}
        missing_elements = {element for element in required_elements 
                          if root.find(element) is None}
        if missing_elements:
            raise ValueError(
                f"Missing required elements: {', '.join(missing_elements)}. "
                "The network XML must contain all of these elements: edges, junctions, and connections."
            )
        
        # Validate XML version and encoding
        version = root.get("version")
        if version != "1.0":
            raise ValueError(
                f"Unsupported XML version: '{version}'. Expected '1.0'. "
                "Please update the XML version attribute to '1.0'."
            )
    
    def _validate_network_consistency(self, edges: List[Dict], junctions: List[Dict], connections: List[Dict]) -> None:
        """Validate overall network consistency.
        
        Args:
            edges: List of edge dictionaries
            junctions: List of junction dictionaries
            connections: List of connection dictionaries
            
        Raises:
            ValueError: If network is inconsistent
        """
        # Check for isolated edges
        isolated_edges = [edge["id"] for edge in edges 
                        if edge["id"] not in self.edge_connections]
        if isolated_edges:
            raise ValueError(
                f"Found {len(isolated_edges)} isolated edges: {', '.join(isolated_edges)}. "
                "Each edge must be connected to at least one other edge through a junction. "
                "Please add appropriate connections for these edges."
            )
        
        # Check for disconnected junctions
        junction_connections = {junction["id"]: set() for junction in junctions}
        for connection in connections:
            from_edge = connection["from"]
            to_edge = connection["to"]
            junction_connections[edges[from_edge]["from"]].add(to_edge)
            junction_connections[edges[to_edge]["to"]].add(from_edge)
        
        disconnected_junctions = [junction_id for junction_id, connections 
                                in junction_connections.items() 
                                if not connections]
        if disconnected_junctions:
            raise ValueError(
                f"Found {len(disconnected_junctions)} disconnected junctions: {', '.join(disconnected_junctions)}. "
                "Each junction must be connected to at least one edge. "
                "Please add appropriate connections for these junctions."
            )
    
    def _convert_edges(self, edges_elem: etree.Element) -> List[Dict]:
        """Convert edges with validation.
        
        Args:
            edges_elem: Edges element from XML
            
        Returns:
            List of converted edge dictionaries
            
        Raises:
            ValueError: If edge data is invalid
        """
        if edges_elem is None:
            return []
        
        edges = []
        for edge in edges_elem.findall("edge"):
            edge_id = edge.get("id")
            if not edge_id:
                raise ValueError(
                    "Edge missing required 'id' attribute. "
                    "Each edge must have a unique identifier."
                )
            if edge_id in self.edge_ids:
                raise ValueError(
                    f"Duplicate edge ID: '{edge_id}'. "
                    "Each edge must have a unique identifier. "
                    f"Previous edge with this ID was found at line {edge.sourceline}."
                )
            self.edge_ids.add(edge_id)
            
            # Validate edge attributes
            priority = edge.get("priority")
            if priority is not None:
                try:
                    priority = int(priority)
                    if priority < -1 or priority > 78:
                        raise ValueError(
                            f"Invalid priority value: {priority}. "
                            "Priority must be between -1 and 78. "
                            f"Found in edge '{edge_id}'."
                        )
                except ValueError:
                    raise ValueError(
                        f"Invalid priority value: '{priority}'. "
                        "Priority must be an integer between -1 and 78. "
                        f"Found in edge '{edge_id}'."
                    )
            
            # Validate edge function
            function = edge.get("function")
            if function and function not in {"normal", "internal", "connector"}:
                raise ValueError(
                    f"Invalid edge function: '{function}'. "
                    "Function must be one of: 'normal', 'internal', 'connector'. "
                    f"Found in edge '{edge_id}'."
                )
            
            lanes = self._convert_lanes(edge)
            edges.append({
                "id": edge_id,
                "from": edge.get("from"),
                "to": edge.get("to"),
                "priority": priority,
                "function": function,
                "lanes": lanes
            })
        
        return edges
    
    def _convert_lanes(self, edge: etree.Element) -> List[Dict]:
        """Convert lanes with validation.
        
        Args:
            edge: Edge element containing lanes
            
        Returns:
            List of converted lane dictionaries
            
        Raises:
            ValueError: If lane data is invalid
        """
        lanes_elem = edge.find("lanes")
        if lanes_elem is None:
            raise ValueError(
                f"Edge '{edge.get('id')}' missing 'lanes' element. "
                "Each edge must contain at least one lane."
            )
        
        lanes = []
        indices = set()
        
        for lane in lanes_elem.findall("lane"):
            # Validate required attributes
            required_attrs = {"id", "index", "speed", "length"}
            missing_attrs = required_attrs - set(lane.attrib.keys())
            if missing_attrs:
                raise ValueError(
                    f"Lane missing required attributes: {', '.join(missing_attrs)}. "
                    f"Found in edge '{edge.get('id')}'. "
                    "Each lane must have: id, index, speed, and length attributes."
                )
            
            # Validate lane ID
            lane_id = lane.get("id")
            if lane_id in self.lane_ids:
                raise ValueError(
                    f"Duplicate lane ID: '{lane_id}'. "
                    "Each lane must have a unique identifier. "
                    f"Previous lane with this ID was found at line {lane.sourceline}."
                )
            self.lane_ids.add(lane_id)
            
            # Validate lane index
            try:
                index = int(lane.get("index"))
                if index < 0 or index >= self.MAX_LANES:
                    raise ValueError(
                        f"Lane index out of range: {index}. "
                        f"Index must be between 0 and {self.MAX_LANES-1}. "
                        f"Found in lane '{lane_id}' of edge '{edge.get('id')}'."
                    )
            except ValueError:
                raise ValueError(
                    f"Invalid lane index: '{lane.get('index')}'. "
                    "Index must be a non-negative integer. "
                    f"Found in lane '{lane_id}' of edge '{edge.get('id')}'."
                )
            
            # Check for non-sequential indices
            if indices and max(indices) + 1 != index:
                raise ValueError(
                    f"Non-sequential lane indices in edge '{edge.get('id')}'. "
                    f"Expected index {max(indices) + 1}, found {index}. "
                    "Lane indices must be sequential starting from 0."
                )
            indices.add(index)
            
            # Validate speed
            try:
                speed = float(lane.get("speed"))
                if speed <= 0 or speed > self.MAX_SPEED:
                    raise ValueError(
                        f"Invalid speed value: {speed} km/h. "
                        f"Speed must be between 0 and {self.MAX_SPEED} km/h. "
                        f"Found in lane '{lane_id}' of edge '{edge.get('id')}'."
                    )
            except ValueError:
                raise ValueError(
                    f"Invalid speed value: '{lane.get('speed')}'. "
                    "Speed must be a positive number. "
                    f"Found in lane '{lane_id}' of edge '{edge.get('id')}'."
                )
            
            # Validate length
            try:
                length = float(lane.get("length"))
                if length <= 0 or length > self.MAX_LENGTH:
                    raise ValueError(
                        f"Invalid length value: {length} meters. "
                        f"Length must be between 0 and {self.MAX_LENGTH} meters. "
                        f"Found in lane '{lane_id}' of edge '{edge.get('id')}'."
                    )
            except ValueError:
                raise ValueError(
                    f"Invalid length value: '{lane.get('length')}'. "
                    "Length must be a positive number. "
                    f"Found in lane '{lane_id}' of edge '{edge.get('id')}'."
                )
            
            # Validate width if present
            width = lane.get("width")
            if width is not None:
                try:
                    width = float(width)
                    if width < self.MIN_LANE_WIDTH or width > self.MAX_LANE_WIDTH:
                        raise ValueError(
                            f"Invalid lane width: {width} meters. "
                            f"Width must be between {self.MIN_LANE_WIDTH} and {self.MAX_LANE_WIDTH} meters. "
                            f"Found in lane '{lane_id}' of edge '{edge.get('id')}'."
                        )
                except ValueError:
                    raise ValueError(
                        f"Invalid lane width: '{width}'. "
                        "Width must be a positive number. "
                        f"Found in lane '{lane_id}' of edge '{edge.get('id')}'."
                    )
            
            # Validate geometry
            shape = lane.find("shape")
            if shape is None or not shape.text:
                raise ValueError(
                    f"Lane '{lane_id}' missing shape. "
                    "Each lane must have a shape element with at least two points."
                )
            
            # Parse and validate shape points
            try:
                points = [tuple(map(float, point.split(","))) for point in shape.text.split()]
                if len(points) < 2:
                    raise ValueError(
                        f"Invalid lane geometry in lane '{lane_id}'. "
                        "At least two points are required to define a lane shape."
                    )
                
                # Validate point spacing
                for i in range(len(points) - 1):
                    dist = self._calculate_distance(points[i], points[i + 1])
                    if dist < 0.1:  # Minimum 0.1m between points
                        raise ValueError(
                            f"Points too close together in lane '{lane_id}'. "
                            f"Points {i} and {i+1} are only {dist:.2f} meters apart. "
                            "Minimum spacing between points is 0.1 meters."
                        )
                
                # Validate shape length matches lane length
                shape_length = sum(self._calculate_distance(points[i], points[i + 1])
                                 for i in range(len(points) - 1))
                if abs(shape_length - length) > 0.1:  # Allow 0.1m tolerance
                    raise ValueError(
                        f"Shape length does not match lane length in lane '{lane_id}'. "
                        f"Shape length: {shape_length:.2f}m, Lane length: {length:.2f}m. "
                        "Difference exceeds tolerance of 0.1 meters."
                    )
                
            except ValueError as e:
                raise ValueError(
                    f"Invalid coordinate values in lane '{lane_id}': {str(e)}. "
                    "Coordinates must be valid numbers in the format 'x,y'."
                )
            
            lanes.append({
                "id": lane_id,
                "index": index,
                "speed": speed,
                "length": length,
                "width": width,
                "shape": points
            })
        
        return lanes
    
    def _convert_junctions(self, junctions_elem: etree.Element) -> List[Dict]:
        """Convert junctions with validation.
        
        Args:
            junctions_elem: Junctions element from XML
            
        Returns:
            List of converted junction dictionaries
            
        Raises:
            ValueError: If junction data is invalid
        """
        if junctions_elem is None:
            return []
        
        junctions = []
        for junction in junctions_elem.findall("junction"):
            # Validate required attributes
            required_attrs = {"id", "type", "x", "y"}
            missing_attrs = required_attrs - set(junction.attrib.keys())
            if missing_attrs:
                raise ValueError(
                    f"Junction missing required attributes: {', '.join(missing_attrs)}. "
                    "Each junction must have: id, type, x, and y attributes."
                )
            
            # Validate junction ID
            junction_id = junction.get("id")
            if junction_id in self.junction_ids:
                raise ValueError(
                    f"Duplicate junction ID: '{junction_id}'. "
                    "Each junction must have a unique identifier. "
                    f"Previous junction with this ID was found at line {junction.sourceline}."
                )
            self.junction_ids.add(junction_id)
            
            # Validate junction type
            junction_type = junction.get("type")
            if junction_type not in self.VALID_JUNCTION_TYPES:
                raise ValueError(
                    f"Invalid junction type: '{junction_type}'. "
                    f"Type must be one of: {', '.join(self.VALID_JUNCTION_TYPES)}. "
                    f"Found in junction '{junction_id}'."
                )
            
            # Validate coordinates
            try:
                x = float(junction.get("x"))
                y = float(junction.get("y"))
                if not (-90 <= x <= 90) or not (-180 <= y <= 180):
                    raise ValueError(
                        f"Coordinates out of valid range: ({x}, {y}). "
                        "X must be between -90 and 90, Y must be between -180 and 180. "
                        f"Found in junction '{junction_id}'."
                    )
            except ValueError:
                raise ValueError(
                    f"Invalid coordinate values in junction '{junction_id}'. "
                    "Coordinates must be valid numbers."
                )
            
            # Validate lane references
            inc_lanes = junction.get("incLanes", "").split()
            int_lanes = junction.get("intLanes", "").split()
            
            # Check for duplicate lane references
            if len(set(inc_lanes)) != len(inc_lanes):
                raise ValueError(
                    f"Duplicate incoming lanes in junction '{junction_id}'. "
                    "Each lane can only be referenced once in incLanes."
                )
            if len(set(int_lanes)) != len(int_lanes):
                raise ValueError(
                    f"Duplicate internal lanes in junction '{junction_id}'. "
                    "Each lane can only be referenced once in intLanes."
                )
            
            for lane_id in inc_lanes + int_lanes:
                if lane_id and lane_id not in self.lane_ids:
                    raise ValueError(
                        f"Invalid junction connection: lane '{lane_id}' does not exist. "
                        f"Found in junction '{junction_id}'. "
                        "All referenced lanes must exist in the network."
                    )
            
            # Validate junction shape if present
            shape = junction.find("shape")
            if shape is not None and shape.text:
                try:
                    points = [tuple(map(float, point.split(","))) for point in shape.text.split()]
                    if len(points) < 3:
                        raise ValueError(
                            f"Junction shape must have at least 3 points. "
                            f"Found {len(points)} points in junction '{junction_id}'."
                        )
                    
                    # Validate shape is closed
                    if points[0] != points[-1]:
                        raise ValueError(
                            f"Junction shape must be closed. "
                            f"First and last points do not match in junction '{junction_id}'."
                        )
                    
                    # Validate point spacing
                    for i in range(len(points) - 1):
                        dist = self._calculate_distance(points[i], points[i + 1])
                        if dist < 0.1:  # Minimum 0.1m between points
                            raise ValueError(
                                f"Points too close together in junction shape. "
                                f"Points {i} and {i+1} are only {dist:.2f} meters apart. "
                                f"Found in junction '{junction_id}'. "
                                "Minimum spacing between points is 0.1 meters."
                            )
                    
                except ValueError as e:
                    raise ValueError(
                        f"Invalid junction shape in junction '{junction_id}': {str(e)}. "
                        "Coordinates must be valid numbers in the format 'x,y'."
                    )
            
            junctions.append({
                "id": junction_id,
                "type": junction_type,
                "x": x,
                "y": y,
                "incLanes": inc_lanes,
                "intLanes": int_lanes,
                "shape": points if shape is not None and shape.text else None
            })
        
        return junctions
    
    def _convert_connections(self, connections_elem: etree.Element) -> List[Dict]:
        """Convert connections with validation.
        
        Args:
            connections_elem: Connections element from XML
            
        Returns:
            List of converted connection dictionaries
            
        Raises:
            ValueError: If connection data is invalid
        """
        if connections_elem is None:
            return []
        
        connections = []
        connection_set = set()  # Track unique connections
        
        for connection in connections_elem.findall("connection"):
            # Validate required attributes
            required_attrs = {"from", "to", "fromLane", "toLane", "dir", "state"}
            missing_attrs = required_attrs - set(connection.attrib.keys())
            if missing_attrs:
                raise ValueError(
                    f"Connection missing required attributes: {', '.join(missing_attrs)}. "
                    "Each connection must have: from, to, fromLane, toLane, dir, and state attributes."
                )
            
            # Validate edge references
            from_edge = connection.get("from")
            to_edge = connection.get("to")
            if from_edge not in self.edge_ids:
                raise ValueError(
                    f"Invalid connection: edge '{from_edge}' does not exist. "
                    "All referenced edges must exist in the network."
                )
            if to_edge not in self.edge_ids:
                raise ValueError(
                    f"Invalid connection: edge '{to_edge}' does not exist. "
                    "All referenced edges must exist in the network."
                )
            
            # Track edge connections
            if from_edge not in self.edge_connections:
                self.edge_connections[from_edge] = set()
            self.edge_connections[from_edge].add(to_edge)
            
            # Validate lane references
            from_lane = f"{from_edge}_{connection.get('fromLane')}"
            to_lane = f"{to_edge}_{connection.get('toLane')}"
            if from_lane not in self.lane_ids:
                raise ValueError(
                    f"Invalid connection: lane '{from_lane}' does not exist. "
                    "All referenced lanes must exist in the network."
                )
            if to_lane not in self.lane_ids:
                raise ValueError(
                    f"Invalid connection: lane '{to_lane}' does not exist. "
                    "All referenced lanes must exist in the network."
                )
            
            # Check for duplicate connections
            connection_key = (from_edge, to_edge, connection.get("fromLane"), connection.get("toLane"))
            if connection_key in connection_set:
                raise ValueError(
                    f"Duplicate connection: {from_edge}->{to_edge} ({connection.get('fromLane')}->{connection.get('toLane')}). "
                    "Each lane-to-lane connection can only be defined once."
                )
            connection_set.add(connection_key)
            
            # Validate direction
            direction = connection.get("dir")
            if direction not in self.VALID_CONNECTION_DIRECTIONS:
                raise ValueError(
                    f"Invalid connection direction: '{direction}'. "
                    f"Direction must be one of: {', '.join(self.VALID_CONNECTION_DIRECTIONS)}. "
                    f"Found in connection {from_edge}->{to_edge}."
                )
            
            # Validate state
            state = connection.get("state")
            if state not in self.VALID_CONNECTION_STATES:
                raise ValueError(
                    f"Invalid connection state: '{state}'. "
                    f"State must be one of: {', '.join(self.VALID_CONNECTION_STATES)}. "
                    f"Found in connection {from_edge}->{to_edge}."
                )
            
            # Validate via lane if present
            via = connection.get("via")
            if via is not None and via not in self.lane_ids:
                raise ValueError(
                    f"Invalid via lane: '{via}'. "
                    "All referenced lanes must exist in the network. "
                    f"Found in connection {from_edge}->{to_edge}."
                )
            
            connections.append({
                "from": from_edge,
                "to": to_edge,
                "fromLane": int(connection.get("fromLane")),
                "toLane": int(connection.get("toLane")),
                "dir": direction,
                "state": state,
                "via": via
            })
        
        return connections
    
    def _calculate_distance(self, point1: Tuple[float, float], point2: Tuple[float, float]) -> float:
        """Calculate Euclidean distance between two points.
        
        Args:
            point1: First point (x, y)
            point2: Second point (x, y)
            
        Returns:
            Distance between points
        """
        return math.sqrt((point2[0] - point1[0])**2 + (point2[1] - point1[1])**2) 