# Terminal Instructions

This document provides clear, step-by-step terminal commands for common operations.

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
python3 -m venv .venv

# Activate virtual environment
# On macOS/Linux:
source .venv/bin/activate
# On Windows:
.venv\Scripts\activate
```

### 3. Install Dependencies
```bash
# Install required packages
pip install -r requirements.txt

# Install development dependencies
pip install -e ".[dev]"
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

## Network Operations

### 1. Convert OSM to SUMO
```bash
# Convert network
python src/converter/osm_to_sumo.py data/networks/kadıköy.osm data/networks/kadıköy.net.xml

# Convert with additional options
python src/converter/osm_to_sumo.py data/networks/kadıköy.osm data/networks/kadıköy.net.xml --geometry.remove --roundabouts.guess
```

### 2. Convert SUMO to OpenDRIVE
```bash
# Convert network
python src/converter/sumo_to_xodr.py data/networks/kadıköy.net.xml data/networks/kadıköy.xodr

# Convert with validation
python src/converter/advanced_sumo_to_xodr.py --validate data/networks/kadıköy.net.xml
```

### 3. Visualize Networks
```bash
# Using SUMO GUI
sumo-gui -n data/networks/kadıköy.net.xml

# Using interactive visualization
python src/visualization/visualize_with_folium.py data/networks/kadıköy.osm
```

## Testing and Validation

### 1. Run Tests
```bash
# Run all tests
python -m unittest discover tests

# Run specific test file
python -m unittest tests/test_network_validation.py

# Run with coverage
coverage run -m unittest discover tests
coverage report
```

### 2. Validate Networks
```bash
# Validate SUMO network
python src/converter/advanced_sumo_to_xodr.py --validate data/networks/kadıköy.net.xml

# Validate OpenDRIVE network
python src/converter/advanced_sumo_to_xodr.py --validate-opendrive data/networks/kadıköy.xodr
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
python -m cProfile -o profile.out src/converter/osm_to_sumo.py data/networks/kadıköy.osm data/networks/kadıköy.net.xml

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
python src/utils/format_parsing.py data/networks/kadıköy.net.xml

# Validate network structure
python src/converter/advanced_sumo_to_xodr.py --validate-structure data/networks/kadıköy.net.xml
```

### 3. Visualization Issues
```bash
# Check XQuartz connection (macOS)
echo $DISPLAY

# Test SUMO GUI
sumo-gui --version

# Check network visualization
python src/visualization/visualize_in_sumo.py data/networks/kadıköy.net.xml
```

## Notes

- All commands assume you're in the project root directory
- Use `PYTHONPATH=$PYTHONPATH:.` when running Python scripts
- Make sure your virtual environment is activated
- Check the documentation for more detailed instructions 