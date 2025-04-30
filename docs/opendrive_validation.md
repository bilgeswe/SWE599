# OpenDRIVE Validation and Comparison Tools

This document describes the validation and comparison tools for OpenDRIVE files.

## Schema Validation

The schema validation component ensures OpenDRIVE files comply with the official 1.7.0 specification.

### Features
- Validates against the official OpenDRIVE 1.7.0 schema
- Checks for required elements and attributes
- Validates data types and enumerations
- Provides detailed error messages for invalid files

### Implementation
```python
class OpenDriveValidator:
    def validate_schema(self, xodr_file: str) -> ValidationResult:
        """
        Validates an OpenDRIVE file against the official schema.
        
        Args:
            xodr_file: Path to the OpenDRIVE file
            
        Returns:
            ValidationResult containing success status and any errors
        """
        # Implementation details...
```

## Geometry Validation

The geometry validation component ensures the logical consistency of road network geometry.

### Features
- Checks road length consistency
- Validates lane width continuity
- Verifies geometry element connections
- Validates junction connections
- Detects overlapping geometries

### Implementation
```python
class OpenDriveValidator:
    def validate_geometry(self, xodr_file: str) -> ValidationResult:
        """
        Validates the geometry of an OpenDRIVE file.
        
        Args:
            xodr_file: Path to the OpenDRIVE file
            
        Returns:
            ValidationResult containing success status and any errors
        """
        # Implementation details...

    def _calculate_road_length(self, road: Element) -> float:
        """Calculates the total length of a road."""
        # Implementation details...

    def _validate_lane_widths(self, road: Element, warnings: List[str]) -> None:
        """Validates lane width continuity."""
        # Implementation details...

    def _validate_geometry_continuity(self, road: Element, errors: List[str]) -> None:
        """Validates geometry element connections."""
        # Implementation details...

    def _validate_junctions(self, root: Element, errors: List[str]) -> None:
        """Validates junction connections."""
        # Implementation details...

    def _get_geometry_endpoint(self, geometry: Element) -> Tuple[float, float]:
        """Calculates the endpoint of a geometry element."""
        # Implementation details...

    def _points_are_close(self, p1: Tuple[float, float], 
                         p2: Tuple[float, float], 
                         tolerance: float) -> bool:
        """Checks if two points are within tolerance distance."""
        # Implementation details...
```

## Visual Comparison Tools

The visual comparison tools provide side-by-side visualization of OpenDRIVE files.

### Features
- Side-by-side visualization of two OpenDRIVE files
- Plots roads and junctions
- Supports different geometry types (lines, arcs, spirals)
- Provides clear visual feedback for differences

### Implementation
```python
class OpenDriveValidator:
    def visualize_comparison(self, xodr_file1: str, xodr_file2: str) -> None:
        """
        Creates a side-by-side visualization of two OpenDRIVE files.
        
        Args:
            xodr_file1: Path to the first OpenDRIVE file
            xodr_file2: Path to the second OpenDRIVE file
        """
        # Implementation details...

    def _plot_opendrive(self, xodr_file: str, ax: plt.Axes, title: str) -> None:
        """Plots a single OpenDRIVE file."""
        # Implementation details...
```

## Test Suite

The implementation includes a comprehensive test suite covering:

### Test Cases
- Valid and invalid files
- Geometry errors
- Lane width discontinuities
- File handling edge cases
- Visualization functionality

### Example Test Structure
```python
def test_schema_validation():
    """Tests schema validation functionality."""
    # Test valid file
    result = validator.validate_schema("valid.xodr")
    assert result.is_valid
    
    # Test invalid file
    result = validator.validate_schema("invalid.xodr")
    assert not result.is_valid
    assert len(result.errors) > 0

def test_geometry_validation():
    """Tests geometry validation functionality."""
    # Test continuous geometry
    result = validator.validate_geometry("continuous.xodr")
    assert result.is_valid
    
    # Test discontinuous geometry
    result = validator.validate_geometry("discontinuous.xodr")
    assert not result.is_valid
    assert "Geometry discontinuity" in result.errors[0]
```

## Usage Examples

### Command Line
```bash
# Validate a single file
python src/validator/validate_opendrive.py input.xodr

# Compare two files
python src/validator/compare_opendrive.py file1.xodr file2.xodr
```

### Python API
```python
from src.validator import OpenDriveValidator

# Create validator instance
validator = OpenDriveValidator()

# Validate schema
result = validator.validate_schema("input.xodr")
if not result.is_valid:
    print("Validation errors:", result.errors)

# Validate geometry
result = validator.validate_geometry("input.xodr")
if not result.is_valid:
    print("Geometry errors:", result.errors)

# Compare files
validator.visualize_comparison("file1.xodr", "file2.xodr")
```

## Notes

- The validator uses the official OpenDRIVE 1.7.0 schema
- Geometry validation includes checks for common errors
- Visual comparison tools help identify differences
- Test suite ensures reliability and correctness 