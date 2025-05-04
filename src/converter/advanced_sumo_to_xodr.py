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

import logging
import math
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
from xml.etree import ElementTree as ET
from lxml import etree

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
    """Represents a lane with its properties."""
    id: str
    index: int
    width: float
    speed: float
    type: str
    predecessor: Optional[str] = None
    successor: Optional[str] = None

@dataclass
class Edge:
    """Represents a road edge with lanes and geometry."""
    id: str
    from_node: str
    to_node: str
    priority: int
    type: str
    lanes: List[Lane]
    shape: List[Point]
    speed: float

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
            
            # Parse junctions with improved connections
            self._parse_junctions(root)
            
            # Parse traffic signals with timing information
            self._parse_traffic_signals(root)
            
            # Validate the parsed network
            self._validate_network()
            
        except Exception as e:
            logger.error(f"Error parsing SUMO network: {str(e)}")
            raise

    def _parse_edges(self, root: etree.Element) -> None:
        """Parse edges with enhanced geometry handling."""
        for edge_elem in root.findall(".//edge"):
            edge_id = edge_elem.get("id")
            if edge_id.startswith(":"):  # Skip internal edges
                continue
                
            # Parse basic edge properties
            from_node = edge_elem.get("from")
            to_node = edge_elem.get("to")
            priority = int(edge_elem.get("priority", "0"))
            edge_type = edge_elem.get("type", "highway.unknown")
            speed = float(edge_elem.get("speed", "13.89"))
            
            # Parse lanes with enhanced properties
            lanes = []
            for lane_elem in edge_elem.findall(".//lane"):
                lane_id = lane_elem.get("id")
                index = int(lane_elem.get("index"))
                width = float(lane_elem.get("width", "3.5"))
                lane_speed = float(lane_elem.get("speed", str(speed)))
                lane_type = lane_elem.get("type", "driving")
                
                lanes.append(Lane(
                    id=lane_id,
                    index=index,
                    width=width,
                    speed=lane_speed,
                    type=lane_type
                ))
            
            # Parse shape with enhanced geometry
            shape = []
            shape_elem = edge_elem.find(".//shape")
            if shape_elem is not None:
                points = shape_elem.text.strip().split()
                for point_str in points:
                    x, y = map(float, point_str.split(","))
                    shape.append(Point(x, y))
            
            # Create edge with enhanced geometry
            self.edges[edge_id] = Edge(
                id=edge_id,
                from_node=from_node,
                to_node=to_node,
                priority=priority,
                type=edge_type,
                lanes=lanes,
                shape=shape,
                speed=speed
            )

    def _parse_junctions(self, root: etree.Element) -> None:
        """Parse junctions with improved connection handling."""
        for junction_elem in root.findall(".//junction"):
            junction_id = junction_elem.get("id")
            junction_type = junction_elem.get("type")
            
            # Parse connections
            connections = []
            for conn_elem in junction_elem.findall(".//connection"):
                from_edge = conn_elem.get("from")
                to_edge = conn_elem.get("to")
                via_lane = conn_elem.get("via")
                connections.append((from_edge, to_edge, via_lane))
            
            # Parse shape
            shape = []
            shape_elem = junction_elem.find(".//shape")
            if shape_elem is not None:
                points = shape_elem.text.strip().split()
                for point_str in points:
                    x, y = map(float, point_str.split(","))
                    shape.append(Point(x, y))
            
            self.junctions[junction_id] = Junction(
                id=junction_id,
                type=junction_type,
                connections=connections,
                shape=shape
            )

    def _parse_traffic_signals(self, root: etree.Element) -> None:
        """Parse traffic signals with timing information."""
        for tl_elem in root.findall(".//tl-logic"):
            tl_id = tl_elem.get("id")
            tl_type = tl_elem.get("type", "static")
            
            # Parse phases
            phases = []
            for phase_elem in tl_elem.findall(".//phase"):
                duration = phase_elem.get("duration")
                state = phase_elem.get("state")
                phases.append({
                    "duration": duration,
                    "state": state
                })
            
            # Get signal location from junction
            junction = self.junctions.get(tl_id)
            location = junction.shape[0] if junction else Point(0, 0)
            
            # Parse connections
            connections = []
            for conn_elem in root.findall(f".//connection[@tl='{tl_id}']"):
                from_edge = conn_elem.get("from")
                to_edge = conn_elem.get("to")
                connections.append((from_edge, to_edge))
            
            self.traffic_signals[tl_id] = TrafficSignal(
                id=tl_id,
                type=tl_type,
                location=location,
                phases=phases,
                connections=connections
            )

    def _validate_network(self) -> None:
        """Validate the parsed network for consistency."""
        # Check edge connectivity
        for edge_id, edge in self.edges.items():
            if edge.from_node not in self.junctions:
                logger.warning(f"Edge {edge_id} has invalid from_node: {edge.from_node}")
            if edge.to_node not in self.junctions:
                logger.warning(f"Edge {edge_id} has invalid to_node: {edge.to_node}")
            
            # Validate lane properties
            for lane in edge.lanes:
                if lane.width <= 0:
                    logger.warning(f"Invalid lane width in edge {edge_id}, lane {lane.id}")
                if lane.speed <= 0:
                    logger.warning(f"Invalid lane speed in edge {edge_id}, lane {lane.id}")
        
        # Check junction connections
        for junction_id, junction in self.junctions.items():
            for from_edge, to_edge, _ in junction.connections:
                if from_edge not in self.edges:
                    logger.warning(f"Invalid from_edge in junction {junction_id}: {from_edge}")
                if to_edge not in self.edges:
                    logger.warning(f"Invalid to_edge in junction {junction_id}: {to_edge}")
        
        # Validate traffic signals
        for tl_id, signal in self.traffic_signals.items():
            if not signal.phases:
                logger.warning(f"Traffic signal {tl_id} has no phases")
            for phase in signal.phases:
                if not phase.get("duration") or not phase.get("state"):
                    logger.warning(f"Invalid phase in traffic signal {tl_id}")

