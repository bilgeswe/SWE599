# Format Conversion Examples

## 1. Simple Road Segment

### SUMO Format
```xml
<edge id="e1" from="j1" to="j2" priority="1" type="highway.primary">
    <lane id="e1_0" index="0" speed="13.89" length="100.00" shape="0,0 100,0"/>
    <lane id="e1_1" index="1" speed="13.89" length="100.00" shape="0,3.2 100,3.2"/>
</edge>
```

### Equivalent OpenDRIVE Format
```xml
<road name="e1" length="100.0" id="1" junction="-1">
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
                    <width sOffset="0.0" a="3.2" b="0.0" c="0.0" d="0.0"/>
                    <speed sOffset="0.0" max="13.89"/>
                </lane>
                <lane id="-2" type="driving" level="false">
                    <width sOffset="0.0" a="3.2" b="0.0" c="0.0" d="0.0"/>
                    <speed sOffset="0.0" max="13.89"/>
                </lane>
            </right>
        </laneSection>
    </lanes>
</road>
```

## 2. Simple Junction

### SUMO Format
```xml
<junction id="j1" type="priority" x="100.00" y="100.00">
    <request index="0" response="0" foes="0"/>
</junction>
<edge id="e1" from="j1" to="j2">
    <lane id="e1_0" index="0" speed="13.89" shape="100,100 200,100"/>
</edge>
<edge id="e2" from="j3" to="j1">
    <lane id="e2_0" index="0" speed="13.89" shape="100,0 100,100"/>
</edge>
```

### Equivalent OpenDRIVE Format
```xml
<junction name="j1" id="1">
    <connection id="0" incomingRoad="2" connectingRoad="1" contactPoint="start">
        <laneLink from="-1" to="-1"/>
    </connection>
</junction>
<road name="e1" length="100.0" id="1" junction="-1">
    <link>
        <predecessor elementType="junction" elementId="1"/>
        <successor elementType="road" elementId="3" contactPoint="start"/>
    </link>
    <planView>
        <geometry s="0.0" x="100.0" y="100.0" hdg="0.0" length="100.0">
            <line/>
        </geometry>
    </planView>
    <lanes>
        <laneSection s="0.0">
            <right>
                <lane id="-1" type="driving" level="false">
                    <width sOffset="0.0" a="3.2" b="0.0" c="0.0" d="0.0"/>
                    <speed sOffset="0.0" max="13.89"/>
                </lane>
            </right>
        </laneSection>
    </lanes>
</road>
```

## 3. Traffic Light

### SUMO Format
```xml
<junction id="j1" type="traffic_light" x="100.00" y="100.00">
    <request index="0" response="0" foes="0"/>
</junction>
<tlLogic id="tl_j1" type="static" programID="0" offset="0">
    <phase duration="31" state="GGr"/>
    <phase duration="4" state="yyr"/>
    <phase duration="31" state="rrG"/>
    <phase duration="4" state="rry"/>
</tlLogic>
```

### Equivalent OpenDRIVE Format
```xml
<road name="r1" length="100.0" id="1" junction="-1">
    <signals>
        <signal s="50.0" t="-3.2" id="tl_j1" name="TrafficLight1" dynamic="yes" orientation="-" zOffset="5.0" type="1000001">
            <validity fromLane="-1" toLane="-2"/>
            <dependency id="tl_j1_2" type="synced"/>
        </signal>
    </signals>
    <signalReference s="50.0" t="-3.2" id="tl_j1" orientation="+"/>
</road>
```

## 4. Complex Geometry

### SUMO Format
```xml
<edge id="e1" from="j1" to="j2">
    <lane id="e1_0" shape="0,0 20,0 50,30 100,50"/>
</edge>
```

### Equivalent OpenDRIVE Format
```xml
<road name="e1" length="121.243" id="1" junction="-1">
    <planView>
        <geometry s="0.0" x="0.0" y="0.0" hdg="0.0" length="20.0">
            <line/>
        </geometry>
        <geometry s="20.0" x="20.0" y="0.0" hdg="0.0" length="50.0">
            <spiral curvStart="0.0" curvEnd="0.02"/>
        </geometry>
        <geometry s="70.0" x="50.0" y="30.0" hdg="0.927" length="51.243">
            <spiral curvStart="0.02" curvEnd="0.0"/>
        </geometry>
    </planView>
    <lanes>
        <laneSection s="0.0">
            <right>
                <lane id="-1" type="driving" level="false">
                    <width sOffset="0.0" a="3.2" b="0.0" c="0.0" d="0.0"/>
                </lane>
            </right>
        </laneSection>
    </lanes>
</road>
```

## Key Conversion Notes

1. **Lane Indexing**
   - SUMO: 0-based, positive indices
   - OpenDRIVE: Center is 0, negative for right, positive for left

2. **Geometry**
   - SUMO: Direct polyline coordinates
   - OpenDRIVE: Reference line with parametric geometry

3. **Traffic Signals**
   - SUMO: Logic-based with phases
   - OpenDRIVE: Physical objects with references

4. **Junctions**
   - SUMO: Node-based with connections
   - OpenDRIVE: Complex objects with connecting roads 