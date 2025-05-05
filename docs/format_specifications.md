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
| **Traffic Light** | `<node>` with traffic_signals tag | `<tlLogic>` | `<signal>` |
| **Speed Limit** | `maxspeed` tag | `speed` attribute | `<speed>` element |
| **Lane Width** | `width` tag | `width` attribute | `<width>` element |
| **Elevation** | `ele` tag | `z` coordinate | `<elevationProfile>` |

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
    <tag k="name" v="Bağdat Caddesi"/>
    <tag k="maxspeed" v="50"/>
  </way>
  ```
- **SUMO**: Roads are edges with explicit lanes
  ```xml
  <edge id="1" from="1" to="2" priority="1" type="highway.primary">
    <lane id="1_0" index="0" speed="13.89" width="3.5" length="100.0" shape="0.0,0.0 100.0,0.0"/>
    <lane id="1_1" index="1" speed="13.89" width="3.5" length="100.0" shape="0.0,3.5 100.0,3.5"/>
  </edge>
  ```
- **OpenDRIVE**: Roads have detailed geometry and lane sections
  ```xml
  <road name="Bağdat Caddesi" length="100.0" id="1" junction="-1">
    <link>
      <predecessor elementType="road" elementId="2" contactPoint="end"/>
      <successor elementType="road" elementId="3" contactPoint="start"/>
    </link>
    <type s="0.0" type="town"/>
    <planView>
      <geometry s="0.0" x="0.0" y="0.0" hdg="0.0" length="100.0">
        <line/>
      </geometry>
    </planView>
    <lanes>
      <laneSection s="0.0">
        <left>
          <lane id="1" type="driving" level="false">
            <width sOffset="0.0" a="3.5" b="0.0" c="0.0" d="0.0"/>
          </lane>
        </left>
        <center>
          <lane id="0" type="none" level="false"/>
        </center>
        <right>
          <lane id="-1" type="driving" level="false">
            <width sOffset="0.0" a="3.5" b="0.0" c="0.0" d="0.0"/>
          </lane>
        </right>
      </laneSection>
    </lanes>
  </road>
  ```

#### 2. Junction Representation
- **OSM**: Simple nodes with tags
  ```xml
  <node id="1" lat="41.0497" lon="29.0024">
    <tag k="highway" v="traffic_signals"/>
  </node>
  ```
- **SUMO**: Complex junctions with connections
  ```xml
  <junction id="1" type="priority" x="0.0" y="0.0" incLanes="1_0 1_1" intLanes="" shape="0.0,0.0 0.0,3.5 3.5,3.5 3.5,0.0"/>
  ```
- **OpenDRIVE**: Detailed junction definitions
  ```xml
  <junction id="1" name="Intersection 1">
    <connection id="1" incomingRoad="1" connectingRoad="2" contactPoint="start">
      <laneLink from="1" to="1"/>
      <laneLink from="-1" to="-1"/>
    </connection>
  </junction>
  ```

## Conversion Rules

### OSM to SUMO
1. **Road Conversion**
   - Convert OSM ways to SUMO edges
   - Map highway tags to edge types
   - Convert lane counts to explicit lanes
   - Preserve oneway information

2. **Junction Conversion**
   - Convert OSM nodes to SUMO junctions
   - Handle traffic signals
   - Create proper connections
   - Set junction priorities

3. **Geometry Conversion**
   - Convert OSM coordinates to SUMO coordinates
   - Handle elevation data
   - Preserve road shapes
   - Adjust for network boundaries

### SUMO to OpenDRIVE
1. **Road Conversion**
   - Convert SUMO edges to OpenDRIVE roads
   - Map edge types to road types
   - Convert lanes with proper attributes
   - Handle road connections

2. **Junction Conversion**
   - Convert SUMO junctions to OpenDRIVE junctions
   - Create proper connections
   - Handle traffic signals
   - Set junction priorities

3. **Geometry Conversion**
   - Convert SUMO coordinates to OpenDRIVE coordinates
   - Handle elevation data
   - Create proper road geometry
   - Adjust for network boundaries

## Validation Rules

### Network Structure
1. **Road Network**
   - All roads must be connected
   - No isolated junctions
   - Proper lane connections
   - Valid road types

2. **Junctions**
   - Valid junction types
   - Proper connections
   - Valid traffic signals
   - Correct priorities

3. **Geometry**
   - Valid coordinates
   - Proper road shapes
   - Valid lane widths
   - Correct elevations

### Data Quality
1. **Required Attributes**
   - Road names
   - Speed limits
   - Lane counts
   - Junction types

2. **Optional Attributes**
   - Elevation data
   - Traffic signals
   - Road markings
   - Additional properties

## Examples

### Kadıköy Network
1. **OSM Format**
   - Bounds: 41.0297, 28.9724 to 41.0697, 29.0324
   - Main roads: Bağdat Caddesi, Moda Caddesi
   - Junctions: Traffic signals at major intersections

2. **SUMO Format**
   - Network size: ~5km²
   - Edge types: highway.primary, highway.secondary
   - Junction types: priority, traffic_light

3. **OpenDRIVE Format**
   - Road types: town, residential
   - Lane configurations: 2-4 lanes
   - Junction types: priority, traffic_light

## Notes

- All examples use the Kadıköy network as a reference
- File paths are relative to the project root
- Make sure to have the required dependencies installed
- Check the documentation for more detailed examples 