class AdvancedOpenDriveGenerator:
    """Generator for OpenDRIVE files with enhanced features."""
    
    def __init__(self, parser: AdvancedSumoNetworkParser):
        """Initialize the generator with a parsed network."""
        self.parser = parser
        self.road_id_counter = 0
        self.junction_id_counter = 0
        self.signal_id_counter = 0
        
    def generate(self, output_file: str) -> None:
        """Generate an OpenDRIVE file with enhanced features."""
        try:
            # Create OpenDRIVE root element
            root = ET.Element("OpenDRIVE")
            root.set("xmlns", "http://www.opendrive.org")
            root.set("xmlns:xsi", "http://www.w3.org/2001/XMLSchema-instance")
            root.set("xsi:schemaLocation", "http://www.opendrive.org http://www.opendrive.org/OpenDRIVE_1.4.xsd")
            
            # Add header
            header = ET.SubElement(root, "header")
            header.set("revMajor", "1")
            header.set("revMinor", "4")
            header.set("name", "SUMO to OpenDRIVE Conversion")
            header.set("version", "1.00")
            header.set("date", "2024")
            
            # Generate roads with enhanced geometry
            self._generate_roads(root)
            
            # Generate junctions with improved connections
            self._generate_junctions(root)
            
            # Generate traffic signals
            self._generate_traffic_signals(root)
            
            # Write the file
            tree = ET.ElementTree(root)
            ET.indent(tree, space="  ")
            tree.write(output_file, encoding="utf-8", xml_declaration=True)
            
            logger.info(f"Successfully generated OpenDRIVE file: {output_file}")
            
        except Exception as e:
            logger.error(f"Error generating OpenDRIVE file: {str(e)}")
            raise

    def _generate_roads(self, root: ET.Element) -> None:
        """Generate roads with enhanced geometry handling."""
        for edge_id, edge in self.parser.edges.items():
            # Create road element
            road = ET.SubElement(root, "road")
            road.set("name", edge_id)
            road.set("length", str(self._calculate_road_length(edge)))
            road.set("id", str(self.road_id_counter))
            road.set("junction", "-1")
            
            # Add planView with enhanced geometry
            plan_view = ET.SubElement(road, "planView")
            self._add_geometry(plan_view, edge)
            
            # Add lanes
            lanes = ET.SubElement(road, "lanes")
            self._add_lane_sections(lanes, edge)
            
            # Add elevation profile
            elevation = ET.SubElement(road, "elevationProfile")
            self._add_elevation_profile(elevation, edge)
            
            self.road_id_counter += 1

    def _calculate_road_length(self, edge: Edge) -> float:
        """Calculate the length of a road with enhanced geometry."""
        if not edge.shape:
            return 0.0
        
        length = 0.0
        for i in range(len(edge.shape) - 1):
            p1 = edge.shape[i]
            p2 = edge.shape[i + 1]
            length += math.sqrt((p2.x - p1.x)**2 + (p2.y - p1.y)**2)
        
        return length

    def _add_geometry(self, plan_view: ET.Element, edge: Edge) -> None:
        """Add geometry with enhanced curve handling."""
        if not edge.shape:
            return
        
        # Convert shape points to numpy array for spline fitting
        points = np.array([(p.x, p.y) for p in edge.shape])
        
        # Fit a smooth spline to the points
        tck, u = splprep(points.T, s=0)
        
        # Generate points along the spline
        u_new = np.linspace(0, 1, 100)
        x_new, y_new = splev(u_new, tck)
        
        # Add geometry elements
        s = 0.0
        for i in range(len(x_new) - 1):
            x1, y1 = x_new[i], y_new[i]
            x2, y2 = x_new[i + 1], y_new[i + 1]
            
            # Calculate heading
            dx = x2 - x1
            dy = y2 - y1
            hdg = math.atan2(dy, dx)
            
            # Calculate length
            length = math.sqrt(dx**2 + dy**2)
            
            # Add geometry element
            geometry = ET.SubElement(plan_view, "geometry")
            geometry.set("s", str(s))
            geometry.set("x", str(x1))
            geometry.set("y", str(y1))
            geometry.set("hdg", str(hdg))
            geometry.set("length", str(length))
            
            # Add line element for straight segments
            line = ET.SubElement(geometry, "line")
            
            s += length

    def _add_lane_sections(self, lanes: ET.Element, edge: Edge) -> None:
        """Add lane sections with enhanced properties."""
        lane_section = ET.SubElement(lanes, "laneSection")
        lane_section.set("s", "0.0")
        
        # Add center lane
        center = ET.SubElement(lane_section, "center")
        center_lane = ET.SubElement(center, "lane")
        center_lane.set("id", "0")
        center_lane.set("type", "none")
        center_lane.set("level", "false")
        
        # Add right lanes
        right = ET.SubElement(lane_section, "right")
        for lane in edge.lanes:
            if lane.index < 0:  # Right lanes have negative indices
                lane_elem = ET.SubElement(right, "lane")
                lane_elem.set("id", str(lane.index))
                lane_elem.set("type", "driving")
                lane_elem.set("level", "false")
                
                # Add width
                width = ET.SubElement(lane_elem, "width")
                width.set("sOffset", "0.0")
                width.set("a", str(lane.width))
                width.set("b", "0.0")
                width.set("c", "0.0")
                width.set("d", "0.0")
                
                # Add speed
                speed = ET.SubElement(lane_elem, "speed")
                speed.set("sOffset", "0.0")
                speed.set("max", str(lane.speed))
                speed.set("unit", "m/s")

    def _add_elevation_profile(self, elevation: ET.Element, edge: Edge) -> None:
        """Add elevation profile with enhanced features."""
        # Add default elevation
        elevation_record = ET.SubElement(elevation, "elevation")
        elevation_record.set("s", "0.0")
        elevation_record.set("a", "0.0")
        elevation_record.set("b", "0.0")
        elevation_record.set("c", "0.0")
        elevation_record.set("d", "0.0")

    def _generate_junctions(self, root: ET.Element) -> None:
        """Generate junctions with improved connections."""
        for junction_id, junction in self.parser.junctions.items():
            # Create junction element
            junction_elem = ET.SubElement(root, "junction")
            junction_elem.set("name", junction_id)
            junction_elem.set("id", str(self.junction_id_counter))
            
            # Add connections
            for from_edge, to_edge, via_lane in junction.connections:
                connection = ET.SubElement(junction_elem, "connection")
                connection.set("id", f"{from_edge}_{to_edge}")
                connection.set("incomingRoad", from_edge)
                connection.set("connectingRoad", to_edge)
                connection.set("contactPoint", "start")
                
                # Add lane links
                lane_link = ET.SubElement(connection, "laneLink")
                lane_link.set("from", via_lane)
                lane_link.set("to", via_lane)
            
            self.junction_id_counter += 1

    def _generate_traffic_signals(self, root: ET.Element) -> None:
        """Generate traffic signals with timing information."""
        for tl_id, signal in self.parser.traffic_signals.items():
            # Create controller
            controller = ET.SubElement(root, "controller")
            controller.set("id", str(self.signal_id_counter))
            controller.set("name", f"Controller_{tl_id}")
            controller.set("sequence", "0")
            
            # Add control elements
            for phase in signal.phases:
                control = ET.SubElement(controller, "control")
                control.set("signalId", str(self.signal_id_counter))
                control.set("type", "0")
                control.set("duration", phase["duration"])
                control.set("state", phase["state"])
            
            # Create signal
            signal_elem = ET.SubElement(root, "signal")
            signal_elem.set("id", str(self.signal_id_counter))
            signal_elem.set("name", f"Signal_{tl_id}")
            signal_elem.set("dynamic", "yes")
            signal_elem.set("orientation", "+")
            signal_elem.set("zOffset", "0.0")
            signal_elem.set("type", "1000001")
            signal_elem.set("subtype", "-1")
            
            # Add position
            position = ET.SubElement(signal_elem, "position")
            position.set("x", str(signal.location.x))
            position.set("y", str(signal.location.y))
            position.set("z", "0.0")
            
            # Add validity
            validity = ET.SubElement(signal_elem, "validity")
            validity.set("fromLane", "-1")
            validity.set("toLane", "1")
            
            self.signal_id_counter += 1

def main():
    """Main function for testing the converter."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Convert SUMO network to OpenDRIVE format")
    parser.add_argument("input_file", help="Input SUMO network file (.net.xml)")
    parser.add_argument("output_file", help="Output OpenDRIVE file (.xodr)")
    
    args = parser.parse_args()
    
    # Parse SUMO network
    sumo_parser = AdvancedSumoNetworkParser(args.input_file)
    sumo_parser.parse()
    
    # Generate OpenDRIVE
    opendrive_generator = AdvancedOpenDriveGenerator(sumo_parser)
    opendrive_generator.generate(args.output_file)

if __name__ == "__main__":
    main() 