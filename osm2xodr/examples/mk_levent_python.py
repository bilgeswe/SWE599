#!/usr/bin/env python3

import os
import subprocess

# Download Levent area directly from Overpass API
os.system('curl -o levent.osm "https://overpass-api.de/api/map?bbox=29.0088,41.0751,29.0228,41.0851"')

# Convert OSM to SUMO network using netconvert
try:
    subprocess.run([
        "netconvert",
        "--osm-files", "levent.osm",
        "--output-file", "levent.net.xml",
        "--geometry.remove",
        "--roundabouts.guess",
        "--ramps.guess",
        "--junctions.join",
        "--tls.guess-signals",
        "--tls.discard-simple",
        "--tls.join"
    ], check=True)
    print("Conversion complete! Network saved as levent.net.xml")
except subprocess.CalledProcessError as e:
    print(f"Error during conversion: {e}")
    print("Make sure netconvert is in your PATH and all dependencies are installed") 