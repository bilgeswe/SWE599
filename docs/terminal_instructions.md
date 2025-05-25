# Terminal Instructions

This document provides clear, step-by-step terminal commands for common operations.

## Pipeline Overview

The project provides a streamlined pipeline for processing road networks. You can run the entire pipeline with a single command:

```bash
# Run the complete pipeline for a location
python run_pipeline.py "Kadıköy, Istanbul, Turkey"
```

The pipeline executes the following steps in sequence:

1. **Download OSM Data**
   - Downloads OpenStreetMap data for the specified location
   - Saves to `data/osm/{location}__{city}__{country}.osm`

2. **Convert to SUMO**
   - Converts OSM data to SUMO network format
   - Saves to `data/sumo/{location}__{city}__{country}.net.xml`

3. **Detect Network Issues**
   - Analyzes the SUMO network for potential problems
   - Checks for disconnected edges, sharp turns, etc.
   - Outputs detailed issue report

4. **Convert to OpenDRIVE**
   - Converts SUMO network to OpenDRIVE format
   - Saves to `data/opendrive/{location}__{city}__{country}.xodr`

5. **Generate Visualizations**
   - Creates HTML visualization
   - Generates PNG plots
   - Saves to `visualization/html/` and `plots/` directories

### Pipeline Options

You can also run individual steps of the pipeline:

```bash
# Download OSM data only
python src/osm_fetcher/fetcher.py "Kadıköy, Istanbul, Turkey"

# Convert OSM to SUMO only
python src/converter/osm_to_sumo.py data/osm/kadıköy__istanbul__turkey.osm data/sumo/kadıköy__istanbul__turkey.net.xml

# Detect network issues only
python src/converter/network_issue_detector.py data/sumo/kadıköy__istanbul__turkey.net.xml

# Convert to OpenDRIVE only
python src/converter/advanced_sumo_to_xodr.py data/sumo/kadıköy__istanbul__turkey.net.xml data/opendrive/kadıköy__istanbul__turkey.xodr
```

### Pipeline Output

The pipeline generates the following files:
- OSM data: `data/osm/{location}__{city}__{country}.osm`
- SUMO network: `data/sumo/{location}__{city}__{country}.net.xml`
- OpenDRIVE file: `data/opendrive/{location}__{city}__{country}.xodr`
- HTML visualization: `visualization/html/{location}__{city}__{country}.html`
- PNG plots: `plots/{location}__{city}__{country}.png`

## Project Setup

### 1. Clone the Repository
```bash
# Navigate to your desired directory
cd ~/Desktop

# Clone the repository
git clone https://github.com/yourusername/SWE599.git

# Navigate into the project directory
cd SWE599
```

### 2. Create and Activate Virtual Environment
```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate
```

### 3. Install Dependencies
```bash
# Install required packages
pip install -r requirements.txt
```

### 4. Install SUMO
```bash
# On macOS
brew install sumo

# On Ubuntu
sudo apt-get install sumo

# On Windows
# Download from https://sumo.dlr.de/docs/Downloads.php
```

### 5. Install XQuartz (macOS only)
```bash
# Install XQuartz
brew install --cask xquartz

# Restart your computer after installation
```

### 6. XQuartz Setup and Usage
```bash
# Start XQuartz
open -a XQuartz

# Set DISPLAY environment variable
export DISPLAY=:0

# Test XQuartz connection
xeyes  # Should show a pair of eyes following your cursor
```

Common XQuartz Applications:
1. **SUMO GUI**
   ```bash
   # Launch SUMO GUI
   sumo-gui -n data/sumo/kadıköy__istanbul__turkey.net.xml
   ```

2. **Network Visualization**
   ```bash
   # View network in SUMO
   sumo-gui -n data/sumo/kadıköy__istanbul__turkey.net.xml
   
   # View with traffic simulation
   sumo-gui -n data/sumo/kadıköy__istanbul__turkey.net.xml -r data/sumo/kadıköy__istanbul__turkey.rou.xml
   ```

3. **Debug Visualization**
   ```bash
   # View network with debug information
   sumo-gui -n data/sumo/kadıköy__istanbul__turkey.net.xml --gui-settings-file debug.settings.xml
   ```

Opening SUMO Files:
1. **Basic Network View**
   ```bash
   # Open a SUMO network file
   sumo-gui -n data/sumo/kadıköy__istanbul__turkey.net.xml
   ```

2. **With Traffic Simulation**
   ```bash
   # Open network with route file
   sumo-gui -n data/sumo/kadıköy__istanbul__turkey.net.xml -r data/sumo/kadıköy__istanbul__turkey.rou.xml
   ```

3. **With Configuration**
   ```bash
   # Open with specific configuration
   sumo-gui -c data/sumo/kadıköy__istanbul__turkey.sumocfg
   ```

4. **With Additional Options**
   ```bash
   # Open with specific viewport
   sumo-gui -n data/sumo/kadıköy__istanbul__turkey.net.xml --viewport 41.0497,29.0024,41.0697,29.0324
   
   # Open with specific delay
   sumo-gui -n data/sumo/kadıköy__istanbul__turkey.net.xml --delay 100
   ```

SUMO GUI Controls:
- **Zoom**: Mouse wheel or +/- keys
- **Pan**: Middle mouse button or arrow keys
- **Select**: Left mouse button
- **Inspect**: Right-click on elements
- **Start/Stop**: Space bar
- **Step**: S key
- **Save View**: Ctrl+S

