#!/usr/bin/env python3
"""
Custom SUMO (.net.xml) to OpenDRIVE (.xodr) converter.
This script provides direct conversion without relying on netconvert.
"""

import os
import math
import logging
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
import xml.etree.ElementTree as ET
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class Point:
    """Represents a 2D point with optional elevation."""
    x: float
    y: float
    z: Optional[float] = None

    def distance_to(self, other: 'Point') -> float:
        """Calculate Euclidean distance to another point."""
        return math.sqrt((self.x - other.x)**2 + (self.y - other.y)**2)

@dataclass
class Lane:
    """Represents a lane with its properties."""
    id: str
    index: int
    speed: float
    width: float
    shape: List[Point]
    length: float

@dataclass
class Edge:
    """Represents a road edge with its lanes."""
    id: str
    from_node: str
    to_node: str
    priority: int
    type: str
    lanes: List[Lane]

@dataclass
class Junction:
    """Represents a junction with its properties."""
    id: str
    type: str
    x: float
    y: float
    inc_lanes: List[str]
    int_lanes: List[str]
    requests: List[dict]

class SumoNetworkParser:
    """Parser for SUMO .net.xml files."""
    
    def __init__(self, net_file: str):
        """Initialize the parser with a SUMO network file."""
        self.net_file = net_file
        self.edges: Dict[str, Edge] = {}
        self.junctions: Dict[str, Junction] = {}
        self.location = None
        self.proj_params = None

    def parse(self) -> None:
        """Parse the SUMO network file."""
        logger.info(f"Parsing SUMO network file: {self.net_file}")
        tree = ET.parse(self.net_file)
        root = tree.getroot()

        # Parse location and projection
        self._parse_location(root.find('location'))
        
        # Parse edges (roads)
        for edge_elem in root.findall('edge'):
            if edge_elem.get('function') != 'internal':  # Skip internal edges
                edge = self._parse_edge(edge_elem)
                self.edges[edge.id] = edge

        # Parse junctions
        for junction_elem in root.findall('junction'):
            if junction_elem.get('type') != 'internal':  # Skip internal junctions
                junction = self._parse_junction(junction_elem)
                self.junctions[junction.id] = junction

        logger.info(f"Parsed {len(self.edges)} edges and {len(self.junctions)} junctions")

    def _parse_location(self, location_elem: ET.Element) -> None:
        """Parse network location and projection information."""
        if location_elem is not None:
            self.location = {
                'orig_x': float(location_elem.get('origX', 0)),
                'orig_y': float(location_elem.get('origY', 0)),
                'proj': location_elem.get('projParameter', '')
            }

    def _parse_edge(self, edge_elem: ET.Element) -> Edge:
        """Parse a SUMO edge element."""
        edge_id = edge_elem.get('id')
        from_node = edge_elem.get('from')
        to_node = edge_elem.get('to')
        priority = int(edge_elem.get('priority', 0))
        edge_type = edge_elem.get('type', '')

        lanes = []
        for lane_elem in edge_elem.findall('lane'):
            lane = self._parse_lane(lane_elem)
            lanes.append(lane)

        return Edge(edge_id, from_node, to_node, priority, edge_type, lanes)

    def _parse_lane(self, lane_elem: ET.Element) -> Lane:
        """Parse a SUMO lane element."""
        lane_id = lane_elem.get('id')
        index = int(lane_elem.get('index'))
        speed = float(lane_elem.get('speed'))
        width = float(lane_elem.get('width', 3.2))  # Default width if not specified
        length = float(lane_elem.get('length'))
        
        # Parse shape points
        shape_str = lane_elem.get('shape', '')
        shape = []
        if shape_str:
            points = shape_str.split(' ')
            for point in points:
                x, y = map(float, point.split(','))
                shape.append(Point(x, y))

        return Lane(lane_id, index, speed, width, shape, length)

    def _parse_junction(self, junction_elem: ET.Element) -> Junction:
        """Parse a SUMO junction element."""
        junction_id = junction_elem.get('id')
        junction_type = junction_elem.get('type')
        x = float(junction_elem.get('x'))
        y = float(junction_elem.get('y'))
        inc_lanes = junction_elem.get('incLanes', '').split()
        int_lanes = junction_elem.get('intLanes', '').split()
        
        # Parse requests
        requests = []
        for request in junction_elem.findall('request'):
            requests.append({
                'index': int(request.get('index')),
                'response': request.get('response'),
                'foes': request.get('foes'),
                'cont': request.get('cont', '0')
            })

        return Junction(junction_id, junction_type, x, y, inc_lanes, int_lanes, requests)

