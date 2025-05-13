### Stage 1:
<img width="730" alt="Ekran Resmi 2025-05-05 03 44 07" src="https://github.com/user-attachments/assets/187a7779-5403-406a-922d-caef0fea37a0" />
<br/>

### Stage 2:
<img width="1235" alt="Ekran Resmi 2025-05-05 03 43 19" src="https://github.com/user-attachments/assets/84c0671a-e2fc-47c5-a60e-4ce8169e000e" />
<br/>

# Road Network Conversion and Validation System
A comprehensive system for converting and validating road network formats between OSM, SUMO, and OpenDRIVE.

## Features

- **Network Conversion**
  - OSM to SUMO conversion
  - SUMO to OpenDRIVE conversion
  - Advanced conversion options
  - Error handling and logging

- **Network Validation**
  - Structure validation
  - Geometry validation
  - Connection validation
  - Traffic signal validation

- **Visualization**
  - SUMO GUI visualization
  - Interactive web maps
  - Network comparison
  - Error visualization

## Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd <project-directory>
   ```

2. **Set up Python environment**
   ```bash
   # Create virtual environment
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate

   # Install dependencies
   pip install -r requirements.txt
   ```

3. **Install SUMO**
   ```bash
   # macOS
   brew install sumo

   # Ubuntu
   sudo add-apt-repository ppa:sumo/stable
   sudo apt-get update
   sudo apt-get install sumo sumo-tools

   # Windows
   # Download installer from https://sumo.dlr.de/docs/Downloads.php
   ```

4. **Install XQuartz (macOS)**
   ```bash
   brew install --cask xquartz
   # Restart computer after installation
   ```

## Usage

### 1. Network Conversion

#### OSM to SUMO
```python
from src.converter.osm_to_sumo import convert_osm_to_sumo

# Convert OSM to SUMO
convert_osm_to_sumo(
    osm_file="data/networks/kadikoy.osm",
    output_file="data/networks/kadikoy.net.xml",
    additional_options=[
        "--default.speed=13.89",
        "--default.lanewidth=3.5",
        "--junctions.join=true",
        "--tls.guess=true"
    ]
)
```

#### SUMO to OpenDRIVE
```python
from src.converter.sumo_to_xodr import convert_sumo_to_opendrive

# Convert SUMO to OpenDRIVE
convert_sumo_to_opendrive(
    sumo_file="data/networks/kadikoy.net.xml",
    output_file="data/networks/kadikoy.xodr",
    additional_options=[
        "--geometry.min-radius=5.0",
        "--geometry.max-grade=0.1",
        "--geometry.min-length=1.0"
    ]
)
```

### 2. Network Validation

```python
from src.validator.network_validator import NetworkValidator

# Create validator
validator = NetworkValidator()

# Validate network
result = validator.validate("data/networks/kadikoy.net.xml")

# Get validation report
report = validator.get_report()
```

### 3. Network Visualization

#### SUMO GUI
```python
from src.visualization.visualize_in_sumo import visualize_in_sumo

# Visualize in SUMO GUI
visualize_in_sumo("data/networks/kadikoy.net.xml")
```

#### Web Map
```python
from src.visualization.visualize_with_folium import visualize_with_folium

# Create interactive web map
visualize_with_folium(
    network_file="data/networks/kadikoy.net.xml",
    output_file="data/visualizations/kadikoy.html"
)
```

## Project Structure

```
project/
├── src/
│   ├── converter/         # Conversion tools
│   │   ├── osm_to_sumo.py
│   │   ├── sumo_to_xodr.py
│   │   └── advanced_sumo_to_xodr.py
│   ├── validator/         # Validation tools
│   │   ├── network_validator.py
│   │   ├── junction_validator.py
│   │   └── geometry_validator.py
│   ├── visualization/     # Visualization tools
│   │   ├── visualize_in_sumo.py
│   │   └── visualize_with_folium.py
│   └── utils/            # Utility functions
│       ├── coordinate_converter.py
│       └── network_utils.py
├── tests/
│   ├── converter/        # Conversion tests
│   ├── validator/        # Validation tests
│   └── visualization/    # Visualization tests
├── data/
│   ├── networks/         # Network files
│   └── visualizations/   # Visualization outputs
└── docs/                 # Documentation
```

## Development

### Running Tests
```bash
# Run all tests
python -m pytest

# Run specific tests
python -m pytest tests/converter/test_osm_to_sumo.py