Troubleshooting XQuartz:
1. If applications don't open:
   ```bash
   # Check XQuartz is running
   ps aux | grep XQuartz
   
   # Verify DISPLAY variable
   echo $DISPLAY
   
   # Restart XQuartz
   killall XQuartz
   open -a XQuartz
   ```

2. If you see "cannot connect to X server":
   ```bash
   # Reset DISPLAY variable
   export DISPLAY=:0
   
   # Check XQuartz permissions
   xhost +  # Allow connections from localhost
   ```

3. If SUMO GUI is slow:
   ```bash
   # Launch with reduced graphics
   sumo-gui -n data/sumo/kadıköy__istanbul__turkey.net.xml --no-internal-links
   ```

## Network Operations

### 1. Download and Convert OSM Data
```bash
# Download OSM data for a location
python src/osm_fetcher/fetcher.py "Kadıköy, Istanbul, Turkey"

# Convert OSM to SUMO
python src/converter/osm_to_sumo.py data/osm/kadıköy__istanbul__turkey.osm data/sumo/kadıköy__istanbul__turkey.net.xml
```

### 2. Convert SUMO to OpenDRIVE
```bash
# Convert SUMO to OpenDRIVE
python src/converter/advanced_sumo_to_xodr.py data/sumo/kadıköy__istanbul__turkey.net.xml data/opendrive/kadıköy__istanbul__turkey.xodr
```

OpenDRIVE Format:
The OpenDRIVE format (.xodr) is a standardized road network description format used in automotive simulation. It includes:

1. **Road Elements**
   - Road geometry (straight, curved, spiral)
   - Lane configurations
   - Road markings
   - Elevation profiles

2. **Junction Elements**
   - Intersection geometry
   - Connection rules
   - Traffic signals
   - Priority rules

3. **Additional Features**
   - Traffic signs
   - Road objects
   - Surface properties
   - Weather conditions

Example OpenDRIVE Structure:
```xml
<?xml version="1.0" encoding="UTF-8"?>
<OpenDRIVE>
  <road name="Bağdat Caddesi" length="100.0" id="1" junction="-1">
    <link>
      <predecessor elementType="road" elementId="2"/>
      <successor elementType="road" elementId="3"/>
    </link>
    <planView>
      <geometry x="0.0" y="0.0" hdg="0.0" length="100.0">
        <line/>
      </geometry>
    </planView>
    <lanes>
      <laneSection s="0.0">
        <left>
          <lane id="1" type="driving" level="false">
            <width sOffset="0.0" a="3.5" b="0.0" c="0.0" d="0.0"/>
          </lane>
        </left>
        <center>
          <lane id="0" type="none" level="false"/>
        </center>
        <right>
          <lane id="-1" type="driving" level="false">
            <width sOffset="0.0" a="3.5" b="0.0" c="0.0" d="0.0"/>
          </lane>
        </right>
      </laneSection>
    </lanes>
  </road>
</OpenDRIVE>
```

### 3. Visualize Networks
```bash
# Using SUMO GUI
sumo-gui -n data/sumo/kadıköy__istanbul__turkey.net.xml

# Using interactive visualization
python src/visualization/visualize_with_folium.py data/osm/kadıköy__istanbul__turkey.osm

# Generate static visualization
python src/visualization/visualize_network.py data/osm/kadıköy__istanbul__turkey.osm
```

## Testing and Validation

### 1. Run Tests
```bash
# Run all tests
python -m pytest tests/

# Run specific test file
python -m pytest tests/test_network_validation.py

# Run with coverage
python -m pytest --cov=src tests/
```

### 2. Validate Networks
```bash
# Detect network issues
python src/converter/network_issue_detector.py data/sumo/kadıköy__istanbul__turkey.net.xml

# Validate OpenDRIVE network
python src/converter/advanced_sumo_to_xodr.py --validate-opendrive data/opendrive/kadıköy__istanbul__turkey.xodr
```

## Development Tools

### 1. Code Formatting
```bash
# Format code
black src/ tests/

# Sort imports
isort src/ tests/

# Check types
mypy src/ tests/
```

### 2. Documentation
```bash
# Generate API documentation
pdoc --html src/

# Check documentation coverage
interrogate src/
```

### 3. Performance Profiling
```bash
# Profile network conversion
python -m cProfile -o profile.out src/converter/osm_to_sumo.py data/osm/kadıköy__istanbul__turkey.osm data/sumo/kadıköy__istanbul__turkey.net.xml

# Analyze profile
python -m pstats profile.out
```

## Troubleshooting

### 1. Common Issues
```bash
# Check SUMO installation
sumo --version

# Check Python environment
python -c "import sumolib; print(sumolib.__version__)"

# Check XQuartz (macOS)
xquartz --version
```

### 2. Network Issues
```bash
# Check network file
python src/converter/network_issue_detector.py data/sumo/kadıköy__istanbul__turkey.net.xml

# Validate network structure
python src/converter/advanced_sumo_to_xodr.py --validate-structure data/sumo/kadıköy__istanbul__turkey.net.xml
```

### 3. Visualization Issues
```bash
# Check XQuartz connection (macOS)
echo $DISPLAY

# Test SUMO GUI
sumo-gui --version

# Check network visualization
python src/visualization/visualize_in_sumo.py data/sumo/kadıköy__istanbul__turkey.net.xml
```

## Notes

- All commands assume you're in the project root directory
- Use `PYTHONPATH=$PYTHONPATH:.` when running Python scripts
- Make sure your virtual environment is activated
- Check the documentation for more detailed instructions 