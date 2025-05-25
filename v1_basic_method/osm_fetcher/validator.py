"""
Validate and analyze OSM road network data.
"""

import os
import osmnx as ox
import networkx as nx
import xml.etree.ElementTree as ET
from typing import Dict, List, Tuple, Set
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class OSMValidator:
    """Class for validating OSM road network data."""
    
    def __init__(self, osm_file: str):
        """
        Initialize validator with OSM file path.
        
        Args:
            osm_file (str): Path to the .osm file
        """
        self.osm_file = osm_file
        self.tree = ET.parse(osm_file)
        self.root = self.tree.getroot()
        
        # Load the graph using OSMnx's graph_from_xml
        try:
            self.G = ox.graph_from_xml(osm_file)
        except Exception as e:
            logger.error(f"Error loading graph from XML: {str(e)}")
            # Fallback to basic graph creation
            self.G = nx.DiGraph()
            self._create_basic_graph()
        
    def _create_basic_graph(self) -> None:
        """Create a basic graph from the XML data."""
        # Add nodes
        for node in self.root.findall('.//node'):
            node_id = node.get('id')
            lat = float(node.get('lat'))
            lon = float(node.get('lon'))
            self.G.add_node(node_id, lat=lat, lon=lon)
        
        # Add edges
        for way in self.root.findall('.//way'):
            # Check if this is a highway
            is_highway = False
            for tag in way.findall('tag'):
                if tag.get('k') == 'highway':
                    is_highway = True
                    break
            
            if is_highway:
                nodes = way.findall('nd')
                for i in range(len(nodes) - 1):
                    u = nodes[i].get('ref')
                    v = nodes[i + 1].get('ref')
                    if u in self.G and v in self.G:
                        self.G.add_edge(u, v)
        
    def validate_basic_structure(self) -> Tuple[bool, List[str]]:
        """
        Validate basic XML structure and required elements.
        
        Returns:
            Tuple[bool, List[str]]: (is_valid, list_of_issues)
        """
        issues = []
        
        # Check root element
        if self.root.tag != 'osm':
            issues.append("Root element must be 'osm'")
            
        # Check version attribute
        if 'version' not in self.root.attrib:
            issues.append("Missing version attribute in root element")
            
        # Check for required elements
        required_elements = ['node', 'way']
        for element in required_elements:
            if not self.root.findall(f'.//{element}'):
                issues.append(f"No {element} elements found")
                
        return len(issues) == 0, issues
        
    def validate_road_network(self) -> Tuple[bool, List[str]]:
        """
        Validate road network specific elements and attributes.
        
        Returns:
            Tuple[bool, List[str]]: (is_valid, list_of_issues)
        """
        issues = []
        
        # Check for highway ways
        highway_ways = []
        for way in self.root.findall('.//way'):
            for tag in way.findall('tag'):
                if tag.get('k') == 'highway':
                    highway_ways.append(way)
                    break
        
        if not highway_ways:
            issues.append("No highway ways found")
            
        # Validate node references
        for way in highway_ways:
            nd_refs = way.findall('nd')
            if len(nd_refs) < 2:
                issues.append(f"Way {way.get('id')} has insufficient nodes")
                
        return len(issues) == 0, issues
        
    def validate_connectivity(self) -> Tuple[bool, List[str]]:
        """
        Validate network connectivity and topology.
        
        Returns:
            Tuple[bool, List[str]]: (is_valid, list_of_issues)
        """
        issues = []
        
        if not self.G.nodes():
            issues.append("Empty graph - no nodes found")
            return False, issues
        
        # Check for isolated nodes
        isolated_nodes = list(nx.isolates(self.G))
        if isolated_nodes:
            issues.append(f"Found {len(isolated_nodes)} isolated nodes")
            
        # Check for disconnected components
        components = list(nx.connected_components(self.G.to_undirected()))
        if len(components) > 1:
            issues.append(f"Network has {len(components)} disconnected components")
            
        return len(issues) == 0, issues
        
    def validate_attributes(self) -> Tuple[bool, List[str]]:
        """
        Validate road attributes and metadata.
        
        Returns:
            Tuple[bool, List[str]]: (is_valid, list_of_issues)
        """
        issues = []
        required_attrs = {'highway', 'lanes', 'maxspeed', 'oneway'}
        
        # Check for missing attributes
        for _, _, data in self.G.edges(data=True):
            missing_attrs = required_attrs - set(data.keys())
            if missing_attrs:
                issues.append(f"Edge missing attributes: {missing_attrs}")
                
        return len(issues) == 0, issues
        
    def analyze_network(self) -> Dict:
        """
        Analyze network characteristics.
        
        Returns:
            Dict: Network statistics
        """
        if not self.G.nodes():
            return {
                'total_nodes': 0,
                'total_edges': 0,
                'road_types': {},
                'avg_degree': 0,
                'density': 0,
                'is_connected': False,
                'components': 0
            }
            
        stats = {
            'total_nodes': len(self.G.nodes()),
            'total_edges': len(self.G.edges()),
            'road_types': {},
            'avg_degree': sum(dict(self.G.degree()).values()) / len(self.G.nodes()),
            'density': nx.density(self.G),
            'is_connected': nx.is_connected(self.G.to_undirected()),
            'components': len(list(nx.connected_components(self.G.to_undirected())))
        }
        
        # Count road types
        for _, _, data in self.G.edges(data=True):
            road_type = data.get('highway', 'unknown')
            if isinstance(road_type, list):
                road_type = road_type[0]
            stats['road_types'][road_type] = stats['road_types'].get(road_type, 0) + 1
            
        return stats

