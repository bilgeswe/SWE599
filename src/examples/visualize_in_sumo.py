"""
Script to convert OSM data to SUMO format and visualize it.
"""

import os
import subprocess
from pathlib import Path
import sys
from sumo import SUMO_HOME

def convert_to_sumo(osm_file: str, output_dir: str = "data/sumo"):
    """Convert OSM file to SUMO network format."""
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate output filenames
    base_name = Path(osm_file).stem
    net_file = os.path.join(output_dir, f"{base_name}.net.xml")
    
    print(f"Converting {osm_file} to SUMO format...")
    
    # Run netconvert using the Python package
    cmd = [
        "netconvert",
        "--osm", osm_file,
        "--output", net_file,
        "--geometry.remove",
        "--roundabouts.guess",
        "--ramps.guess",
        "--junctions.join",
        "--tls.guess-signals",
        "--tls.discard-simple",
        "--verbose",
    ]
    
    subprocess.run(cmd, check=True)
    print(f"Created SUMO network file: {net_file}")
    
    return net_file

def open_in_sumo_gui(net_file: str):
    """Open the network file in SUMO GUI."""
    cmd = ["sumo-gui", "-n", net_file]
    print(f"\nOpening {net_file} in SUMO GUI...")
    subprocess.Popen(cmd)  # Using Popen to not block

if __name__ == "__main__":
    # Add SUMO_HOME/bin to PATH
    os.environ["PATH"] = os.path.join(SUMO_HOME, "bin") + os.pathsep + os.environ.get("PATH", "")
    
    # Convert and visualize the 43R bus route area in Istanbul
    osm_file = "data/osm/istanbul_43r.osm"    
    try:
        # Convert to SUMO format
        net_file = convert_to_sumo(osm_file)
        
        # Open in SUMO GUI
        open_in_sumo_gui(net_file)
        
        print("\nInstructions:")
        print("1. In SUMO-GUI, click the 'Play' button to load the network")
        print("2. Use mouse wheel to zoom in/out")
        print("3. Hold right mouse button and drag to rotate")
        print("4. Hold left mouse button and drag to pan")
        print("5. Press 'F9' to show junction names")
        print("6. Press 'F10' to show edge names")
        
    except Exception as e:
        print(f"Error: {e}") 