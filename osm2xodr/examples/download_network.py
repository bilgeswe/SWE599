import osmnx as ox
import os
import subprocess
from sumolib import checkBinary

def download_and_convert_network(place_name, output_dir="."):
    """
    Download OSM data for a place and convert it to SUMO format.
    
    Args:
        place_name (str): Name of the place to download (e.g., "Levent, Istanbul, Turkey")
        output_dir (str): Directory to save the output files
    """
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Configure OSMnx settings
    ox.settings.all_oneway = True
    ox.settings.use_cache = True
    
    # Download the road network from OSM (unsimplified)
    print(f"Downloading road network for {place_name}...")
    G = ox.graph_from_place(place_name, network_type='drive', simplify=False)
    
    # Save the OSM data
    place_clean = place_name.split(',')[0].lower().replace(' ', '_')
    osm_file = os.path.join(output_dir, f"{place_clean}.osm")
    net_file = os.path.join(output_dir, f"{place_clean}.net.xml")
    
    # Save as OSM XML
    print(f"Saving OSM data to {osm_file}...")
    ox.save_graph_xml(G, filepath=osm_file)
    print(f"Successfully saved OSM data to {osm_file}")
    
    # Convert OSM to SUMO network using netconvert
    print("Converting to SUMO network...")
    netconvert = checkBinary('netconvert')
    
    # Build netconvert command with additional options for better conversion
    netconvert_cmd = [
        netconvert,
        '--osm', osm_file,
        '--output', net_file,
        '--geometry.remove',
        '--roundabouts.guess',
        '--ramps.guess',
        '--junctions.join',
        '--tls.guess-signals',
        '--tls.discard-simple',
        '--tls.join',
        '--remove-edges.isolated',
        '--geometry.max-grade.fix',
        '--geometry.max-angle', '45',
        '--ignore-errors',
        '--verbose'
    ]
    
    # Run netconvert
    try:
        result = subprocess.run(netconvert_cmd, check=True, capture_output=True, text=True)
        print(f"Successfully converted network to SUMO format")
        print(f"Saved SUMO network to {net_file}")
    except subprocess.CalledProcessError as e:
        print(f"Error converting network: {e}")
        print(f"netconvert output: {e.output}")
        return None, None
    
    return osm_file, net_file

if __name__ == "__main__":
    # Example usage
    place = "Levent, Istanbul, Turkey"
    osm_file, net_file = download_and_convert_network(place)
    if osm_file and net_file:
        print(f"\nConversion complete!")
        print(f"OSM file: {osm_file}")
        print(f"SUMO network file: {net_file}")
    else:
        print("Conversion failed.") 