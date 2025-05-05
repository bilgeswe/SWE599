# Testing Guidelines

This document provides comprehensive guidelines for testing the Road Network Conversion and Validation Tools.

## 1. Test Structure

### Directory Structure
```tests/
├── __init__.py
├── conftest.py
├── pytest.ini
├── test_environment.py
├── test_instructions.md
├── test_osm_fetcher.py
├── test_sumo_setup.py
├── test_sumo_to_xodr.py
└── test_validator.py
```

### Test Categories
- **Environment Tests** (`test_environment.py`)
  - System requirements
  - Dependencies
  - Configuration

- **Data Fetching Tests** (`test_osm_fetcher.py`)
  - OSM data retrieval
  - Network extraction
  - Data validation

- **Conversion Tests** (`test_sumo_to_xodr.py`)
  - OSM to SUMO conversion
  - SUMO to OpenDRIVE conversion
  - Format validation

- **Validation Tests** (`test_validator.py`)
  - Network structure validation
  - Geometry validation
  - Connection validation

## 2. Running Tests

### Basic Test Execution
```bash
# Run all tests
pytest tests/

# Run specific test file
pytest tests/test_validator.py

# Run specific test function
pytest tests/test_validator.py::test_network_structure
```

### Coverage Reports
```bash
# Generate coverage report
pytest tests/ --cov=src --cov-report=term-missing

# Generate HTML coverage report
pytest tests/ --cov=src --cov-report=html
```

### Test Configuration
```ini
# pytest.ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = --cov=src --cov-report=term-missing
```

## 3. Writing Tests

### Test Structure
```python
def test_feature_name():
    """Test description of what the test verifies."""
    # Arrange
    setup_code()
    
    # Act
    result = function_under_test()
    
    # Assert
    assert result == expected_value
```

### Test Fixtures
```python
# conftest.py
@pytest.fixture
def validator():
    """Create a NetworkValidator instance."""
    return NetworkValidator()

@pytest.fixture
def test_data_dir(tmp_path):
    """Create a temporary directory for test files."""
    return tmp_path

@pytest.fixture
def valid_network():
    """Load a valid network file."""
    return load_network("data/networks/kadikoy.net.xml")
```

### Common Test Patterns

#### Network Validation
```python
def test_network_structure(validator, valid_network):
    """Test network structure validation."""
    result = validator.validate_structure(valid_network)
    assert result.is_valid
    assert len(result.errors) == 0
```

#### Geometry Validation
```python
def test_geometry_validation(validator, valid_network):
    """Test geometry validation."""
    result = validator.validate_geometry(valid_network)
    assert result.is_valid
    assert result.max_deviation < 0.1
```

#### Conversion Tests
```python
def test_osm_to_sumo_conversion():
    """Test OSM to SUMO conversion."""
    # Convert network
    convert_osm_to_sumo("input.osm", "output.net.xml")
    
    # Validate output
    assert os.path.exists("output.net.xml")
    assert is_valid_sumo_network("output.net.xml")
```

## 4. Test Data

### Test Networks
- **Kadıköy Network**
  - Complex urban network
  - Multiple junction types
  - Various road geometries

- **Levent Network**
  - Business district network
  - Regular grid layout
  - Traffic signal systems

### Sample Files
```python
@pytest.fixture
def sample_osm_file():
    """Return path to sample OSM file."""
    return "data/networks/kadikoy.osm"

@pytest.fixture
def sample_sumo_file():
    """Return path to sample SUMO file."""
    return "data/networks/kadikoy.net.xml"
```

## 5. Best Practices

### Test Organization
1. Group related tests in test files
2. Use descriptive test names
3. Include docstrings
4. Follow the Arrange-Act-Assert pattern

### Test Data Management
1. Use fixtures for common setup
2. Clean up resources after tests
3. Use temporary directories
4. Mock external dependencies

### Error Handling
1. Test both success and failure cases
2. Verify error messages
3. Check error types
4. Validate error handling

### Performance
1. Keep tests fast
2. Use appropriate test data size
3. Avoid unnecessary I/O
4. Cache expensive operations

## 6. Continuous Integration

### GitHub Actions
```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run tests
        run: pytest tests/ --cov=src
```

### Coverage Requirements
- Overall coverage: 80%
- Critical components: 90%
- New features: 100%

## 7. Troubleshooting

### Common Issues
1. **Missing Dependencies**
   ```bash
   pip install -r requirements-dev.txt
   ```

2. **Test Failures**
   ```bash
   # Run with verbose output
   pytest -v tests/
   
   # Run with debug output
   pytest --pdb tests/
   ```

3. **Coverage Issues**
   ```bash
   # Generate detailed coverage report
   pytest --cov=src --cov-report=html
   ```

## Next Steps

1. Review the [Test Instructions](Test-Instructions) for more details
2. Check the [Development Guide](Development-Guide) for coding standards
3. Refer to the [API Documentation](API-Documentation) for function details 