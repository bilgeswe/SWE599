# Basic Usage Guide

This guide provides detailed instructions for using the Road Network Conversion and Validation Tools.

## 1. Data Fetching

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

## 2. Network Conversion

### OSM to SUMO
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

### SUMO to OpenDRIVE
```bash
# Convert SUMO to OpenDRIVE
python src/converter/sumo_to_xodr.py \
    --sumo-file data/networks/kadikoy.net.xml \
    --output-file data/networks/kadikoy.xodr \
    --geometry.min-radius 5.0 \
    --geometry.max-grade 0.1 \
    --geometry.min-length 1.0
```

## 3. Network Validation

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

## 4. Network Visualization

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

## 5. Configuration

### Network Settings
```ini
[network]
default_speed = 13.89
default_lanewidth = 3.5
junction_priority = 1
traffic_signal_timing = 30
```

### Conversion Settings
```ini
[conversion]
coordinate_system = WGS84
geometry_precision = 0.1
error_tolerance = 0.01
```

### Validation Settings
```ini
[validation]
structure_rules = strict
geometry_tolerance = 0.1
connection_rules = standard
error_threshold = 0.05
```

## 6. Error Handling

### Conversion Errors
```python
try:
    convert_osm_to_sumo("input.osm", "output.net.xml")
except ConversionError as e:
    print(f"Conversion error: {e}")
    # Handle error
```

### Validation Errors
```python
try:
    validator.validate("network.net.xml")
except ValidationError as e:
    print(f"Validation error: {e}")
    # Handle error
```

### Visualization Errors
```python
try:
    visualize_with_folium("network.net.xml", "output.html")
except VisualizationError as e:
    print(f"Visualization error: {e}")
    # Handle error
```

## 7. Best Practices

1. **Data Management**
   - Keep original OSM data
   - Use consistent file naming
   - Document data modifications

2. **Conversion**
   - Validate input data
   - Check conversion settings
   - Verify output format

3. **Validation**
   - Run multiple validation levels
   - Document validation results
   - Address critical issues first

4. **Visualization**
   - Use appropriate visualization type
   - Include relevant metadata
   - Document visualization settings

## Next Steps

1. Explore the [Advanced Usage](Advanced-Usage) guide for more complex scenarios
2. Check out the [Tutorials](Tutorials) section for practical examples
3. Refer to the [API Documentation](API-Documentation) for detailed function descriptions 