# Format Comparison

This document provides a detailed comparison of the road network formats used in the project.

## Overview

| Feature | OSM | SUMO | OpenDRIVE |
|---------|-----|------|-----------|
| **Primary Use** | Open mapping data | Traffic simulation | Road network description |
| **Format** | XML | XML | XML |
| **Coordinate System** | WGS84 | Local Cartesian | Local Cartesian |
| **Geometry** | Simple | Intermediate | Complex |
| **Lane Information** | Implicit | Explicit | Detailed |
| **Traffic Control** | Basic | Advanced | Advanced |

## Road Representation

### OSM
- Uses `<way>` elements with highway tags
- Lanes are implicit in width and tags
- Basic road properties:
  ```xml
  <way id="123">
    <nd ref="1"/>
    <nd ref="2"/>
    <tag k="highway" v="primary"/>
    <tag k="lanes" v="2"/>
    <tag k="oneway" v="yes"/>
    <tag k="maxspeed" v="50"/>
  </way>
  ```

### SUMO
- Uses `<edge>` elements with explicit lanes
- Detailed lane properties:
  ```xml
  <edge id="1" from="1" to="2" priority="1" type="highway.primary">
    <lane id="1_0" index="0" speed="13.89" width="3.5" length="100.0"/>
    <lane id="1_1" index="1" speed="13.89" width="3.5" length="100.0"/>
  </edge>
  ```

### OpenDRIVE
- Uses `<road>` elements with detailed geometry
- Complex lane sections:
  ```xml
  <road name="Road1" length="100.0" id="1" junction="-1">
    <lanes>
      <laneSection s="0.0">
        <left>
          <lane id="1" type="driving">
            <width sOffset="0.0" a="3.5"/>
          </lane>
        </left>
        <center>
          <lane id="0" type="none"/>
        </center>
        <right>
          <lane id="-1" type="driving">
            <width sOffset="0.0" a="3.5"/>
          </lane>
        </right>
      </laneSection>
    </lanes>
  </road>
  ```

## Junction Representation

### OSM
- Simple nodes with tags
- Basic intersection information:
  ```xml
  <node id="1" lat="41.0497" lon="29.0024">
    <tag k="highway" v="traffic_signals"/>
  </node>
  ```

### SUMO
- Complex junctions with connections
- Traffic light logic:
  ```xml
  <junction id="1" type="priority" x="0.0" y="0.0">
    <request index="0" response="0" foes="0"/>
  </junction>
  <tlLogic id="1" type="static" programID="0" offset="0">
    <phase duration="31" state="GG"/>
    <phase duration="6" state="yy"/>
  </tlLogic>
  ```

### OpenDRIVE
- Detailed junction definitions
- Connection rules:
  ```xml
  <junction id="1" name="Intersection 1">
    <connection id="1" incomingRoad="1" connectingRoad="2">
      <laneLink from="1" to="1"/>
    </connection>
  </junction>
  ```

## Geometry Handling

### OSM
- Simple line segments
- WGS84 coordinates
- No explicit geometry types
- Limited elevation data

### SUMO
- Line segments and curves
- Local Cartesian coordinates
- Basic geometry types
- Optional elevation data

### OpenDRIVE
- Complex geometry types:
  - Lines
  - Spirals
  - Arcs
  - Polynomials
- Local Cartesian coordinates
- Detailed elevation profiles

## Traffic Control

### OSM
- Basic traffic signal tags
- No timing information
- Limited control types

### SUMO
- Detailed traffic light logic
- Phase definitions
- Timing information
- State transitions

### OpenDRIVE
- Signal definitions
- Controller definitions
- Timing information
- Signal dependencies

## Attribute Mapping

| OSM Tag | SUMO Attribute | OpenDRIVE Element |
|---------|---------------|-------------------|
| `highway=primary` | `type="highway.primary"` | `type="town"` |
| `lanes=2` | Two `<lane>` elements | Two lanes in `<laneSection>` |
| `maxspeed=50` | `speed="13.89"` | `<speed>` element |
| `oneway=yes` | `from` and `to` nodes | Unidirectional road |
| `width=3.5` | `width="3.5"` | `<width a="3.5">` |

## Conversion Considerations

### OSM to SUMO
1. **Geometry**
   - Convert WGS84 to local coordinates
   - Create explicit lane definitions
   - Handle one-way roads

2. **Attributes**
   - Map highway tags to edge types
   - Convert speed limits
   - Handle lane counts

3. **Junctions**
   - Create proper connections
   - Handle traffic signals
   - Set priorities

### SUMO to OpenDRIVE
1. **Geometry**
   - Convert to OpenDRIVE geometry types
   - Create proper lane sections
   - Handle elevation data

2. **Attributes**
   - Map edge types to road types
   - Convert lane properties
   - Handle traffic signals

3. **Junctions**
   - Create proper connections
   - Handle traffic light logic
   - Set junction priorities

## Notes

- OSM provides the most basic representation
- SUMO adds simulation-specific details
- OpenDRIVE offers the most detailed description
- Conversion between formats may lose some information
- Validation is crucial during conversion 