# Development Guide

This document provides guidelines for contributing to the project.

## Development Environment Setup

1. **Python Environment**
   ```bash
   # Create virtual environment
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate

   # Install dependencies
   pip install -r requirements.txt
   ```

2. **SUMO Installation**
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

3. **XQuartz Installation (macOS)**
   ```bash
   # Install XQuartz
   brew install --cask xquartz
   # Restart computer after installation
   ```

## Code Style

1. **Python Style Guide**
   - Follow PEP 8 guidelines
   - Use type hints
   - Document all functions and classes
   - Keep functions focused and small

2. **File Organization**
   - One class per file
   - Group related functions
   - Use meaningful names
   - Follow project structure

3. **Documentation**
   - Use docstrings
   - Update README
   - Keep comments current
   - Document changes

## Testing

1. **Test Structure**
   ```python
   def test_function():
       """Test description."""
       # Setup
       input_data = create_test_data()
       
       # Execute
       result = process_data(input_data)
       
       # Verify
       assert result == expected_result
   ```

2. **Test Categories**
   - Unit tests
   - Integration tests
   - Validation tests
   - Performance tests

3. **Running Tests**
   ```bash
   # Run all tests
   python -m pytest

   # Run specific tests
   python -m pytest tests/converter/test_osm_to_sumo.py

   # Run with coverage
   python -m pytest --cov=src
   ```

## Git Workflow

1. **Branching**
   ```bash
   # Create feature branch
   git checkout -b feature/new-feature

   # Create bugfix branch
   git checkout -b fix/bug-description
   ```

2. **Committing**
   ```bash
   # Stage changes
   git add .

   # Commit with message
   git commit -m "Description of changes"
   ```

3. **Pull Requests**
   - Create from feature branch
   - Include description
   - Link related issues
   - Request reviews

## Network Conversion Development

1. **OSM to SUMO**
   ```python
   def convert_osm_to_sumo(osm_file, output_file):
       """Convert OSM to SUMO network."""
       # Load OSM data
       network = load_osm(osm_file)
       
       # Convert to SUMO
       sumo_network = convert_to_sumo(network)
       
       # Save SUMO network
       save_sumo(sumo_network, output_file)
   ```

2. **SUMO to OpenDRIVE**
   ```python
   def convert_sumo_to_opendrive(sumo_file, output_file):
       """Convert SUMO to OpenDRIVE network."""
       # Load SUMO data
       network = load_sumo(sumo_file)
       
       # Convert to OpenDRIVE
       opendrive_network = convert_to_opendrive(network)
       
       # Save OpenDRIVE network
       save_opendrive(opendrive_network, output_file)
   ```

## Visualization Development

1. **SUMO Visualization**
   ```python
   def visualize_in_sumo(network_file):
       """Visualize network in SUMO GUI."""
       # Load network
       network = load_network(network_file)
       
       # Start SUMO GUI
       start_sumo_gui(network)
   ```

2. **Web Visualization**
   ```python
   def visualize_with_folium(network_file):
       """Create interactive web map."""
       # Load network
       network = load_network(network_file)
       
       # Create map
       map = create_map(network)
       
       # Save map
       save_map(map, "output.html")
   ```

## Troubleshooting

1. **Common Issues**
   - SUMO installation problems
   - Coordinate conversion errors
   - Network validation failures
   - Visualization issues

2. **Debugging**
   ```python
   # Enable debug logging
   import logging
   logging.basicConfig(level=logging.DEBUG)
   ```

3. **Performance**
   - Profile code
   - Optimize bottlenecks
   - Use efficient algorithms
   - Cache results

## Resources

1. **Documentation**
   - [SUMO Documentation](https://sumo.dlr.de/docs/)
   - [OpenDRIVE Specification](https://www.asam.net/standards/detail/opendrive/)
   - [OSM Documentation](https://wiki.openstreetmap.org/wiki/Main_Page)

2. **Tools**
   - SUMO GUI
   - JOSM
   - QGIS
   - NetworkX

3. **References**
   - Example networks
   - Test cases
   - Best practices
   - Research papers 