"""
Script to fetch and analyze OSM data for Kadıköy district in Istanbul.
"""

import os
import osmnx as ox
import networkx as nx

def analyze_network(G):
    """Analyze the road network and print basic statistics."""
    # Basic stats
    num_nodes = G.number_of_nodes()
    num_edges = G.number_of_edges()
    
    # Road type statistics
    road_types = {}
    for _, _, data in G.edges(data=True):
        highway_type = data.get('highway', 'unknown')
        if isinstance(highway_type, list):
            highway_type = highway_type[0]
        road_types[highway_type] = road_types.get(highway_type, 0) + 1
    
    print("\nNetwork Statistics:")
    print(f"Number of nodes (intersections): {num_nodes}")
    print(f"Number of edges (road segments): {num_edges}")
    print("\nRoad types distribution:")
    for road_type, count in sorted(road_types.items(), key=lambda x: x[1], reverse=True):
        print(f"  {road_type}: {count} segments")

def main():
    # Define the area of interest (Kadıköy district)
    place_name = "Kadıköy, Istanbul, Turkey"
    print(f"\nFetching OSM data for {place_name}...")
    
    try:
        # Configure OSMnx settings
        ox.settings.use_cache = True
        ox.settings.log_console = True
        ox.settings.all_oneway = True
        
        # Create output directory
        os.makedirs("data/osm", exist_ok=True)
        os.makedirs("data/plots", exist_ok=True)
        
        # Fetch the data with road network information (no simplification)
        G = ox.graph_from_place(place_name, network_type="drive", simplify=False)
        
        # Save OSM data
        osm_file = os.path.join("data/osm", "kadikoy.osm")
        ox.save_graph_xml(G, filepath=osm_file)
        print(f"Successfully saved OSM data to: {osm_file}")
        
        # Create simplified version for analysis and visualization
        G_simple = ox.simplify_graph(G)
        
        # Analyze the network
        analyze_network(G_simple)
        
        # Save a visualization of the network
        print("\nGenerating visualization...")
        fig, ax = ox.plot_graph(G_simple, 
                              node_color='red',
                              node_size=5,
                              edge_color='gray',
                              edge_linewidth=0.5,
                              show=False)
        
        # Save the plot
        plot_path = "data/plots/kadikoy_network.png"
        fig.savefig(plot_path, dpi=300, bbox_inches='tight')
        print(f"Saved network visualization to: {plot_path}")
        
        # Fetch detailed area using bounding box
        print("\nFetching detailed area using bounding box...")
        # Bounding box for Kadıköy district
        bbox = (41.02, 40.98, 29.05, 29.00)
        G_detailed = ox.graph_from_bbox(bbox[0], bbox[1], bbox[2], bbox[3], 
                                      network_type="drive", simplify=False)
        
        # Save detailed OSM data
        detailed_osm = os.path.join("data/osm", "kadikoy_detailed.osm")
        ox.save_graph_xml(G_detailed, filepath=detailed_osm)
        print(f"Successfully saved detailed OSM data to: {detailed_osm}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main() 