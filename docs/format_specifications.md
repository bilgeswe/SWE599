# Road Network Format Specifications

This document provides detailed specifications for the road network formats used in our project and their conversion processes.

## Overview

The project works with three main road network formats:
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
    <tag k="lanes" v="2"/>
    <tag k="oneway" v="yes"/>
  </way>
  ```
- **SUMO**: Roads are edges with explicit lanes
  ```xml
  <edge id="1" from="1" to="2" priority="1" type="highway.primary">
    <lane id="1_0" index="0" speed="13.89" width="3.5"/>
    <lane id="1_1" index="1" speed="13.89" width="3.5"/>
  </edge>
  ```
- **OpenDRIVE**: Roads have detailed geometry and lane sections
  ```xml
  <road name="Road1" length="100.0" id="1" junction="-1">
    <planView>
      <geometry s="0.0" x="29.0088" y="41.0751" hdg="0.0" length="100.0"/>
    </planView>
    <lanes>
      <laneSection s="0.0">
        <center>
          <lane id="0" type="none"/>
        </center>
        <right>
          <lane id="-1" type="driving" level="false">
            <width sOffset="0.0" a="3.5" b="0.0" c="0.0" d="0.0"/>
          </lane>
          <lane id="-2" type="driving" level="false">
            <width sOffset="0.0" a="3.5" b="0.0" c="0.0" d="0.0"/>
          </lane>
        </right>
      </laneSection>
    </lanes>
  </road>
  ```

#### 2. Lane Information
- **OSM**: 
  - Implicit in way width and tags
  - Uses `lanes` tag for count
  - Uses `width` tag for total width
  - Uses `oneway` tag for direction

- **SUMO**: 
  - Explicit lane definitions
  - Each lane has properties:
    - Speed limit
    - Width
    - Type
    - Index
  - Supports lane-specific attributes

- **OpenDRIVE**: 
  - Detailed lane properties
  - Lane sections with offsets
  - Lane connectivity
  - Lane types and materials
  - Elevation profiles

#### 3. Traffic Control
- **OSM**: 
  - Basic traffic signal tags
  - Uses `highway=traffic_signals`
  - Limited timing information

- **SUMO**: 
  - Detailed traffic light logic
  - Phase definitions
  - Timing information
  - State transitions

- **OpenDRIVE**: 
  - Signal definitions
  - Controller definitions
  - Timing information
  - Signal dependencies

## Conversion Process

### OSM → SUMO Conversion

1. **Road Conversion**
   ```python
   def convert_osm_to_sumo(osm_file, output_file):
       # Parse OSM
       G = ox.graph_from_xml(osm_file)
       
       # Convert ways to edges
       for way in G.edges():
           edge = create_sumo_edge(way)
           add_lanes(edge, way.tags)
           
       # Save SUMO network
       save_sumo_network(output_file)
   ```

2. **Lane Information**
   - Infer lane count from OSM tags
   - Set lane properties based on road type
   - Handle one-way/two-way roads
   - Calculate lane widths

3. **Traffic Signals**
   - Convert OSM traffic signal nodes
   - Create SUMO traffic light logic
   - Set signal timing
   - Define phase sequences

### SUMO → OpenDRIVE Conversion

1. **Road Conversion**
   ```python
   def convert_sumo_to_opendrive(sumo_file, output_file):
       # Parse SUMO network
       net = sumolib.net.readNet(sumo_file)
       
       # Create OpenDRIVE structure
       root = ET.Element("OpenDRIVE")
       
       # Convert edges to roads
       for edge in net.getEdges():
           road = create_opendrive_road(edge)
           add_geometry(road, edge)
           add_lanes(road, edge)
           
       # Save OpenDRIVE file
       save_opendrive_file(root, output_file)
   ```

2. **Lane Mapping**
   - Map SUMO lanes to OpenDRIVE lane sections
   - Preserve lane properties
   - Handle lane connectivity
   - Calculate geometry

3. **Traffic Control**
   - Convert SUMO traffic light logic
   - Create OpenDRIVE signal definitions
   - Preserve timing information
   - Define signal dependencies

## Validation Rules

### OSM Validation
- Required tags for ways
- Valid highway types
- Consistent lane counts
- Valid geometry

### SUMO Validation
- Valid edge connections
- Consistent lane properties
- Valid traffic light logic
- Proper junction definitions

### OpenDRIVE Validation
- Schema compliance
- Geometry continuity
- Lane connectivity
- Signal definitions

## Common Issues and Solutions

### 1. Geometry Discontinuities
- **Issue**: Gaps between road segments
- **Solution**: Use tolerance in connection checks
- **Code**:
  ```python
  def check_geometry_continuity(road1, road2, tolerance=0.1):
      end1 = get_road_endpoint(road1)
      start2 = get_road_startpoint(road2)
      return distance(end1, start2) < tolerance
  ```

### 2. Lane Count Mismatches
- **Issue**: Inconsistent lane counts
- **Solution**: Use default values and warnings
- **Code**:
  ```python
  def get_lane_count(tags, default=1):
      if 'lanes' in tags:
          return int(tags['lanes'])
      return default
  ```

### 3. Traffic Signal Timing
- **Issue**: Lost timing information
- **Solution**: Use default timing patterns
- **Code**:
  ```python
  def create_default_timing():
      return {
          'phase1': {'duration': 30, 'state': 'GGGrrr'},
          'phase2': {'duration': 5, 'state': 'yyyrrr'},
          'phase3': {'duration': 30, 'state': 'rrrGGG'},
          'phase4': {'duration': 5, 'state': 'rrryyy'}
      }
  ```

## Best Practices

1. **Data Validation**
   - Validate input data before conversion
   - Check for missing or invalid elements
   - Ensure coordinate system consistency
   - Verify required attributes

2. **Error Handling**
   - Handle missing data gracefully
   - Provide meaningful error messages
   - Log conversion issues
   - Create validation reports

3. **Performance**
   - Process large networks efficiently
   - Use appropriate data structures
   - Optimize memory usage
   - Implement batch processing

## References

1. [OpenStreetMap XML Format](https://wiki.openstreetmap.org/wiki/OSM_XML)
2. [SUMO Network Format](https://sumo.dlr.de/docs/Networks/PlainXML.html)
3. [OpenDRIVE Format](https://www.asam.net/standards/detail/opendrive/) 