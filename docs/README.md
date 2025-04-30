# Road Network Conversion and Visualization Documentation

## Table of Contents
1. [Project Overview](#project-overview)
2. [File Structure](#file-structure)
3. [Core Files](#core-files)
4. [Example Files](#example-files)
5. [Dependencies](#dependencies)
6. [Usage Guide](#usage-guide)

## Project Overview

This project provides tools for converting and visualizing road network data between different formats (OSM, SUMO, and OpenDRIVE). It includes functionality for downloading road networks, converting between formats, and creating visualizations.

## File Structure

```
.
├── docs/                    # Documentation files
├── src/                    # Source code
│   ├── examples/          # Example scripts
│   └── utils/            # Utility functions
├── data/                  # Data files
│   ├── networks/         # Network files
│   └── plots/           # Generated plots
└── requirements.txt      # Python dependencies
```

## Core Files

### 1. `src/utils/network_converter.py`

**Purpose**: Core conversion utilities between different road network formats.

**Key Functions**:
- `osm_to_sumo(osm_file, output_file)`: Converts OSM data to SUMO network format
- `sumo_to_opendrive(net_file, output_file)`: Converts SUMO network to OpenDRIVE format
- `osm_to_opendrive(osm_file, output_file)`: Direct conversion from OSM to OpenDRIVE

**Usage**:
```python
from src.utils.network_converter import osm_to_sumo

# Convert OSM to SUMO
osm_to_sumo('data/networks/levent.osm', 'data/networks/levent.net.xml')
```

### 2. `src/utils/visualization.py`

**Purpose**: Visualization utilities for road networks.

**Key Functions**:
- `plot_network(network, format_type)`: Creates static plots of road networks
- `create_interactive_map(network, output_file)`: Generates interactive HTML maps
- `compare_networks(network1, network2)`: Visual comparison of two networks

**Usage**:
```python
from src.utils.visualization import plot_network

# Create static plot
plot_network('data/networks/levent.net.xml', 'sumo')
```

## Example Files

### 1. `src/examples/download_network.py`

**Purpose**: Downloads road network data for a specified location.

**Key Functions**:
- `download_and_convert_network(place_name, output_dir)`: Downloads and converts network data

**Usage**:
```bash
python src/examples/download_network.py "Levent, Istanbul, Turkey"
```

**Output**:
- OSM file: `data/networks/levent.osm`
- SUMO network: `data/networks/levent.net.xml`

### 2. `src/examples/visualize_kadikoy.py`

**Purpose**: Creates interactive visualization of Kadıköy's road network.

**Key Functions**:
- `load_network_data()`: Loads network data
- `create_map()`: Creates interactive map
- `add_road_types()`: Adds road types with different colors

**Usage**:
```bash
python src/examples/visualize_kadikoy.py
```

**Output**:
- Interactive HTML map: `data/plots/kadikoy_interactive.html`

### 3. `src/examples/basic_parsing.py`

**Purpose**: Demonstrates basic parsing of different road network formats.

**Key Functions**:
- `parse_osm_basic(osm_file)`: Parses OSM data
- `parse_sumo_basic(net_file)`: Parses SUMO network
- `create_basic_opendrive(roads, output_file)`: Creates OpenDRIVE structure

**Usage**:
```bash
python src/examples/basic_parsing.py
```

**Output**:
- Network statistics
- Basic OpenDRIVE file
- Network visualizations

## Dependencies

Listed in `requirements.txt`:
```
osmnx>=1.0.0
sumolib>=1.0.0
lxml>=4.9.0
matplotlib>=3.5.0
folium>=0.12.0
```

Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage Guide

### 1. Downloading a Road Network

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Download network
python src/examples/download_network.py "Levent, Istanbul, Turkey"
```

### 2. Converting Between Formats

```bash
# OSM to SUMO
python -c "from src.utils.network_converter import osm_to_sumo; osm_to_sumo('data/networks/levent.osm', 'data/networks/levent.net.xml')"

# SUMO to OpenDRIVE
python -c "from src.utils.network_converter import sumo_to_opendrive; sumo_to_opendrive('data/networks/levent.net.xml', 'data/networks/levent.xodr')"
```

### 3. Creating Visualizations

```bash
# Create interactive map
python src/examples/visualize_kadikoy.py

# View the map
open data/plots/kadikoy_interactive.html  # On macOS
# or
start data/plots/kadikoy_interactive.html  # On Windows
```

### 4. Basic Parsing Example

```bash
# Run basic parsing
python src/examples/basic_parsing.py
```

This will:
1. Parse the OSM and SUMO networks
2. Create a basic OpenDRIVE structure
3. Generate visualizations of the networks 