class OpenDriveGenerator:
    """Generator for OpenDRIVE .xodr files."""

    def __init__(self, network: SumoNetworkParser):
        """Initialize the generator with parsed SUMO network."""
        self.network = network
        self.root = None

    def generate(self, output_file: str) -> None:
        """Generate OpenDRIVE file from parsed SUMO network."""
        logger.info(f"Generating OpenDRIVE file: {output_file}")
        
        # Create root element
        self.root = ET.Element('OpenDRIVE')
        
        # Add header
        self._add_header()
        
        # Add roads
        self._add_roads()
        
        # Add junctions
        self._add_junctions()
        
        # Write to file
        tree = ET.ElementTree(self.root)
        tree.write(output_file, encoding='utf-8', xml_declaration=True)
        logger.info(f"Successfully generated OpenDRIVE file: {output_file}")

    def _add_header(self) -> None:
        """Add OpenDRIVE header."""
        header = ET.SubElement(self.root, 'header')
        header.set('revMajor', '1')
        header.set('revMinor', '7')
        header.set('name', '')
        header.set('version', '1.00')
        header.set('date', '')
        
        if self.network.location:
            header.set('north', str(self.network.location['orig_y'] + 100))
            header.set('south', str(self.network.location['orig_y'] - 100))
            header.set('east', str(self.network.location['orig_x'] + 100))
            header.set('west', str(self.network.location['orig_x'] - 100))

    def _add_roads(self) -> None:
        """Add roads from SUMO edges."""
        for edge in self.network.edges.values():
            road = ET.SubElement(self.root, 'road')
            road.set('name', edge.id)
            road.set('length', str(edge.lanes[0].length))
            road.set('id', edge.id)
            road.set('junction', '-1')

            # Add planView
            self._add_plan_view(road, edge)

            # Add lanes
            self._add_lanes(road, edge)

    def _add_plan_view(self, road_elem: ET.Element, edge: Edge) -> None:
        """Add planView geometry for a road."""
        plan_view = ET.SubElement(road_elem, 'planView')
        
        # Use first lane's shape for reference line
        if edge.lanes and edge.lanes[0].shape:
            first_point = edge.lanes[0].shape[0]
            last_point = edge.lanes[0].shape[-1]
            
            # Calculate heading
            hdg = math.atan2(last_point.y - first_point.y,
                           last_point.x - first_point.x)
            
            geometry = ET.SubElement(plan_view, 'geometry')
            geometry.set('s', '0.0')
            geometry.set('x', str(first_point.x))
            geometry.set('y', str(first_point.y))
            geometry.set('hdg', str(hdg))
            geometry.set('length', str(edge.lanes[0].length))
            
            # For now, use simple line geometry
            ET.SubElement(geometry, 'line')

    def _add_lanes(self, road_elem: ET.Element, edge: Edge) -> None:
        """Add lanes to a road."""
        lanes = ET.SubElement(road_elem, 'lanes')
        lane_section = ET.SubElement(lanes, 'laneSection')
        lane_section.set('s', '0.0')

        # Add center lane
        center = ET.SubElement(lane_section, 'center')
        center_lane = ET.SubElement(center, 'lane')
        center_lane.set('id', '0')
        center_lane.set('type', 'none')
        center_lane.set('level', 'false')

        # Add right lanes (negative ids)
        right = ET.SubElement(lane_section, 'right')
        for lane in edge.lanes:
            lane_elem = ET.SubElement(right, 'lane')
            lane_elem.set('id', str(-(lane.index + 1)))
            lane_elem.set('type', 'driving')
            lane_elem.set('level', 'false')
            
            # Add width
            width = ET.SubElement(lane_elem, 'width')
            width.set('sOffset', '0.0')
            width.set('a', str(lane.width))
            width.set('b', '0.0')
            width.set('c', '0.0')
            width.set('d', '0.0')
            
            # Add speed
            speed = ET.SubElement(lane_elem, 'speed')
            speed.set('sOffset', '0.0')
            speed.set('max', str(lane.speed))

    def _add_junctions(self) -> None:
        """Add junctions to OpenDRIVE."""
        for junction in self.network.junctions.values():
            junction_elem = ET.SubElement(self.root, 'junction')
            junction_elem.set('name', junction.id)
            junction_elem.set('id', junction.id)

            # Add connections (simplified for now)
            for i, inc_lane in enumerate(junction.inc_lanes):
                connection = ET.SubElement(junction_elem, 'connection')
                connection.set('id', str(i))
                connection.set('incomingRoad', inc_lane.split('_')[0])
                connection.set('connectingRoad', junction.id + '_c' + str(i))
                connection.set('contactPoint', 'start')

def main():
    """Main function to demonstrate usage."""
    import argparse
    parser = argparse.ArgumentParser(description='Convert SUMO network to OpenDRIVE format')
    parser.add_argument('input', help='Input SUMO .net.xml file')
    parser.add_argument('output', help='Output OpenDRIVE .xodr file')
    args = parser.parse_args()

    try:
        # Parse SUMO network
        parser = SumoNetworkParser(args.input)
        parser.parse()

        # Generate OpenDRIVE
        generator = OpenDriveGenerator(parser)
        generator.generate(args.output)

    except Exception as e:
        logger.error(f"Error during conversion: {str(e)}")
        raise

if __name__ == "__main__":
    main() 