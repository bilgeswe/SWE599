# Road Network Formats and Conversion

## Overview

This document explains the three main road network formats used in our project:
- OpenStreetMap (OSM) XML format (.osm)
- SUMO Network format (.net.xml)
- OpenDRIVE format (.xodr)

## Format Comparison

### Basic Elements

| Element | OSM (.osm) | SUMO (.net.xml) | OpenDRIVE (.xodr) |
|---------|------------|-----------------|-------------------|
| **Road** | `<way>` with highway tag | `<edge>` | `<road>` |
| **Lane** | Implicit in way width | `<lane>` | `<lane>` |
| **Intersection** | `<node>` with tags | `<junction>` | `<junction>` |
| **Traffic Light** | `<node>` with traffic_signals tag | `<tl-logic>` | `<signal>` |

### Key Differences

#### 1. Road Representation
- **OSM**: Roads are represented as ways with tags
  ```xml
  <way id="123">
    <nd ref="1"/>
    <nd ref="2"/>
    <tag k="highway" v="primary"/>
  </way>
  ```
- **SUMO**: Roads are edges with explicit lanes
  ```xml
  <edge id="1" from="1" to="2">
    <lane id="1_0" index="0" speed="13.89"/>
  </edge>
  ```
- **OpenDRIVE**: Roads have detailed geometry and lane sections
  ```xml
  <road name="Road1">
    <planView>
      <geometry s="0.0" x="29.0088" y="41.0751"/>
    </planView>
    <lanes>
      <laneSection s="0.0">
        <center>
          <lane id="0" type="none"/>
        </center>
      </laneSection>
    </lanes>
  </road>
  ```

#### 2. Lane Information
- **OSM**: Lane information is implicit in way width and tags
- **SUMO**: Explicit lane definitions with properties
- **OpenDRIVE**: Detailed lane properties and connectivity

#### 3. Traffic Control
- **OSM**: Basic traffic signal tags
- **SUMO**: Detailed traffic light logic
- **OpenDRIVE**: Signal definitions with timing

## Conversion Process

### OSM → SUMO Conversion

1. **Road Conversion**
   - Convert OSM ways to SUMO edges
   - Preserve road type information
   - Maintain connectivity

2. **Lane Information**
   - Infer lane count from OSM tags
   - Set lane properties based on road type
   - Handle one-way/two-way roads

3. **Traffic Signals**
   - Convert OSM traffic signal nodes
   - Create SUMO traffic light logic
   - Set signal timing

### SUMO → OpenDRIVE Conversion

1. **Road Conversion**
   - Convert SUMO edges to OpenDRIVE roads
   - Preserve geometry information
   - Maintain road hierarchy

2. **Lane Mapping**
   - Map SUMO lanes to OpenDRIVE lane sections
   - Preserve lane properties
   - Handle lane connectivity

3. **Traffic Control**
   - Convert SUMO traffic light logic
   - Create OpenDRIVE signal definitions
   - Preserve timing information

## Implementation

### Python Tools
- **OSM Processing**: `osmnx` library
- **SUMO Processing**: `sumolib` library
- **OpenDRIVE Processing**: `lxml` for XML handling

### Example Code
```python
# Parse OSM
G = ox.graph_from_xml("network.osm")

# Parse SUMO
net = sumolib.net.readNet("network.net.xml")

# Create OpenDRIVE
root = ET.Element("OpenDRIVE")
# ... add roads, lanes, etc.
```

## Best Practices

1. **Data Validation**
   - Validate input data before conversion
   - Check for missing or invalid elements
   - Ensure coordinate system consistency

2. **Error Handling**
   - Handle missing data gracefully
   - Provide meaningful error messages
   - Log conversion issues

3. **Performance**
   - Process large networks efficiently
   - Use appropriate data structures
   - Optimize memory usage

## References

1. [OpenStreetMap XML Format](https://wiki.openstreetmap.org/wiki/OSM_XML)
2. [SUMO Network Format](https://sumo.dlr.de/docs/Networks/PlainXML.html)
3. [OpenDRIVE Format](https://www.asam.net/standards/detail/opendrive/) 