# Data Fetching Instructions

This document provides detailed instructions for fetching road network data for the project.

## 1. OSM Data Fetching

### Using the Fetcher Script
```bash
# Fetch network by place name
python src/osm_fetcher/fetcher.py "Kadıköy, Istanbul, Turkey"

# The script will:
# 1. Download OSM data for the specified location
# 2. Save it to data/osm/kadıköy__istanbul__turkey.osm
# 3. Validate the downloaded data
```

### Using osmnx (Alternative Method)
```python
import osmnx as ox

# Fetch network by place name
network = ox.graph_from_place("Kadıköy, Istanbul, Turkey", network_type="drive")

# Fetch network by bounding box
north, south, east, west = 41.0697, 41.0297, 29.0324, 28.9724
network = ox.graph_from_bbox(north, south, east, west, network_type="drive")

# Save as OSM file
ox.save_graphml(network, "data/osm/kadıköy__istanbul__turkey.osm")
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

## 3. Data Processing

### OSM to SUMO Conversion
```bash
# Convert OSM to SUMO
python src/converter/osm_to_sumo.py \
    data/osm/kadıköy__istanbul__turkey.osm \
    data/sumo/kadıköy__istanbul__turkey.net.xml
```

### SUMO to OpenDRIVE Conversion
```bash
# Convert SUMO to OpenDRIVE
python src/converter/advanced_sumo_to_xodr.py \
    data/sumo/kadıköy__istanbul__turkey.net.xml \
    data/opendrive/kadıköy__istanbul__turkey.xodr
```

## 4. Data Validation

### Network Issue Detection
```bash
# Detect network issues
python src/converter/network_issue_detector.py data/sumo/kadıköy__istanbul__turkey.net.xml
```

### OpenDRIVE Validation
```bash
# Validate OpenDRIVE network
python src/converter/advanced_sumo_to_xodr.py --validate-opendrive data/opendrive/kadıköy__istanbul__turkey.xodr
```

## 5. Data Storage

### Directory Structure
```
data/
├── osm/            # OSM data files
├── sumo/           # SUMO network files
├── opendrive/      # OpenDRIVE files
├── visualizations/ # Visualization outputs
└── plots/          # Static plots
```

### File Naming Convention
- OSM files: `{location}__{city}__{country}.osm`
- SUMO networks: `{location}__{city}__{country}.net.xml`
- OpenDRIVE files: `{location}__{city}__{country}.xodr`
- Visualizations: `{location}__{city}__{country}.html`
- Plots: `{location}__{city}__{country}.png`

## 6. Notes

- Always validate data after fetching
- Keep original OSM data for reference
- Document any data modifications
- Use consistent coordinate systems
- Maintain data version control 