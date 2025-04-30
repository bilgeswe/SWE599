# Installation Guide

This guide provides detailed instructions for installing and setting up the Road Network Conversion and Validation Tools.

## Prerequisites

Before installing the tools, ensure you have the following:

- Python 3.8 or higher
- Git
- Virtual environment (recommended)
- Basic understanding of command line operations

## Installation Steps

### 1. Clone the Repository

```bash
# Navigate to your desired directory
cd ~/Desktop

# Clone the repository
git clone https://github.com/yourusername/SWE599.git

# Navigate into the project directory
cd SWE599
```

### 2. Set Up Virtual Environment

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

### 4. Verify Installation

```bash
# Check Python version
python --version

# Verify package installation
pip list | grep -E "osmnx|networkx|lxml|numpy|matplotlib"

# Run basic test
pytest tests/test_basic.py
```

## Platform-Specific Instructions

### macOS

1. Install Homebrew if not already installed:
   ```bash
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   ```

2. Install Python and Git:
   ```bash
   brew install python git
   ```

### Windows

1. Install Python from [python.org](https://www.python.org/downloads/)
2. Install Git from [git-scm.com](https://git-scm.com/download/win)
3. Add Python and Git to PATH during installation

### Linux (Ubuntu/Debian)

```bash
# Install required packages
sudo apt update
sudo apt install python3 python3-pip python3-venv git
```

## Common Installation Issues

### 1. Python Version Issues

If you have multiple Python versions installed:
```bash
# Specify Python version explicitly
python3.8 -m venv .venv
```

### 2. Virtual Environment Issues

If virtual environment activation fails:
```bash
# Deactivate current environment
deactivate

# Remove old environment
rm -rf .venv

# Create new environment
python3 -m venv .venv

# Activate new environment
source .venv/bin/activate
```

### 3. Dependency Installation Issues

If package installation fails:
```bash
# Update pip
pip install --upgrade pip

# Clear pip cache
pip cache purge

# Reinstall dependencies
pip install -r requirements.txt
```

## Post-Installation Configuration

### 1. Set Up Configuration File

Create `config.ini` in the project root:
```ini
[general]
log_level = INFO
data_dir = data/

[validation]
tolerance = 0.1
max_road_length = 10000.0

[visualization]
plot_width = 800
plot_height = 600
```

### 2. Create Required Directories

```bash
# Create data directories
mkdir -p data/input data/output data/plots

# Create validation directories
mkdir -p validation/reports validation/logs
```

## Next Steps

After installation, you can:
1. Follow the [Quick Start Guide](Quick-Start)
2. Explore the [Basic Usage](Basic-Usage) documentation
3. Check out the [Tutorials](Tutorials) section

## Support

If you encounter any issues during installation:
1. Check the [Common Issues](Common-Issues) page
2. Search the [FAQ](FAQ)
3. Create an issue in the [Issue Tracker](https://github.com/yourusername/SWE599/issues) 