# Validation Instructions

This document provides instructions for validating road network data and conversion results.

## OpenDRIVE Validation

To validate an OpenDRIVE file, use the following command:

```bash
python src/validator/validate_opendrive.py path/to/file.xodr
```

The validator checks for:
1. XML schema compliance
2. Required elements and attributes
3. Logical consistency
4. Geometric validity

## Validation Rules

### Basic Structure
- Root element must be `<OpenDRIVE>`
- Must contain at least one `<road>` element
- Must contain at least one `<junction>` element

### Road Elements
- Each road must have a unique ID
- Must contain at least one `<planView>` element
- Must contain at least one `<lanes>` element
- Geometry must be continuous and valid

### Lane Elements
- Each lane must have a unique ID within its road
- Lane width must be positive
- Lane type must be valid
- Lane links must be valid

### Junction Elements
- Each junction must have a unique ID
- Connection elements must reference valid roads and lanes
- Priority rules must be valid

## Error Handling

The validator provides:
- Detailed error messages
- Line numbers for XML errors
- Suggestions for fixing common issues

## Validation Reports

Validation results are saved in:
- `validation/reports/`: Detailed validation reports
- `validation/logs/`: Validation logs

## Notes

- Always validate files before using them
- Fix validation errors in order of severity
- Keep backup copies of original files
- Document any intentional deviations from standards 