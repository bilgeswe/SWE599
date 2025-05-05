# Data Fetching Instructions

This document provides detailed instructions for fetching road network data for the project.

## 1. OSM Data Fetching

### Using osmnx
```python
import osmnx as ox

# Fetch network by place name
network = ox.graph_from_place("Kadıköy, Istanbul, Turkey", network_type="drive")

# Fetch network by bounding box
north, south, east, west = 41.0697, 41.0297, 29.0324, 28.9724
network = ox.graph_from_bbox(north, south, east, west, network_type="drive")

# Save as OSM file
ox.save_graphml(network, "data/networks/kadikoy.osm")
```

### Using Overpass API
```python
import requests
import json

# Define query
query = """
[out:json][timeout:25];
(
  way["highway"](41.0297,28.9724,41.0697,29.0324);
  >;
);
out body;
"""

# Fetch data
response = requests.post("https://overpass-api.de/api/interpreter", data=query)
data = response.json()

# Save as OSM file
with open("data/networks/kadikoy.osm", "w") as f:
    json.dump(data, f)
```

## 2. Test Networks

### Kadıköy Network
- **Bounding Box**: 
  - North: 41.0697
  - South: 41.0297
  - East: 29.0324
  - West: 28.9724
- **Characteristics**:
  - Complex urban network
  - Multiple junction types
  - Various road geometries

### Levent Network
- **Bounding Box**: 
  - North: 41.0897
  - South: 41.0497
  - East: 29.0524
  - West: 28.9924
- **Characteristics**:
  - Business district network
  - Regular grid layout
  - Traffic signal systems

### Odunpazarı Network
- **Bounding Box**: 
  - North: 39.7897
  - South: 39.7497
  - East: 30.5324
  - West: 30.4724
- **Characteristics**:
  - Historical district
  - Narrow streets
  - Complex intersections

## 3. 43R Bus Route

### Route Details
- **Start**: Kadıköy
- **End**: Levent
- **Stops**: 25 major stops
- **Length**: ~15 km

### Bounding Box
- North: 41.0697
- South: 41.0297
- East: 29.0324
- West: 28.9724

## 4. Data Processing

### OSM to SUMO Conversion
```bash
# Convert OSM to SUMO
python src/converter/osm_to_sumo.py \
    --osm-file data/networks/kadikoy.osm \
    --output-file data/networks/kadikoy.net.xml \
    --default.speed 13.89 \
    --default.lanewidth 3.5 \
    --junctions.join true \
    --tls.guess true
```

### SUMO to OpenDRIVE Conversion
```bash
# Convert SUMO to OpenDRIVE
python src/converter/sumo_to_xodr.py \
    --sumo-file data/networks/kadikoy.net.xml \
    --output-file data/networks/kadikoy.xodr \
    --geometry.min-radius 5.0 \
    --geometry.max-grade 0.1 \
    --geometry.min-length 1.0
```

## 5. Data Validation

### Network Structure Validation
```python
from src.validator.network_validator import NetworkValidator

# Create validator
validator = NetworkValidator()

# Validate network
result = validator.validate("data/networks/kadikoy.net.xml")

# Get validation report
report = validator.get_report()
```

### Geometry Validation
```python
from src.validator.geometry_validator import GeometryValidator

# Create validator
validator = GeometryValidator()

# Validate geometry
result = validator.validate("data/networks/kadikoy.net.xml")

# Get validation report
report = validator.get_report()
```

## 6. Data Storage

### Directory Structure
```
data/
├── networks/         # Network files
│   ├── kadikoy/     # Kadıköy network
│   ├── levent/      # Levent network
│   └── odunpazari/  # Odunpazarı network
├── visualizations/   # Visualization outputs
└── plots/           # Static plots
```

### File Naming Convention
- OSM files: `{location}.osm`
- SUMO networks: `{location}.net.xml`
- OpenDRIVE files: `{location}.xodr`
- Visualizations: `{location}_{type}.html`

## 7. Notes

- Always validate data after fetching
- Keep original OSM data for reference
- Document any data modifications
- Use consistent coordinate systems
- Maintain data version control 