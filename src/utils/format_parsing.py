import osmnx as ox
import sumolib
import lxml.etree as ET
import matplotlib.pyplot as plt

def parse_osm(osm_file):
    """Parse OSM file and extract road network information"""
    print("\n=== Parsing OSM File ===")
    
    # Load OSM data
    G = ox.graph_from_xml(osm_file)
    
    # Extract nodes and edges
    nodes = G.nodes(data=True)
    edges = G.edges(data=True)
    
    print(f"Found {len(nodes)} nodes and {len(edges)} edges")
    
    # Example: Print first node and edge
    if nodes:
        first_node = next(iter(nodes))
        print(f"\nFirst node: {first_node}")
    
    if edges:
        first_edge = next(iter(edges))
        print(f"First edge: {first_edge}")
    
    return G

def parse_sumo(net_file):
    """Parse SUMO network file and extract network information"""
    print("\n=== Parsing SUMO Network ===")
    
    # Load SUMO network
    net = sumolib.net.readNet(net_file)
    
    # Extract nodes and edges
    nodes = net.getNodes()
    edges = net.getEdges()
    
    print(f"Found {len(nodes)} nodes and {len(edges)} edges")
    
    # Example: Print first node and edge
    if nodes:
        first_node = nodes[0]
        print(f"\nFirst node: ID={first_node.getID()}, Type={first_node.getType()}")
    
    if edges:
        first_edge = edges[0]
        print(f"First edge: ID={first_edge.getID()}, From={first_edge.getFromNode().getID()}, To={first_edge.getToNode().getID()}")
    
    return net

def parse_opendrive(xodr_file):
    """Parse OpenDRIVE file and extract road network information"""
    print("\n=== Parsing OpenDRIVE File ===")
    
    # Parse XML
    tree = ET.parse(xodr_file)
    root = tree.getroot()
    
    # Extract roads
    roads = root.findall('.//road')
    
    print(f"Found {len(roads)} roads")
    
    # Example: Print first road
    if roads:
        first_road = roads[0]
        print(f"\nFirst road: ID={first_road.get('id')}, Name={first_road.get('name')}")
        
        # Extract lanes
        lanes = first_road.findall('.//lane')
        print(f"Found {len(lanes)} lanes in first road")
    
    return tree

def visualize_network(network, format_type):
    """Visualize the network based on format type"""
    print(f"\n=== Visualizing {format_type} Network ===")
    
    if format_type == "OSM":
        # Plot OSM network
        fig, ax = ox.plot_graph(network, node_size=0, edge_linewidth=0.5)
        plt.title("OSM Network")
    
    elif format_type == "SUMO":
        # Create a new figure
        fig, ax = plt.subplots(figsize=(10, 10))
        
        # Plot edges
        for edge in network.getEdges():
            shape = edge.getShape()
            x_coords = [point[0] for point in shape]
            y_coords = [point[1] for point in shape]
            ax.plot(x_coords, y_coords, 'k-', linewidth=0.5)
        
        plt.title("SUMO Network")
    
    plt.show()

if __name__ == "__main__":
    # Example usage
    osm_file = "levent.osm"
    net_file = "levent.net.xml"
    xodr_file = "levent.xodr"  # Note: This file doesn't exist yet
    
    # Parse OSM
    osm_network = parse_osm(osm_file)
    
    # Parse SUMO
    sumo_network = parse_sumo(net_file)
    
    # Try to parse OpenDRIVE (will fail as file doesn't exist)
    try:
        opendrive_tree = parse_opendrive(xodr_file)
    except FileNotFoundError:
        print("\nOpenDRIVE file not found. This is expected as we haven't created it yet.")
    
    # Visualize networks
    visualize_network(osm_network, "OSM")
    visualize_network(sumo_network, "SUMO") 