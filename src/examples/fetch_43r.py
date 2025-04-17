"""
Example script to fetch and analyze OSM data for Istanbul 43R bus route area.
"""

import os
import osmnx as ox
import networkx as nx
from src.osm_fetcher.fetcher import OSMFetcher

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
    # Initialize the fetcher
    fetcher = OSMFetcher()
    
    # Define the area of interest (43R bus route area in Istanbul)
    place_name = "Istanbul, Turkey"
    print(f"\nFetching OSM data for {place_name}...")
    
    try:
        # Fetch the data with bus route information
        osm_file = fetcher.fetch_by_place(place_name, network_type="all")
        print(f"Successfully downloaded OSM data to: {osm_file}")
        
        # Load the graph for analysis
        G = ox.graph_from_place(place_name, network_type="all")
        
        # Analyze the network
        analyze_network(G)
        
        # Save a visualization of the network
        print("\nGenerating visualization...")
        fig, ax = ox.plot_graph(G, 
                              node_color='red',
                              node_size=5,
                              edge_color='gray',
                              edge_linewidth=0.5,
                              show=False)
        
        # Create plots directory if it doesn't exist
        os.makedirs("data/plots", exist_ok=True)
        
        # Save the plot
        plot_path = "data/plots/43r_route_network.png"
        fig.savefig(plot_path, dpi=300, bbox_inches='tight')
        print(f"Saved network visualization to: {plot_path}")
        
        # Fetch detailed area using bounding box
        print("\nFetching detailed area using bounding box...")
        bbox = (41.0697, 41.0297, 29.0324, 28.9724)  # Area covering 43R route
        detailed_osm = fetcher.fetch_by_bbox(bbox, network_type="all")
        print(f"Successfully downloaded detailed OSM data to: {detailed_osm}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()