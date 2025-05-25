"""OpenDRIVE exporter for converting SUMO networks to OpenDRIVE XML format."""

import xml.etree.ElementTree as ET
from xml.dom import minidom
from typing import List, Dict, Tuple, Optional
import math
from datetime import datetime

# Use try-catch for imports to handle different contexts
try:
    from av_algorithms.path_planner import Node, Edge
    from av_algorithms.traffic_light_handler import TrafficLight
except ImportError:
    # Fallback for when running from different directory
    import sys
    from pathlib import Path
    sys.path.append(str(Path(__file__).parent.parent.parent))
    from av_algorithms.path_planner import Node, Edge
    from av_algorithms.traffic_light_handler import TrafficLight


class OpenDRIVEExporter:
    """Exports SUMO network data to OpenDRIVE XML format."""
    
    def __init__(self):
        """Initialize the OpenDRIVE exporter."""
        self.roads = {}
        self.junctions = {}
        self.road_counter = 1
        self.junction_counter = 1
        
    def export_network(self, nodes: List, edges: List, 
                      traffic_lights: List,
                      output_path: str,
                      net_offset: Tuple[float, float] = (0, 0)) -> str:
        """Export SUMO network to OpenDRIVE format.
        
        Args:
            nodes: List of network nodes
            edges: List of network edges  
            traffic_lights: List of traffic lights
            output_path: Path to save the OpenDRIVE file
            net_offset: Network offset for coordinate transformation
            
        Returns:
            Path to the exported OpenDRIVE file
        """
        # Create root OpenDRIVE element
        root = ET.Element("OpenDRIVE")
        
        # Add header
        self._add_header(root, net_offset)
        
        # Process network data
        self._process_nodes_and_edges(nodes, edges)
        
        # Add roads to XML
        for road_id, road_data in self.roads.items():
            road_elem = self._create_road_element(road_data)
            root.append(road_elem)
            
        # Add junctions to XML
        for junction_id, junction_data in self.junctions.items():
            junction_elem = self._create_junction_element(junction_data)
            root.append(junction_elem)
            
        # Add traffic lights
        self._add_traffic_lights(root, traffic_lights)
        
        # Write to file
        self._write_xml(root, output_path)
        
        return output_path
        
    def _add_header(self, root: ET.Element, net_offset: Tuple[float, float]):
        """Add OpenDRIVE header information."""
        header = ET.SubElement(root, "header")
        header.set("revMajor", "1")
        header.set("revMinor", "4")
        header.set("name", "Uskudar_Network")
        header.set("version", "1.0")
        header.set("date", datetime.now().isoformat())
        header.set("north", "0.0")
        header.set("south", "0.0") 
        header.set("east", "0.0")
        header.set("west", "0.0")
        header.set("vendor", "SWE599_AV_Simulation")
        
        # Add geographic reference
        geo_ref = ET.SubElement(header, "geoReference")
        # Use UTM Zone 35N for Istanbul
        geo_ref.text = f"+proj=utm +zone=35 +datum=WGS84 +units=m +no_defs +x_0={net_offset[0]} +y_0={net_offset[1]}"
        
    def _process_nodes_and_edges(self, nodes: List[Node], edges: List[Edge]):
        """Process SUMO nodes and edges to create OpenDRIVE roads and junctions."""
        # Create node lookup
        node_map = {node.id: node for node in nodes}
        
        # Identify junctions (nodes with multiple incoming/outgoing edges)
        junction_nodes = set()
        node_connections = {}
        
        for edge in edges:
            # Count connections for each node
            if edge.from_node not in node_connections:
                node_connections[edge.from_node] = {'in': 0, 'out': 0}
            if edge.to_node not in node_connections:
                node_connections[edge.to_node] = {'in': 0, 'out': 0}
                
            node_connections[edge.from_node]['out'] += 1
            node_connections[edge.to_node]['in'] += 1
            
        # Nodes with multiple connections are junctions
        for node_id, connections in node_connections.items():
            if connections['in'] + connections['out'] > 2:
                junction_nodes.add(node_id)
                
        # Create roads for simple edge connections
        for edge in edges:
            if edge.from_node not in junction_nodes and edge.to_node not in junction_nodes:
                self._create_road_from_edge(edge, node_map)
            else:
                # Edge connects to/from junction - handle separately
                self._handle_junction_edge(edge, node_map, junction_nodes)
                
        # Create junction elements
        for junction_node_id in junction_nodes:
            if junction_node_id in node_map:
                self._create_junction(junction_node_id, node_map[junction_node_id])
                
    def _create_road_from_edge(self, edge: Edge, node_map: Dict[str, Node]):
        """Create an OpenDRIVE road from a SUMO edge."""
        from_node = node_map.get(edge.from_node)
        to_node = node_map.get(edge.to_node)
        
        if not from_node or not to_node:
            return
            
        road_id = str(self.road_counter)
        self.road_counter += 1
        
        # Calculate road geometry
        start_x, start_y = from_node.x, from_node.y
        end_x, end_y = to_node.x, to_node.y
        
        length = math.sqrt((end_x - start_x)**2 + (end_y - start_y)**2)
        heading = math.atan2(end_y - start_y, end_x - start_x)
        
        road_data = {
            'id': road_id,
            'name': f"Road_{edge.id}",
            'length': length,
            'junction': "-1",  # Not part of junction
            'rule': "RHT",  # Right-hand traffic
            'geometry': {
                'start_x': start_x,
                'start_y': start_y,
                'heading': heading,
                'length': length
            },
            'lanes': self._create_lanes_from_edge(edge),
            'edge_id': edge.id,
            'from_node': edge.from_node,
            'to_node': edge.to_node
        }
        
        self.roads[road_id] = road_data
        
    def _create_lanes_from_edge(self, edge: Edge) -> Dict:
        """Create lane information from SUMO edge."""
        lanes_data = {
            'lane_sections': []
        }
        
        # Create a single lane section for the entire road
        lane_section = {
            's': 0.0,
            'center_lane': {
                'id': 0,
                'type': 'none',
                'level': False
            },
            'right_lanes': []
        }
        
        # Add lanes from the edge
        if hasattr(edge, 'lanes') and edge.lanes:
            for i, lane_id in enumerate(edge.lanes):
                lane_data = {
                    'id': -(i + 1),  # Right lanes have negative IDs
                    'type': 'driving',
                    'level': False,
                    'width': 3.5,  # Standard lane width
                    'speed_limit': getattr(edge, 'speed_limit', 13.89)  # Default 50 km/h
                }
                lane_section['right_lanes'].append(lane_data)
        else:
            # Default single lane
            lane_data = {
                'id': -1,
                'type': 'driving', 
                'level': False,
                'width': 3.5,
                'speed_limit': getattr(edge, 'speed_limit', 13.89)
            }
            lane_section['right_lanes'].append(lane_data)
            
        lanes_data['lane_sections'].append(lane_section)
        return lanes_data
        
    def _handle_junction_edge(self, edge: Edge, node_map: Dict[str, Node], junction_nodes: set):
        """Handle edges that connect to junctions."""
        # For now, treat junction edges as regular roads
        # In a full implementation, these would be junction connection roads
        self._create_road_from_edge(edge, node_map)
        
    def _create_junction(self, junction_id: str, junction_node: Node):
        """Create an OpenDRIVE junction."""
        junction_data = {
            'id': str(self.junction_counter),
            'name': f"Junction_{junction_id}",
            'node_id': junction_id,
            'x': junction_node.x,
            'y': junction_node.y,
            'connections': []
        }
        
        self.junctions[str(self.junction_counter)] = junction_data
        self.junction_counter += 1
        
    def _create_road_element(self, road_data: Dict) -> ET.Element:
        """Create XML element for a road."""
        road = ET.Element("road")
        road.set("name", road_data['name'])
        road.set("length", f"{road_data['length']:.6f}")
        road.set("id", road_data['id'])
        road.set("junction", road_data['junction'])
        road.set("rule", road_data['rule'])
        
        # Add plan view (geometry)
        plan_view = ET.SubElement(road, "planView")
        geometry = ET.SubElement(plan_view, "geometry")
        geometry.set("s", "0.0")
        geometry.set("x", f"{road_data['geometry']['start_x']:.6f}")
        geometry.set("y", f"{road_data['geometry']['start_y']:.6f}")
        geometry.set("hdg", f"{road_data['geometry']['heading']:.6f}")
        geometry.set("length", f"{road_data['geometry']['length']:.6f}")
        
        # Add line geometry
        line = ET.SubElement(geometry, "line")
        
        # Add lanes
        lanes = ET.SubElement(road, "lanes")
        
        for section_data in road_data['lanes']['lane_sections']:
            lane_section = ET.SubElement(lanes, "laneSection")
            lane_section.set("s", f"{section_data['s']:.6f}")
            
            # Center lane
            center = ET.SubElement(lane_section, "center")
            center_lane = ET.SubElement(center, "lane")
            center_lane.set("id", "0")
            center_lane.set("type", "none")
            center_lane.set("level", "false")
            
            # Right lanes
            if section_data['right_lanes']:
                right = ET.SubElement(lane_section, "right")
                for lane_data in section_data['right_lanes']:
                    lane = ET.SubElement(right, "lane")
                    lane.set("id", str(lane_data['id']))
                    lane.set("type", lane_data['type'])
                    lane.set("level", str(lane_data['level']).lower())
                    
                    # Lane width
                    width = ET.SubElement(lane, "width")
                    width.set("sOffset", "0.0")
                    width.set("a", f"{lane_data['width']:.6f}")
                    width.set("b", "0.0")
                    width.set("c", "0.0") 
                    width.set("d", "0.0")
                    
                    # Speed limit
                    speed = ET.SubElement(lane, "speed")
                    speed.set("sOffset", "0.0")
                    speed.set("max", f"{lane_data['speed_limit']:.6f}")
                    
        return road
        
    def _create_junction_element(self, junction_data: Dict) -> ET.Element:
        """Create XML element for a junction."""
        junction = ET.Element("junction")
        junction.set("name", junction_data['name'])
        junction.set("id", junction_data['id'])
        
        return junction
        
    def _add_traffic_lights(self, root: ET.Element, traffic_lights: List[TrafficLight]):
        """Add traffic lights as OpenDRIVE signals."""
        # Traffic lights would be added as road signals in a full implementation
        # For now, we'll skip this as it requires complex road-signal associations
        pass
        
    def _write_xml(self, root: ET.Element, output_path: str):
        """Write XML to file with proper formatting."""
        # Convert to string
        rough_string = ET.tostring(root, 'unicode')
        
        # Parse and pretty print
        reparsed = minidom.parseString(rough_string)
        pretty_string = reparsed.toprettyxml(indent="  ")
        
        # Remove extra blank lines
        lines = [line for line in pretty_string.split('\n') if line.strip()]
        final_string = '\n'.join(lines)
        
        # Write to file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(final_string)
            
        print(f"OpenDRIVE file exported to: {output_path}") 