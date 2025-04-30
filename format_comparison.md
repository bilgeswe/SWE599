# Road Network Format Comparison

## Basic Elements

| Element | OSM (.osm) | SUMO (.net.xml) | OpenDRIVE (.xodr) |
|---------|------------|-----------------|-------------------|
| **Road** | `<way>` with highway tag | `<edge>` | `<road>` |
| **Lane** | Implicit in way width | `<lane>` | `<lane>` |
| **Intersection** | `<node>` with tags | `<junction>` | `<junction>` |
| **Traffic Light** | `<node>` with traffic_signals tag | `<tl-logic>` | `<signal>` |

## Key Differences

1. **Road Representation**:
   - OSM: Roads are ways with tags
   - SUMO: Roads are edges with explicit lanes
   - OpenDRIVE: Roads have detailed geometry and lane sections

2. **Lane Information**:
   - OSM: Implicit in way width and tags
   - SUMO: Explicit lane definitions
   - OpenDRIVE: Detailed lane properties and connectivity

3. **Traffic Control**:
   - OSM: Basic traffic signal tags
   - SUMO: Detailed traffic light logic
   - OpenDRIVE: Signal definitions with timing

## Conversion Focus

1. **OSM → SUMO**:
   - Convert ways to edges
   - Infer lane information from tags
   - Map traffic signals to tl-logic

2. **SUMO → OpenDRIVE**:
   - Convert edges to roads
   - Map lanes to lane sections
   - Convert traffic light logic to signals 