# Run with coverage
python -m pytest --cov=src
```

### Code Style
- Follow PEP 8 guidelines
- Use type hints
- Document all functions and classes
- Keep functions focused and small

### Git Workflow
1. Create feature branch
2. Make changes
3. Run tests
4. Create pull request

## Documentation

- [Format Specifications](docs/format_specifications.md)
- [API Reference](docs/api_reference.md)
- [Development Guide](docs/development_guide.md)
- [Architecture](docs/architecture.md)

## Acknowledgments

- [SUMO](https://sumo.dlr.de/docs/)
- [OpenDRIVE](https://www.asam.net/standards/detail/opendrive/)
- [OpenStreetMap](https://www.openstreetmap.org/)

## 📌 Project Status

### ✅ Completed Features
- OSM data collection and parsing
- SUMO network conversion and validation
- Basic OpenDRIVE conversion
- Network visualization tools
- Test coverage for core functionality

### 🚧 In Progress
- Advanced OpenDRIVE conversion features
- Complex road network handling
- Traffic signal timing conversion
- Elevation profile support

### 📋 Planned Features
- Road markings and signs conversion
- Lane-specific properties
- Complex junction handling
- Performance optimization

## 📌 Project Goals

- Use OpenStreetMap (OSM) API to gather real-world road data
- Convert OSM data to SUMO Net using netconvert
- Write a Python script to convert SUMO Net to OpenDRIVE format
- Develop basic AV algorithms to test on the OpenDRIVE map
- Focus on map-based simulation structure and testing

## 📅 Timeline & Phases

### ✅ Phase 1: Environment Setup & Exploration
**Objectives:**
- Set up development environment
- Explore OSM, SUMO, and OpenDRIVE formats

**Tasks:**
- [ ] Install Python & required libraries: osmnx, requests, xml, etc.
- [ ] Install SUMO and verify netconvert tool
- [ ] Review .osm (XML), SUMO .net.xml, and OpenDRIVE .xodr formats

### 🌐 Phase 2: OSM Data Collection via API
**Objectives:**
- Use Overpass API or osmnx to scrape road network data

**Tasks:**
- [ ] Select region of interest (city or custom bounding box)
- [ ] Retrieve and save .osm road data

### 🔁 Phase 3: Convert OSM → SUMO Net → OpenDRIVE
**Objectives:**
- Build conversion pipeline from real-world data to OpenDRIVE format

**Tasks:**
- [ ] Use SUMO's netconvert to convert .osm → .net.xml
- [ ] Explore existing tools to convert SUMO Net → OpenDRIVE
- [ ] Write custom Python script to parse SUMO XML and build .xodr
- [ ] Validate resulting OpenDRIVE file

### 🤖 Phase 4: AV Algorithm Development
**Objectives:**
- Simulate AV logic on OpenDRIVE map structure

**Tasks:**
- [ ] Design algorithms (lane following, routing, stoplight behavior)
- [ ] Apply logic on OpenDRIVE map data
- [ ] Output simulated behavior (paths, decisions, logs)

### 📘 Phase 5: Documentation & Final Report
**Objectives:**
- Prepare full documentation and final report

**Tasks:**
- [ ] Complete technical documentation
- [ ] Write final report
- [ ] Create visualizations and demos
- [ ] Present findings

## ⚙️ Tools and Libraries

- OpenStreetMap API / Overpass API
- osmnx – OSM data extraction with Python
- SUMO + netconvert – Create traffic networks
- Python – Scripting and conversion logic
- OpenDRIVE – Standardized road format

## 📂 Repository Structure

```
.
├── data/
│   ├── networks/     # OSM and SUMO network files
│   ├── visualizations/ # Network visualizations
│   └── plots/        # Static network plots
├── src/
│   ├── converter/    # Conversion pipeline
│   │   ├── advanced_sumo_to_xodr.py
│   │   ├── osm_to_sumo.py
│   │   └── sumo_to_xodr.py
│   ├── visualization/ # Visualization tools
│   └── utils/        # Utility functions
├── tests/            # Unit tests
├── docs/             # Documentation
├── requirements.txt  # Python dependencies
└── README.md        # Project documentation
```

## 🚀 Getting Started

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Install SUMO:
```bash
# On macOS
brew install sumo

# On Ubuntu
sudo apt-get install sumo
```

3. Convert OSM to SUMO:
```bash
python src/converter/osm_to_sumo.py data/networks/kadıköy.osm data/networks/kadıköy.net.xml
```

4. Visualize the network:
```bash
# Using SUMO GUI
sumo-gui -n data/networks/kadıköy.net.xml

# Using interactive visualization
python src/visualization/visualize_with_folium.py data/networks/kadıköy.osm
```

## 🚌 Test Networks

The project includes several test networks:

1. **Kadıköy, Istanbul**
   - Complex urban network
   - Multiple junction types
   - Various road geometries

2. **Levent, Istanbul**
   - Business district network
   - Regular grid layout
   - Traffic signal systems

3. **Odunpazarı, Eskişehir**
   - Historical district
   - Narrow streets
   - Complex intersections

## 📚 Documentation

- [Format Specifications](docs/format_specifications.md)
- [Conversion Pipeline](docs/conversion_pipeline.md)
- [Visualization Guide](docs/visualization_guide.md)


