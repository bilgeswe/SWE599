import osmnx as ox
import sumolib
import lxml.etree as ET
import matplotlib.pyplot as plt

def parse_osm_basic(osm_file):
    """Parse basic road network information from OSM"""
    print("\n=== Parsing OSM Road Network ===")
    
    # Load OSM data
    G = ox.graph_from_xml(osm_file)
    
    # Count road types
    road_types = {}
    for _, _, data in G.edges(data=True):
        if 'highway' in data:
            road_type = data['highway']
            if isinstance(road_type, list):
                road_type = road_type[0]  # Take the first type if multiple
            road_types[road_type] = road_types.get(road_type, 0) + 1
    
    print("\nRoad Types in OSM:")
    for road_type, count in road_types.items():
        print(f"{road_type}: {count} segments")
    
    return G

def parse_sumo_basic(net_file):
    """Parse basic road network information from SUMO"""
    print("\n=== Parsing SUMO Road Network ===")
    
    # Load SUMO network
    net = sumolib.net.readNet(net_file)
    
    # Count edge types
    edge_types = {}
    for edge in net.getEdges():
        edge_type = edge.getType()
        edge_types[edge_type] = edge_types.get(edge_type, 0) + 1
    
    print("\nEdge Types in SUMO:")
    for edge_type, count in edge_types.items():
        print(f"{edge_type}: {count} edges")
    
    return net

def create_basic_opendrive(roads, output_file):
    """Create basic OpenDRIVE structure without elevation"""
    print("\n=== Creating Basic OpenDRIVE Structure ===")
    
    # Create OpenDRIVE structure
    root = ET.Element("OpenDRIVE")
    header = ET.SubElement(root, "header")
    header.set("revMajor", "1")
    header.set("revMinor", "7")
    
    # Add roads
    for road in roads:
        road_elem = ET.SubElement(root, "road")
        road_elem.set("id", str(road['id']))
        road_elem.set("name", road['name'])
        
        # Add planView (geometry)
        plan_view = ET.SubElement(road_elem, "planView")
        geometry = ET.SubElement(plan_view, "geometry")
        geometry.set("s", "0.0")
        geometry.set("x", str(road['x']))
        geometry.set("y", str(road['y']))
        geometry.set("hdg", "0.0")
        geometry.set("length", str(road['length']))
        line = ET.SubElement(geometry, "line")
        
        # Add lanes
        lanes = ET.SubElement(road_elem, "lanes")
        lane_section = ET.SubElement(lanes, "laneSection")
        lane_section.set("s", "0.0")
        
        # Add center lane
        center = ET.SubElement(lane_section, "center")
        lane = ET.SubElement(center, "lane")
        lane.set("id", "0")
        lane.set("type", "none")
        
        # Add right lanes
        right = ET.SubElement(lane_section, "right")
        for i in range(road['lanes']):
            lane = ET.SubElement(right, "lane")
            lane.set("id", str(-(i+1)))
            lane.set("type", "driving")
    
    # Write to file
    tree = ET.ElementTree(root)
    tree.write(output_file, pretty_print=True, xml_declaration=True, encoding="UTF-8")
    print(f"Created basic OpenDRIVE file: {output_file}")

def visualize_basic_network(network, format_type):
    """Visualize basic road network"""
    print(f"\n=== Visualizing {format_type} Network ===")
    
    if format_type == "OSM":
        # Plot OSM network
        fig, ax = ox.plot_graph(network, node_size=0, edge_linewidth=0.5)
        plt.title("OSM Road Network")
    
    elif format_type == "SUMO":
        # Create a new figure
        fig, ax = plt.subplots(figsize=(10, 10))
        
        # Plot edges
        for edge in network.getEdges():
            shape = edge.getShape()
            x_coords = [point[0] for point in shape]
            y_coords = [point[1] for point in shape]
            ax.plot(x_coords, y_coords, 'k-', linewidth=0.5)
        
        plt.title("SUMO Road Network")
    
    plt.show()

if __name__ == "__main__":
    # Example usage
    osm_file = "levent.osm"
    net_file = "levent.net.xml"
    xodr_file = "levent_basic.xodr"
    
    # Parse OSM
    osm_network = parse_osm_basic(osm_file)
    
    # Parse SUMO
    sumo_network = parse_sumo_basic(net_file)
    
    # Create basic OpenDRIVE
    roads = [
        {'id': 1, 'name': 'Road1', 'x': 29.0088, 'y': 41.0751, 'length': 100.0, 'lanes': 2},
        {'id': 2, 'name': 'Road2', 'x': 29.0128, 'y': 41.0781, 'length': 150.0, 'lanes': 3}
    ]
    create_basic_opendrive(roads, xodr_file)
    
    # Visualize networks
    visualize_basic_network(osm_network, "OSM")
    visualize_basic_network(sumo_network, "SUMO") 