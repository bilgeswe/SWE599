# Detailed Format Analysis: SUMO to OpenDRIVE

## 1. SUMO Network Format (.net.xml)

### 1.1 Core Elements

#### Location and Projection
```xml
<location>
    <orig x="-73.9875" y="40.7498" />  <!-- Origin point -->
    <proj>!</proj>                      <!-- Projection string -->
    <boundary .../>                     <!-- Network boundaries -->
</location>
```

#### Edges (Roads)
```xml
<edge id="edge_0" from="junction1" to="junction2" priority="1" type="highway.primary">
    <lane id="edge_0_0" index="0" speed="13.89" length="100.00" shape="x1,y1 x2,y2"/>
    <lane id="edge_0_1" index="1" speed="13.89" length="100.00" shape="x3,y3 x4,y4"/>
</edge>
```
Key attributes:
- `id`: Unique identifier
- `from/to`: Connected junction IDs
- `priority`: Road priority level
- `type`: Road classification

#### Lanes
```xml
<lane id="edge_0_0" index="0" speed="13.89" length="100.00" shape="x1,y1 x2,y2">
    <param key="width" value="3.2"/>
    <neigh lane="edge_0_1"/>
</lane>
```
Key attributes:
- `id`: Unique identifier
- `index`: Lane position (0 = rightmost)
- `speed`: Maximum speed (m/s)
- `length`: Lane length
- `shape`: Geometry points

#### Junctions
```xml
<junction id="junction1" type="priority" x="100.00" y="100.00" incLanes="edge_1_0 edge_2_0" intLanes="...">
    <request index="0" response="0" foes="0" cont="0"/>
</junction>
```
Key attributes:
- `id`: Unique identifier
- `type`: Junction type (priority, traffic_light, etc.)
- `x,y`: Position
- `incLanes`: Incoming lanes

#### Traffic Lights
```xml
<tlLogic id="tl_0" type="static" programID="0" offset="0">
    <phase duration="31" state="GGggrrrrGGggrrrr"/>
    <phase duration="4"  state="yyggrrrryyggrrrr"/>
</tlLogic>
```

### 1.2 Geometric Representation
- Uses x,y coordinates for all elements
- Lane shapes defined by polylines
- Junction shapes defined by internal lanes
- Elevation (z) supported but optional

## 2. OpenDRIVE Format (.xodr)

### 2.1 Core Elements

#### Header
```xml
<OpenDRIVE>
    <header revMajor="1" revMinor="7" name="" version="1.00" date="2024-01-01" north="0.0" south="0.0" east="0.0" west="0.0">
        <geoReference>...</geoReference>
    </header>
</OpenDRIVE>
```

#### Roads
```xml
<road name="Road1" length="100.0" id="1" junction="-1">
    <link>
        <predecessor elementType="road" elementId="0" contactPoint="end"/>
        <successor elementType="junction" elementId="2"/>
    </link>
    <planView>
        <geometry s="0.0" x="0.0" y="0.0" hdg="0.0" length="100.0">
            <line/>
        </geometry>
    </planView>
    <lanes>
        <laneSection s="0.0">
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

#### Junctions
```xml
<junction name="Junction1" id="2">
    <connection id="0" incomingRoad="1" connectingRoad="3" contactPoint="start">
        <laneLink from="-1" to="-1"/>
    </connection>
</junction>
```

### 2.2 Geometric Representation
- Uses absolute coordinates for road reference lines
- Complex geometry types (line, spiral, arc, polynomial)
- Explicit lane width profiles
- Detailed elevation and banking profiles

## 3. Key Mapping Relationships

### 3.1 Road Network Elements

| SUMO Element | OpenDRIVE Element | Mapping Notes |
|--------------|-------------------|---------------|
| `<edge>` | `<road>` | Direct mapping, needs geometry conversion |
| `<lane>` | `<lane>` in `<laneSection>` | Convert index to OpenDRIVE ID system |
| `<junction>` | `<junction>` | Create connecting roads for each path |
| `<tlLogic>` | `<signal>` | Convert phases to signal plans |

### 3.2 Geometry Conversion

#### Lane Geometry
1. SUMO: Uses shape attribute with polyline
```xml
<lane shape="0,0 10,0 20,5"/>
```

2. OpenDRIVE: Uses reference line + width
```xml
<geometry s="0.0" x="0.0" y="0.0" hdg="0.0" length="20.0">
    <line/>
</geometry>
<width sOffset="0.0" a="3.5" b="0.0" c="0.0" d="0.0"/>
```

### 3.3 Critical Conversion Challenges

1. **Reference Line Calculation**
   - SUMO: Individual lane shapes
   - OpenDRIVE: Single reference line with offsets

2. **Junction Handling**
   - SUMO: Simple node with connections
   - OpenDRIVE: Complex junction with connecting roads

3. **Lane Numbering**
   - SUMO: Index-based (0, 1, 2...)
   - OpenDRIVE: Signed (-3, -2, -1, 1, 2, 3)

4. **Traffic Signals**
   - SUMO: Program-based phases
   - OpenDRIVE: Physical signal objects

## 4. Implementation Strategy

### 4.1 Processing Pipeline
1. Parse SUMO network
2. Extract road topology
3. Calculate reference lines
4. Generate OpenDRIVE roads
5. Process junctions
6. Add traffic signals
7. Validate geometry

### 4.2 Required Geometric Calculations
1. Reference line extraction from lane shapes
2. Lane offset calculations
3. Junction connection geometry
4. Heading calculations
5. Length parameterization

### 4.3 Validation Requirements
1. Topology preservation
2. Geometric continuity
3. Junction connectivity
4. Lane connections
5. Signal placement 