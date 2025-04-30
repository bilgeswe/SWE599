# Test Instructions

This document provides instructions for running and writing tests for the road network conversion tools.

## Running Tests

To run the test suite, use the following command:

```bash
pytest tests/
```

For more detailed output and coverage information:

```bash
pytest tests/ --cov=src --cov-report=term-missing
```

## Test Structure

The test suite is organized as follows:

- `tests/test_sumo_to_xodr.py`: Tests for SUMO to OpenDRIVE conversion
- `tests/test_validator.py`: Tests for OpenDRIVE validation
- `tests/test_visualization.py`: Tests for network visualization

## Writing New Tests

When adding new tests, follow these guidelines:

1. Use descriptive test function names
2. Include docstrings explaining the test purpose
3. Use fixtures for common setup code
4. Follow the Arrange-Act-Assert pattern
5. Include both positive and negative test cases

Example test structure:

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

## Test Fixtures

Common test fixtures are available in `tests/conftest.py`:

- `validator`: OpenDriveValidator instance
- `test_data_dir`: Temporary directory for test files
- `valid_opendrive`: Sample valid OpenDRIVE file
- `invalid_opendrive`: Sample invalid OpenDRIVE file

## Continuous Integration

Tests are automatically run on:
- Pull requests
- Main branch updates
- Scheduled runs

## Coverage Requirements

- Minimum coverage: 80%
- Critical components: 90%
- New features: 100%

## Notes

- Tests should be independent and self-contained
- Use temporary directories for file operations
- Clean up resources after tests
- Mock external dependencies when necessary 