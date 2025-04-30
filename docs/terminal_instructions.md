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
# Install development dependencies
pip install -e ".[dev]"

# Install required packages
pip install osmnx networkx lxml numpy matplotlib
```

## Data Operations

### 1. Download Road Network Data
```bash
# Download by place name
python src/examples/download_network.py "Place Name, Country"

# Example for Odunpazarı, Eskişehir:
python src/examples/download_network.py "Odunpazarı, Eskişehir, Turkey"

# Download by coordinates
python src/examples/download_by_coordinates.py min_lat max_lat min_lon max_lon

# Example for specific area:
python src/examples/download_by_coordinates.py 39.7 39.8 30.4 30.6
```

### 2. Validate OpenDRIVE Files
```bash
# Validate a single file
python src/validator/validate_opendrive.py data/output/your_file.xodr

# Compare two files
python src/validator/compare_opendrive.py file1.xodr file2.xodr
```

### 3. View Generated Files
```bash
# List downloaded files
ls -l data/

# View OSM file
cat data/input/your_file.osm | less

# View SUMO network file
cat data/output/your_file.net.xml | less

# View OpenDRIVE file
cat data/output/your_file.xodr | less
```

## Testing

### 1. Run All Tests
```bash
# Run all tests
pytest tests/

# Run with coverage report
pytest tests/ --cov=src --cov-report=term-missing
```

### 2. Run Specific Test Files
```bash
# Run conversion tests
pytest tests/test_sumo_to_xodr.py

# Run validation tests
pytest tests/test_validator.py

# Run visualization tests
pytest tests/test_visualization.py
```

### 3. Run Specific Test Functions
```bash
# Run a specific test function
pytest tests/test_sumo_to_xodr.py::test_specific_function

# Run tests matching a pattern
pytest -k "pattern" tests/
```

## Development

### 1. Code Formatting
```bash
# Format code using black
black src/

# Check code style
flake8 src/
```

### 2. Type Checking
```bash
# Run mypy type checking
mypy src/
```

### 3. Documentation
```bash
# Generate documentation
cd docs
make html
```

## Common Issues and Solutions

### 1. Virtual Environment Issues
```bash
# If activation fails
deactivate  # Deactivate current environment
rm -rf .venv  # Remove old environment
python3 -m venv .venv  # Create new environment
source .venv/bin/activate  # Activate new environment
```

### 2. Dependency Issues
```bash
# Update pip
pip install --upgrade pip

# Reinstall dependencies
pip uninstall -r requirements.txt
pip install -r requirements.txt
```

### 3. Test Issues
```bash
# Clear pytest cache
pytest --cache-clear

# Run tests in verbose mode
pytest -v tests/
```

## File Management

### 1. Clean Up Generated Files
```bash
# Remove all generated files
rm -rf data/output/*
rm -rf data/plots/*

# Remove specific file types
find data/ -name "*.xodr" -type f -delete
find data/ -name "*.net.xml" -type f -delete
```

### 2. Backup Important Files
```bash
# Create backup directory
mkdir -p backups

# Backup specific files
cp data/input/important.osm backups/
cp data/output/important.xodr backups/
```

## Notes

1. Always activate the virtual environment before running commands
2. Use `python3` explicitly if you have multiple Python versions
3. Add `-v` flag to any command for verbose output
4. Use `--help` flag to see available options for any command
5. Press `Ctrl+C` to stop any running command
6. Use `| less` to view long outputs page by page 