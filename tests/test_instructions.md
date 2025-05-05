# Test Instructions

This document provides comprehensive instructions for running, writing, and maintaining tests for the road network conversion tools.

## Directory Structure

```
tests/
├── __init__.py          # Package initialization
├── conftest.py          # Common test fixtures
├── pytest.ini           # Pytest configuration
├── test_environment.py  # Environment setup tests
├── test_osm_fetcher.py  # OSM data fetching tests
├── test_sumo_setup.py   # SUMO configuration tests
├── test_sumo_to_xodr.py # SUMO to OpenDRIVE conversion tests
└── test_validator.py    # Network validation tests
```

## Running Tests

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
The `pytest.ini` file contains:
- Test discovery patterns
- Coverage thresholds
- Logging configuration
- Test timeout settings

## Test Categories

### 1. Environment Tests (`test_environment.py`)
- System requirements verification
- Package dependencies
- Environment variables
- Configuration files

### 2. Data Fetching Tests (`test_osm_fetcher.py`)
- OSM data retrieval
- Network graph generation
- Data format validation
- Error handling

### 3. SUMO Tests (`test_sumo_setup.py`)
- SUMO installation verification
- Network file generation
- Traffic simulation setup
- Configuration validation

### 4. Conversion Tests (`test_sumo_to_xodr.py`)
- SUMO to OpenDRIVE conversion
- Geometry preservation
- Attribute mapping
- Error handling

### 5. Validation Tests (`test_validator.py`)
- Network structure validation
- Geometry validation
- Traffic rules validation
- Error reporting

## Writing Tests

### Test Structure
```python
def test_feature_name():
    """Test description of what the test verifies.
    
    Args:
        None
        
    Returns:
        None
        
    Raises:
        AssertionError: If test conditions are not met
    """
    # Arrange
    setup_code()
    
    # Act
    result = function_under_test()
    
    # Assert
    assert result == expected_value
```

### Test Fixtures
Common fixtures in `conftest.py`:
- `validator`: NetworkValidator instance
- `test_data_dir`: Temporary directory
- `sample_network`: Test network file
- `mock_osm_data`: Mock OSM data

### Best Practices
1. Use descriptive test names
2. Include comprehensive docstrings
3. Follow Arrange-Act-Assert pattern
4. Test both success and failure cases
5. Use fixtures for common setup
6. Clean up resources after tests
7. Mock external dependencies
8. Use temporary directories for files

## Continuous Integration

### GitHub Actions
- Runs on pull requests
- Runs on main branch updates
- Scheduled daily runs
- Coverage reporting

### Coverage Requirements
- Overall coverage: 80%
- Critical components: 90%
- New features: 100%
- Test files: 100%

## Troubleshooting

### Common Issues
1. Missing dependencies
2. Environment configuration
3. File permission issues
4. Network connectivity
5. Test timeouts

### Debugging Tips
1. Use `-v` for verbose output
2. Use `--pdb` for post-mortem debugging
3. Check test logs
4. Verify environment setup
5. Review coverage reports

## Notes

- Tests should be independent
- Use meaningful assertions
- Document test dependencies
- Keep test data minimal
- Update tests with code changes
- Regular test maintenance
- Performance considerations 