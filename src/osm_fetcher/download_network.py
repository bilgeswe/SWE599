#!/usr/bin/env python3
import os
import osmnx as ox
import networkx as nx
import argparse

# Configure OSMnx
ox.settings.use_cache = True
ox.settings.cache_folder = 'data/cache'
ox.settings.all_oneway = True
ox.settings.useful_tags_path = [
    'bridge', 'tunnel', 'oneway', 'lanes', 'ref', 'name',
    'highway', 'maxspeed', 'service', 'access', 'area',
    'landuse', 'width', 'est_width', 'junction'
]

def download_network(place_name, output_dir='data/networks'):
    """
    Download road network data for a specified location.
    
    Args:
        place_name (str): Name of the place to download (e.g., "Levent, Istanbul, Turkey")
        output_dir (str): Directory to save the output files
    """
    # Create output directories if they don't exist
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs('data/cache', exist_ok=True)
    
    # Download the road network using osmnx
    print(f"Downloading road network for {place_name}...")
    print("This may take a few minutes depending on the area size...")
    
    try:
        # Download with custom filter to include all road types
        custom_filter = (
            '["highway"]'
            '["highway"!~"abandoned|construction|proposed|platform|raceway"]'
            '["area"!~"yes"]'
            '["service"!~"private"]'
        )
        
        G = ox.graph_from_place(
            place_name,
            network_type='all',  # Get all street types
            simplify=False,      # Don't simplify the graph
            retain_all=True,     # Keep all nodes
            truncate_by_edge=True,  # Don't truncate the graph
            custom_filter=custom_filter
        )
    except Exception as e:
        print(f"Error downloading full area: {e}")
        print("Trying with a smaller area...")
        # If that fails, try with a smaller area but same parameters
        G = ox.graph_from_place(
            place_name,
            network_type='all',
            simplify=False,
            retain_all=True,
            truncate_by_edge=True,
            custom_filter=custom_filter,
            which_result=1
        )
    
    # Save as OSM file
    place_name_simple = place_name.split(',')[0].lower().strip()
    osm_file = os.path.join(output_dir, f"{place_name_simple}.osm")
    print(f"Saving OSM data to {osm_file}...")
    ox.save_graph_xml(G, filepath=osm_file)
    
    print("\nDownload complete!")
    print(f"OSM file saved to: {osm_file}")
    
    # Print basic statistics
    print("\nNetwork Statistics:")
    print(f"Total nodes: {len(G.nodes())}")
    print(f"Total edges: {len(G.edges())}")
    
    # Count road types
    road_types = {}
    for _, _, data in G.edges(data=True):
        road_type = data.get('highway', 'unknown')
        if isinstance(road_type, list):
            road_type = road_type[0]
        road_types[road_type] = road_types.get(road_type, 0) + 1
    
    print("\nRoad Types:")
    for road_type, count in sorted(road_types.items()):
        print(f"{road_type}: {count} segments")

def main():
    parser = argparse.ArgumentParser(description='Download OSM road network data by place name')
    parser.add_argument('place_name', help='Name of the place (e.g., "Levent, Istanbul, Turkey")')
    parser.add_argument('--output-dir', default='data/networks', help='Output directory')
    
    args = parser.parse_args()
    download_network(args.place_name, args.output_dir)

if __name__ == "__main__":
    main() 