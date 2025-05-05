# Network Conversion and Visualization Guide

This guide provides step-by-step instructions for converting and visualizing road networks.

## 1. Prerequisites

Before starting, ensure you have:

1. Python 3.8+ installed
2. SUMO installed and configured
3. Required Python packages:
```bash
pip install -r requirements.txt
```

## 2. Network Conversion

### Converting OSM to SUMO

```bash
# Convert Kadıköy network
python src/converter/osm_to_sumo.py data/networks/kadıköy.osm data/networks/kadıköy.net.xml

# Convert Levent network
python src/converter/osm_to_sumo.py data/networks/levent.osm data/networks/levent.net.xml

# Convert Odunpazarı network
python src/converter/osm_to_sumo.py data/networks/odunpazarı.osm data/networks/odunpazarı.net.xml
```

### Converting SUMO to OpenDRIVE

```bash
# Convert Kadıköy network
python src/converter/sumo_to_xodr.py data/networks/kadıköy.net.xml data/networks/kadıköy.xodr

# Convert Levent network
python src/converter/sumo_to_xodr.py data/networks/levent.net.xml data/networks/levent.xodr

# Convert Odunpazarı network
python src/converter/sumo_to_xodr.py data/networks/odunpazarı.net.xml data/networks/odunpazarı.xodr
```

## 3. Network Visualization

### Using SUMO GUI

```bash
# View Kadıköy network
sumo-gui -n data/networks/kadıköy.net.xml

# View Levent network
sumo-gui -n data/networks/levent.net.xml

# View Odunpazarı network
sumo-gui -n data/networks/odunpazarı.net.xml
```

### Using Interactive Visualization

```bash
# Create interactive visualization for Kadıköy
python src/visualization/visualize_with_folium.py data/networks/kadıköy.osm

# Create interactive visualization for Levent
python src/visualization/visualize_with_folium.py data/networks/levent.osm

# Create interactive visualization for Odunpazarı
python src/visualization/visualize_with_folium.py data/networks/odunpazarı.osm
```

## 4. Network Validation

### Running Tests

```bash
# Run all tests
python -m unittest discover tests

# Run specific test file
python -m unittest tests/test_network_validation.py
```

### Validating Networks

```bash
# Validate Kadıköy network
python src/converter/advanced_sumo_to_xodr.py --validate data/networks/kadıköy.net.xml

# Validate Levent network
python src/converter/advanced_sumo_to_xodr.py --validate data/networks/levent.net.xml

# Validate Odunpazarı network
python src/converter/advanced_sumo_to_xodr.py --validate data/networks/odunpazarı.net.xml
```

## 5. Expected Output

After running all commands, you should have:

1. Network files in `data/networks/`:
   - `*.osm` - Original OSM files
   - `*.net.xml` - SUMO network files
   - `*.xodr` - OpenDRIVE files

2. Visualizations in `data/visualizations/`:
   - `*_interactive.html` - Interactive network maps
   - `*_network.png` - Static network plots

## Notes

- Make sure you're in your project's root directory before running commands
- Ensure your Python virtual environment is activated
- All paths are relative to the project root directory
- The conversion process might take a few minutes for large networks
- Interactive visualizations can be opened in any modern web browser
- SUMO GUI requires XQuartz on macOS 