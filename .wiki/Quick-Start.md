# Quick Start Guide

This guide provides a quick overview of how to get started with the Road Network Conversion and Validation Tools.

## 1. Basic Conversion

### OSM to SUMO
```bash
# Convert OSM to SUMO
python src/converter/osm_to_sumo.py \
    --osm-file data/networks/kadikoy.osm \
    --output-file data/networks/kadikoy.net.xml
```

### SUMO to OpenDRIVE
```bash
# Convert SUMO to OpenDRIVE
python src/converter/sumo_to_xodr.py \
    --sumo-file data/networks/kadikoy.net.xml \
    --output-file data/networks/kadikoy.xodr
```

## 2. Network Validation

```python
from src.validator.network_validator import NetworkValidator

# Create validator
validator = NetworkValidator()

# Validate network
result = validator.validate("data/networks/kadikoy.net.xml")

# Get validation report
report = validator.get_report()
```

## 3. Network Visualization

### SUMO GUI
```bash
# Visualize in SUMO GUI
sumo-gui -n data/networks/kadikoy.net.xml
```

### Interactive Map
```python
from src.visualization.visualize_with_folium import visualize_with_folium

# Create interactive map
visualize_with_folium(
    network_file="data/networks/kadikoy.net.xml",
    output_file="data/visualizations/kadikoy.html"
)
```

## 4. Test Networks

### Kadıköy Network
```python
import osmnx as ox

# Fetch Kadıköy network
north, south, east, west = 41.0697, 41.0297, 29.0324, 28.9724
network = ox.graph_from_bbox(north, south, east, west, network_type="drive")
ox.save_graphml(network, "data/networks/kadikoy.osm")
```

### Levent Network
```python
# Fetch Levent network
network = ox.graph_from_place("Levent, Istanbul, Turkey", network_type="drive")
ox.save_graphml(network, "data/networks/levent.osm")
```

## 5. Common Tasks

### Fetching OSM Data
```python
import osmnx as ox

# By place name
network = ox.graph_from_place("Your Location", network_type="drive")

# By bounding box
network = ox.graph_from_bbox(north, south, east, west, network_type="drive")
```

### Converting Networks
```python
from src.converter.osm_to_sumo import convert_osm_to_sumo
from src.converter.sumo_to_xodr import convert_sumo_to_opendrive

# OSM to SUMO
convert_osm_to_sumo("input.osm", "output.net.xml")

# SUMO to OpenDRIVE
convert_sumo_to_opendrive("input.net.xml", "output.xodr")
```

### Validating Networks
```python
from src.validator import NetworkValidator, GeometryValidator

# Network validation
network_validator = NetworkValidator()
network_validator.validate("network.net.xml")

# Geometry validation
geometry_validator = GeometryValidator()
geometry_validator.validate("network.net.xml")
```

## Next Steps

1. Explore the [Basic Usage](Basic-Usage) guide for more detailed instructions
2. Check out the [Tutorials](Tutorials) section for step-by-step examples
3. Refer to the [API Documentation](API-Documentation) for detailed function descriptions 