def main():
    """Command line interface for the OSM Validator."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Validate OSM road network data')
    parser.add_argument('osm_file', help='Path to the .osm file')
    parser.add_argument('--output-dir', default='data/validation', 
                      help='Directory to save validation reports')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.osm_file):
        print(f"Error: File {args.osm_file} does not exist")
        exit(1)
        
    try:
        # Create output directory
        Path(args.output_dir).mkdir(parents=True, exist_ok=True)
        
        # Initialize validator
        validator = OSMValidator(args.osm_file)
        
        # Run validations
        print("\nRunning validations...")
        
        # Basic structure validation
        is_valid, issues = validator.validate_basic_structure()
        print("\nBasic Structure Validation:")
        if is_valid:
            print("✅ Basic structure is valid")
        else:
            print("❌ Basic structure issues found:")
            for issue in issues:
                print(f"  - {issue}")
                
        # Road network validation
        is_valid, issues = validator.validate_road_network()
        print("\nRoad Network Validation:")
        if is_valid:
            print("✅ Road network is valid")
        else:
            print("❌ Road network issues found:")
            for issue in issues:
                print(f"  - {issue}")
                
        # Connectivity validation
        is_valid, issues = validator.validate_connectivity()
        print("\nConnectivity Validation:")
        if is_valid:
            print("✅ Network connectivity is valid")
        else:
            print("❌ Connectivity issues found:")
            for issue in issues:
                print(f"  - {issue}")
                
        # Attributes validation
        is_valid, issues = validator.validate_attributes()
        print("\nAttributes Validation:")
        if is_valid:
            print("✅ Road attributes are valid")
        else:
            print("❌ Attribute issues found:")
            for issue in issues:
                print(f"  - {issue}")
                
        # Network analysis
        stats = validator.analyze_network()
        print("\nNetwork Analysis:")
        print(f"Total Nodes: {stats['total_nodes']}")
        print(f"Total Edges: {stats['total_edges']}")
        print(f"Average Node Degree: {stats['avg_degree']:.2f}")
        print(f"Network Density: {stats['density']:.4f}")
        print(f"Is Connected: {'Yes' if stats['is_connected'] else 'No'}")
        print(f"Number of Components: {stats['components']}")
        
        print("\nRoad Types Distribution:")
        for road_type, count in sorted(stats['road_types'].items()):
            print(f"  - {road_type}: {count} segments")
            
    except Exception as e:
        print(f"Error: {str(e)}")
        exit(1)

if __name__ == "__main__":
    main() 