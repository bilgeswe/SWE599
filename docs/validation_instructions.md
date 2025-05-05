# Validation Instructions

This document provides comprehensive instructions for validating road networks in various formats.

## Validation Levels

### 1. Basic Validation
- File format compliance
- Required elements presence
- Basic structure integrity
- Mandatory attributes

### 2. Advanced Validation
- Network connectivity
- Geometry consistency
- Attribute completeness
- Reference integrity

### 3. Simulation Validation
- Traffic rule compliance
- Signal timing
- Lane connectivity
- Vehicle behavior

## Validation Tools

### Network Validator
```python
from src.validator.network_validator import NetworkValidator

# Create validator
validator = NetworkValidator()

# Validate network
result = validator.validate("data/networks/kadikoy.net.xml")

# Get validation report
report = validator.get_report()
```

### Geometry Validator
```python
from src.validator.geometry_validator import GeometryValidator

# Create validator
validator = GeometryValidator()

# Validate geometry
result = validator.validate("data/networks/kadikoy.net.xml")

# Get validation report
report = validator.get_report()
```

### Traffic Validator
```python
from src.validator.traffic_validator import TrafficValidator

# Create validator
validator = TrafficValidator()

# Validate traffic rules
result = validator.validate("data/networks/kadikoy.net.xml")

# Get validation report
report = validator.get_report()
```

## Validation Rules

### Network Structure
1. **Road Elements**
   - Road IDs must be unique
   - Road types must be valid
   - Lane numbers must be positive
   - Speed limits must be realistic

2. **Junction Elements**
   - Junction IDs must be unique
   - Connection points must exist
   - Priority rules must be valid
   - Signal timing must be consistent

3. **Geometry Elements**
   - Coordinates must be valid
   - Curvature must be smooth
   - Grade must be within limits
   - Lane width must be realistic

### Traffic Rules
1. **Speed Limits**
   - Must be positive
   - Must be realistic for road type
   - Must be consistent within segments

2. **Priority Rules**
   - Must be defined at junctions
   - Must be consistent
   - Must follow traffic regulations

3. **Signal Timing**
   - Phases must be complete
   - Timing must be realistic
   - Cycles must be consistent

## Validation Process

### 1. Pre-validation
```python
# Check file existence
if not os.path.exists(network_file):
    raise FileNotFoundError(f"Network file not found: {network_file}")

# Check file format
if not network_file.endswith(('.net.xml', '.xodr')):
    raise ValueError("Invalid file format")
```

### 2. Structure Validation
```python
# Validate network structure
structure_validator = NetworkValidator()
structure_result = structure_validator.validate(network_file)

# Check for critical errors
if structure_result.has_critical_errors():
    raise ValidationError("Critical structure errors found")
```

### 3. Geometry Validation
```python
# Validate geometry
geometry_validator = GeometryValidator()
geometry_result = geometry_validator.validate(network_file)

# Check for geometry errors
if geometry_result.has_errors():
    print("Geometry warnings found")
```

### 4. Traffic Validation
```python
# Validate traffic rules
traffic_validator = TrafficValidator()
traffic_result = traffic_validator.validate(network_file)

# Check for traffic rule violations
if traffic_result.has_violations():
    print("Traffic rule violations found")
```

## Error Handling

### Error Categories
1. **Critical Errors**
   - Missing required elements
   - Invalid file format
   - Unrecoverable structure issues

2. **Warnings**
   - Missing optional elements
   - Inconsistent attributes
   - Potential geometry issues

3. **Information**
   - Optimization suggestions
   - Best practice recommendations
   - Performance considerations

### Error Reporting
```python
# Generate validation report
report = validator.get_report()

# Print summary
print(f"Validation Summary:")
print(f"Critical Errors: {report.critical_errors}")
print(f"Warnings: {report.warnings}")
print(f"Information: {report.info}")

# Save detailed report
report.save("validation_report.html")
```

## Best Practices

### 1. Validation Order
1. Basic structure validation
2. Geometry validation
3. Traffic rules validation
4. Simulation validation

### 2. Error Handling
- Log all validation steps
- Provide clear error messages
- Include error context
- Suggest possible fixes

### 3. Performance
- Use efficient validation algorithms
- Cache validation results
- Parallelize when possible
- Optimize memory usage

### 4. Reporting
- Generate clear reports
- Include visualizations
- Provide fix suggestions
- Track validation history

## Notes

- Validate early and often
- Keep validation rules updated
- Document validation results
- Maintain validation history
- Consider performance impact
- Use appropriate validation level
- Handle edge cases properly 