#!/usr/bin/env bash -e

# Levent, Istanbul coordinates (approximately)
# bbox = min_lon,min_lat,max_lon,max_lat
# Levent area: 29.0088,41.0751,29.0228,41.0851

# Download Levent area directly from Overpass API
curl -o levent.osm "https://overpass-api.de/api/map?bbox=29.0088,41.0751,29.0228,41.0851"

# Extract the roads from the OpenStreetMap data
osmium tags-filter --overwrite levent.osm w/highway=primary -o levent-roads.osm.pbf

# Convert to the textual OSM format
osmium cat --overwrite levent-roads.osm.pbf -o levent.osm

# Convert to the OpenDrive format
netconvert --osm.elevation true --osm-files levent.osm --opendrive-output levent.xodr