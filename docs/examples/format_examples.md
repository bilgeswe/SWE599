# Format Examples

This document provides examples of the different file formats used in the project.

## OSM Format Example

```xml
<?xml version="1.0" encoding="UTF-8"?>
<osm version="0.6" generator="osmium/1.14.0">
  <bounds minlat="41.0297" minlon="28.9724" maxlat="41.0697" maxlon="29.0324"/>
  
  <!-- Nodes -->
  <node id="1" lat="41.0497" lon="29.0024" version="1">
    <tag k="highway" v="traffic_signals"/>
  </node>
  
  <!-- Ways (Roads) -->
  <way id="1" version="1">
    <nd ref="1"/>
    <nd ref="2"/>
    <tag k="highway" v="primary"/>
    <tag k="lanes" v="2"/>
    <tag k="oneway" v="yes"/>
    <tag k="name" v="Bağdat Caddesi"/>
  </way>
</osm>
```

## SUMO Network Format Example

```xml
<?xml version="1.0" encoding="UTF-8"?>
<net version="1.0" junctionCornerDetail="5" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="http://sumo.dlr.de/xsd/net_file.xsd">
  <location netOffset="0.0,0.0" convBoundary="0.0,0.0,1000.0,1000.0" origBoundary="28.9724,41.0297,29.0324,41.0697" projParameter="+proj=utm +zone=35 +ellps=WGS84 +datum=WGS84 +units=m +no_defs"/>
  
  <!-- Edges (Roads) -->
  <edge id="1" from="1" to="2" priority="1" type="highway.primary">
    <lane id="1_0" index="0" speed="13.89" width="3.5" length="100.0" shape="0.0,0.0 100.0,0.0"/>
    <lane id="1_1" index="1" speed="13.89" width="3.5" length="100.0" shape="0.0,3.5 100.0,3.5"/>
  </edge>
  
  <!-- Junctions -->
  <junction id="1" type="priority" x="0.0" y="0.0" incLanes="1_0 1_1" intLanes="" shape="0.0,0.0 0.0,3.5 3.5,3.5 3.5,0.0"/>
  
  <!-- Traffic Lights -->
  <tlLogic id="1" type="static" programID="0" offset="0">
    <phase duration="31" state="GG"/>
    <phase duration="6" state="yy"/>
    <phase duration="31" state="rr"/>
    <phase duration="6" state="rr"/>
  </tlLogic>
</net>
```

## OpenDRIVE Format Example

```xml
<?xml version="1.0" encoding="UTF-8"?>
<OpenDRIVE>
  <header revMajor="1" revMinor="4" name="Kadıköy Network" version="1.00" date="2024-05-05" north="41.0697" south="41.0297" east="29.0324" west="28.9724">
    <geoReference><![CDATA[+proj=utm +zone=35 +ellps=WGS84 +datum=WGS84 +units=m +no_defs]]></geoReference>
  </header>
  
  <!-- Roads -->
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
    <elevationProfile>
      <elevation s="0.0" a="0.0" b="0.0" c="0.0" d="0.0"/>
    </elevationProfile>
    <lanes>
      <laneSection s="0.0">
        <left>
          <lane id="1" type="driving" level="false">
            <link/>
            <width sOffset="0.0" a="3.5" b="0.0" c="0.0" d="0.0"/>
            <roadMark sOffset="0.0" type="solid" weight="standard" color="standard" width="0.15"/>
          </lane>
        </left>
        <center>
          <lane id="0" type="none" level="false">
            <link/>
            <roadMark sOffset="0.0" type="broken" weight="standard" color="standard" width="0.15"/>
          </lane>
        </center>
        <right>
          <lane id="-1" type="driving" level="false">
            <link/>
            <width sOffset="0.0" a="3.5" b="0.0" c="0.0" d="0.0"/>
            <roadMark sOffset="0.0" type="solid" weight="standard" color="standard" width="0.15"/>
          </lane>
        </right>
      </laneSection>
    </lanes>
  </road>
  
  <!-- Junctions -->
  <junction id="1" name="Intersection 1">
    <connection id="1" incomingRoad="1" connectingRoad="2" contactPoint="start">
      <laneLink from="1" to="1"/>
      <laneLink from="-1" to="-1"/>
    </connection>
  </junction>
</OpenDRIVE>
```

## Conversion Examples

### OSM to SUMO Conversion
```bash
# Basic conversion
python src/converter/osm_to_sumo.py data/networks/kadıköy.osm data/networks/kadıköy.net.xml

# With additional options
python src/converter/osm_to_sumo.py data/networks/kadıköy.osm data/networks/kadıköy.net.xml \
  --geometry.remove \
  --roundabouts.guess \
  --junctions.join \
  --tls.guess-signals
```

### SUMO to OpenDRIVE Conversion
```bash
# Basic conversion
python src/converter/sumo_to_xodr.py data/networks/kadıköy.net.xml data/networks/kadıköy.xodr

# With validation
python src/converter/advanced_sumo_to_xodr.py --validate data/networks/kadıköy.net.xml
```

## Visualization Examples

### SUMO GUI
```bash
# View network
sumo-gui -n data/networks/kadıköy.net.xml

# View with traffic
sumo-gui -n data/networks/kadıköy.net.xml -r data/networks/kadıköy.rou.xml
```

### Interactive Map
```bash
# Create interactive visualization
python src/visualization/visualize_with_folium.py data/networks/kadıköy.osm

# View in browser
open data/visualizations/kadıköy_interactive.html
```

## Notes

- All examples use the Kadıköy network as a reference
- File paths are relative to the project root
- Make sure to have the required dependencies installed
- Check the documentation for more detailed examples 