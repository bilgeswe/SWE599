# Validation Instructions

This document provides detailed instructions for validating road network data in various formats.

## 1. Network Issue Detection

### Basic Validation
```bash
# Detect issues in SUMO network
python src/converter/network_issue_detector.py data/sumo/kadıköy__istanbul__turkey.net.xml
```

The detector will check for:
- Disconnected edges
- Sharp turns
- Orphaned lanes
- Incomplete roundabouts
- Missing required attributes

### Validation Output
The detector will output:
- Number of issues found
- Details of each issue
- Recommendations for fixing issues

## 2. OpenDRIVE Validation

### Basic Validation
```bash
# Validate OpenDRIVE network
python src/converter/advanced_sumo_to_xodr.py --validate-opendrive data/opendrive/kadıköy__istanbul__turkey.xodr
```

### Validation Options
```bash
# Validate with specific checks
python src/converter/advanced_sumo_to_xodr.py \
    --validate-opendrive \
    --check-geometry \
    --check-connections \
    --check-lanes \
    data/opendrive/kadıköy__istanbul__turkey.xodr
```

## 3. Common Issues and Solutions

### Disconnected Edges
- **Issue**: Edges that don't connect to any other edges
- **Solution**: 
  1. Check the network for missing connections
  2. Add missing connections in the SUMO network
  3. Re-run the conversion

### Sharp Turns
- **Issue**: Turns with angles greater than 150 degrees
- **Solution**:
  1. Identify the problematic edges
  2. Add intermediate points to smooth the turn
  3. Re-run the conversion

### Orphaned Lanes
- **Issue**: Lanes that don't connect to any other lanes
- **Solution**:
  1. Check lane connections in the SUMO network
  2. Add missing lane connections
  3. Re-run the conversion

### Incomplete Roundabouts
- **Issue**: Roundabouts with missing connections
- **Solution**:
  1. Check roundabout geometry
  2. Add missing connections
  3. Re-run the conversion

## 4. Validation Best Practices

### Before Conversion
1. Validate OSM data
2. Check network connectivity
3. Verify geometry

### During Conversion
1. Monitor conversion process
2. Check for warnings
3. Validate intermediate results

### After Conversion
1. Run full validation
2. Check visualization
3. Verify all connections

## 5. Troubleshooting

### Common Errors
1. **Missing Attributes**
   - Check required attributes
   - Add missing attributes
   - Re-run validation

2. **Invalid Geometry**
   - Check coordinate system
   - Verify geometry calculations
   - Fix invalid shapes

3. **Connection Issues**
   - Check junction connections
   - Verify lane connections
   - Add missing connections

### Debugging Tips
1. Use verbose output
2. Check log files
3. Visualize issues
4. Test in small sections

## 6. Notes

- Always validate after modifications
- Keep validation reports
- Document fixes
- Test thoroughly
- Use consistent naming 