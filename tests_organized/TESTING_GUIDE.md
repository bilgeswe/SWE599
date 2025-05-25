# 🧪 Testing Guide - Üsküdar AV Simulation Project

> **Comprehensive guide for running, writing, and understanding tests in our organized testing framework.**

## 📋 Table of Contents

1. [🏗️ Test Structure Overview](#️-test-structure-overview)
2. [🚀 Quick Start Testing](#-quick-start-testing)
3. [📂 Test Categories](#-test-categories)
4. [🎯 Running Specific Tests](#-running-specific-tests)
5. [✍️ Writing New Tests](#️-writing-new-tests)
6. [🔧 Test Configuration](#-test-configuration)
7. [📊 Coverage & Quality](#-coverage--quality)
8. [🛠️ Troubleshooting Tests](#️-troubleshooting-tests)

---

## 🏗️ Test Structure Overview

Our testing framework is organized into a clear hierarchical structure that mirrors our project's architecture:

```
tests_organized/
├── 📁 unit/                    # Individual component tests
│   ├── v1_basic/              # Version 1 (Basic Method) tests
│   ├── v2_advanced/           # Version 2 (Advanced Method) tests
│   └── shared/                # Tests applying to both versions
├── 📁 integration/            # Component interaction tests
│   ├── v1_basic/              # V1 integration workflows
│   ├── v2_advanced/           # V2 integration workflows
│   └── shared/                # Cross-version integration
├── 📁 functional/             # End-to-end workflow tests
│   ├── v1_basic/              # Complete V1 pipeline tests
│   ├── v2_advanced/           # Complete V2 pipeline tests
│   └── shared/                # Cross-system functionality
├── 📁 performance/            # Speed and memory benchmarks
│   ├── v1_basic/              # V1 performance tests
│   ├── v2_advanced/           # V2 performance tests
│   └── shared/                # Comparative performance
├── 📁 fixtures/               # Test data and fixtures
├── 📁 utils/                  # Testing utilities and helpers
├── 📁 data/                   # Sample data for tests
└── 📁 examples/               # Reference output files
```

### **Test Type Definitions**

| Type | Purpose | Examples |
|------|---------|----------|
| **Unit** | Test individual functions/classes | `test_osm_fetcher.py`, `test_validator.py` |
| **Integration** | Test component interactions | `test_conversion_errors.py`, `test_pipeline.py` |
| **Functional** | Test complete workflows | `test_uskudar_pipeline.py`, `test_export_workflow.py` |
| **Performance** | Benchmark speed and memory | `test_large_network_performance.py` |

---

## 🚀 Quick Start Testing

### **Run All Tests**
```bash
# Run the complete test suite
pytest tests_organized/

# Run with verbose output
pytest tests_organized/ -v

# Run with coverage report
pytest tests_organized/ --cov=v1_basic_method --cov=v2_advanced_method --cov-report=html
```

### **Run Tests by Category**
```bash
# Unit tests only
pytest -m unit

# Integration tests only
pytest -m integration

# Functional tests only
pytest -m functional

# Performance benchmarks
pytest -m performance
```

### **Run Tests by Version**
```bash
# Version 1 (Basic) tests only
pytest -m v1_basic

# Version 2 (Advanced) tests only
pytest -m v2_advanced

# Tests that apply to both versions
pytest -m shared
```

---

## 📂 Test Categories

### **🔧 Unit Tests**

**Purpose**: Test individual components in isolation to ensure each function and class works correctly.

**Location**: `tests_organized/unit/`

**Examples**:
- `v1_basic/test_osm_fetcher.py` - OSM data fetching functions
- `v2_advanced/test_road_geometry.py` - Geometric calculation algorithms
- `shared/test_network_validator.py` - Network validation logic

**Run Command**:
```bash
# All unit tests
pytest tests_organized/unit/ -v

# V1 unit tests only
pytest tests_organized/unit/v1_basic/ -v

# V2 unit tests only  
pytest tests_organized/unit/v2_advanced/ -v

# Shared unit tests
pytest tests_organized/unit/shared/ -v
```

### **🔗 Integration Tests**

**Purpose**: Test how different components work together, focusing on interfaces and data flow between modules.

**Location**: `tests_organized/integration/`

**Examples**:
- `shared/test_conversion_errors.py` - OSM → SUMO → OpenDRIVE conversion chain
- `shared/test_junction_connections.py` - Network connectivity validation
- `v2_advanced/test_export_pipeline.py` - Complete export workflow

**Run Command**:
```bash
# All integration tests
pytest tests_organized/integration/ -v

# Integration tests with slower timeout
pytest tests_organized/integration/ -v --timeout=600
```

### **🎯 Functional Tests**

**Purpose**: Test complete end-to-end workflows from user perspective, validating entire use cases.

**Location**: `tests_organized/functional/`

**Examples**:
- `v1_basic/test_basic_pipeline.py` - Complete V1 workflow test
- `v2_advanced/test_uskudar_simulation.py` - Full Üsküdar AV simulation test
- `shared/test_format_compatibility.py` - Cross-format conversion validation

**Run Command**:
```bash
# All functional tests (slower)
pytest tests_organized/functional/ -v -m "not slow"

# Include slow tests (complete workflows)
pytest tests_organized/functional/ -v
```

### **⚡ Performance Tests**

**Purpose**: Benchmark execution speed, memory usage, and scalability under different conditions.

**Location**: `tests_organized/performance/`

**Examples**:
- `shared/test_large_network_performance.py` - Large network processing benchmarks
- `v2_advanced/test_export_performance.py` - OpenDRIVE/OpenSCENARIO export speed
- `v1_basic/test_conversion_performance.py` - Basic conversion speed tests

**Run Command**:
```bash
# Performance benchmarks
pytest tests_organized/performance/ -v --benchmark-only

# Performance with comparison to baseline
pytest tests_organized/performance/ -v --benchmark-compare
```

---

## 🎯 Running Specific Tests

### **By Test Markers**

```bash
# Tests that require SUMO installation
pytest -m requires_sumo

# Tests that need network connectivity
pytest -m requires_network

# Skip slow tests during development
pytest -m "not slow"

# Advanced tests only
pytest -m v2_advanced

# Integration tests for V1
pytest -m "integration and v1_basic"

# Unit tests excluding performance
pytest -m "unit and not performance"
```

### **By File or Function**

```bash
# Run specific test file
pytest tests_organized/unit/v2_advanced/test_road_geometry.py -v

# Run specific test function
pytest tests_organized/unit/shared/test_network_validator.py::test_validate_network_structure -v

# Run tests matching pattern
pytest -k "test_osm" -v

# Run tests with specific substring
pytest -k "validator" -v
```

### **Advanced Test Selection**

```bash
# Run failed tests from last run
pytest --lf

# Run tests in parallel (requires pytest-xdist)
pytest -n auto

# Run with specific log level
pytest --log-cli-level=DEBUG

# Generate JUnit XML report
pytest --junitxml=test_results.xml
```

---

## ✍️ Writing New Tests

### **Test File Naming Convention**

- **Unit Tests**: `test_[component_name].py`
- **Integration Tests**: `test_[workflow_name].py`  
- **Functional Tests**: `test_[feature_name]_workflow.py`
- **Performance Tests**: `test_[component_name]_performance.py`

### **Test Function Structure**

```python
import pytest
from pathlib import Path

@pytest.mark.unit
@pytest.mark.v2_advanced
def test_opendrive_export_basic(temp_output_dir, sample_sumo_network):
    """Test basic OpenDRIVE export functionality.
    
    Args:
        temp_output_dir: Temporary directory fixture
        sample_sumo_network: Sample SUMO network data fixture
    """
    # Arrange: Set up test data
    from v2_advanced_method.exporters.opendrive_exporter.exporter import OpenDRIVEExporter
    
    exporter = OpenDRIVEExporter()
    output_file = temp_output_dir / "test_output.xodr"
    
    # Act: Execute the functionality
    exporter.set_network_offset(-668686.91, -4539963.74)
    exporter.add_node("node1", x=29.0448, y=41.0370)
    exporter.export(str(output_file))
    
    # Assert: Verify the results
    assert output_file.exists()
    assert output_file.stat().st_size > 0
    
    # Verify file content
    content = output_file.read_text()
    assert "<OpenDRIVE>" in content
    assert "node1" in content
```

### **Using Fixtures**

```python
def test_with_mock_uskudar_data(mock_uskudar_data, create_temp_osm_file):
    """Test using project-specific fixtures."""
    # Use Üsküdar-specific test data
    bounds = mock_uskudar_data['bounds']
    assert bounds['min_lat'] == 40.992
    
    # Create temporary OSM file
    osm_file = create_temp_osm_file()
    assert Path(osm_file).exists()
```

### **Adding Test Markers**

```python
@pytest.mark.slow
@pytest.mark.requires_sumo
@pytest.mark.integration
@pytest.mark.v1_basic
def test_complete_v1_pipeline():
    """Test that requires SUMO and takes significant time."""
    pass
```

---

## 🔧 Test Configuration

### **Pytest Configuration** (`pytest.ini`)

Key configuration options in our setup:

```ini
[tool:pytest]
testpaths = tests_organized          # Where to find tests
addopts = -v --tb=short --color=yes  # Default options
markers = unit, integration, ...     # Available markers
timeout = 300                        # Test timeout (5 minutes)
```

### **Environment Variables**

Tests automatically set these environment variables:

- `TESTING=1` - Indicates test environment
- `SUMO_HOME=/opt/homebrew/share/sumo` - SUMO installation path

### **Shared Fixtures** (`conftest.py`)

Available fixtures for all tests:

- `project_root_path` - Project root directory
- `temp_output_dir` - Temporary directory for test outputs
- `sample_osm_data` - Mock OSM data for testing
- `sample_sumo_network` - Mock SUMO network data
- `mock_uskudar_data` - Üsküdar-specific test data
- `create_temp_osm_file()` - Function to create temporary OSM files
- `create_temp_sumo_file()` - Function to create temporary SUMO files

---

## 📊 Coverage & Quality

### **Code Coverage**

```bash
# Generate HTML coverage report
pytest --cov=v1_basic_method --cov=v2_advanced_method --cov-report=html

# Generate terminal coverage report  
pytest --cov=v1_basic_method --cov=v2_advanced_method --cov-report=term

# Coverage with missing lines
pytest --cov=v1_basic_method --cov=v2_advanced_method --cov-report=term-missing

# Minimum coverage threshold
pytest --cov=v1_basic_method --cov=v2_advanced_method --cov-fail-under=80
```

### **Quality Checks**

```bash
# Run tests with warnings enabled
pytest --disable-warnings=false

# Check for test duplication
pytest --collect-only | grep "test_" | sort | uniq -d

# Validate test markers
pytest --strict-markers
```

### **Performance Monitoring**

```bash
# Show slowest 10 tests
pytest --durations=10

# Profile test execution
pytest --profile

# Memory usage profiling (requires pytest-memprof)
pytest --memprof
```

---

## 🛠️ Troubleshooting Tests

### **Common Issues**

**1. Import Errors**
```bash
# Problem: Module not found
ModuleNotFoundError: No module named 'v1_basic_method'

# Solution: Run from project root
cd /path/to/SWE599
pytest tests_organized/
```

**2. SUMO Not Found**
```bash
# Problem: SUMO tools not available
FileNotFoundError: netconvert not found

# Solution: Install SUMO
brew install sumo  # macOS
# or check SUMO_HOME environment variable
```

**3. Fixture Not Found**
```bash
# Problem: Fixture 'temp_output_dir' not found
# Solution: Import pytest and ensure conftest.py is accessible
```

**4. Slow Tests**
```bash
# Problem: Tests taking too long
# Solution: Skip slow tests during development
pytest -m "not slow"
```

### **Debug Mode**

```bash
# Run single test with maximum verbosity
pytest tests_organized/unit/v2_advanced/test_road_geometry.py::test_specific_function -vvv -s

# Enable all logging
pytest --log-cli-level=DEBUG --capture=no

# Drop into debugger on failure
pytest --pdb

# Debug specific fixture
pytest --setup-show
```

### **Test Data Issues**

```bash
# Clean test data
rm -rf tests_organized/data/temp/*

# Regenerate fixtures
pytest tests_organized/fixtures/test_data.py -v

# Verify test files
pytest tests_organized/examples/ -v
```

---

## 📈 Continuous Integration

### **GitHub Actions Example**

```yaml
# .github/workflows/tests.yml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: 3.8
    - name: Install SUMO
      run: |
        sudo add-apt-repository ppa:sumo/stable
        sudo apt-get update
        sudo apt-get install sumo sumo-tools
    - name: Install dependencies
      run: pip install -r requirements.txt
    - name: Run tests
      run: pytest tests_organized/ --cov=v1_basic_method --cov=v2_advanced_method
```

---

## 📞 Getting Help

**Test-Specific Issues:**
- Check the `tests_organized/utils/test_instructions.md` for additional guidance
- Review existing tests for patterns and examples
- Use `pytest --help` for command-line options

**Project Issues:**
- Main project documentation: `instructions.md`
- Version-specific guides: `v1_basic_method/README.md`, `v2_advanced_method/README.md`

---

**🧪 Happy Testing!**  
**🏛️ Built for SWE599 - Advanced Software Development Project**  
**📍 Geographic Focus: Üsküdar, Istanbul, Turkey** 