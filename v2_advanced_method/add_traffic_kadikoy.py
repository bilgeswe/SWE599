#!/usr/bin/env python3
"""
🚦 Kadıköy Traffic Generator for Advanced V2 Pipeline
====================================================

This script generates realistic traffic patterns for Kadıköy district, Istanbul.
Kadıköy is known for:
- Ferry terminal with high passenger traffic
- Commercial areas with shopping districts
- Metro and bus connections
- Cultural venues and restaurants
- Mixed residential and commercial zones

This creates intelligent traffic flows that reflect real Kadıköy usage patterns.
"""

import xml.etree.ElementTree as ET
import random
import os


def extract_edges_from_sumo_network(network_file):
    """Extract real edge IDs from SUMO network file"""
    
    print(f"📊 Extracting edges from {network_file}...")
    
    try:
        tree = ET.parse(network_file)
        root = tree.getroot()
        
        edges = []
        junctions = []
        
        for edge in root.findall('edge'):
            edge_id = edge.get('id')
            if edge_id and not edge_id.startswith(':'):  # Skip internal edges
                from_node = edge.get('from')
                to_node = edge.get('to')
                
                # Get edge priority/type
                priority = edge.get('priority', '1')
                edge_type = edge.get('type', 'default')
                
                edges.append({
                    'id': edge_id,
                    'from': from_node,
                    'to': to_node,
                    'priority': int(priority),
                    'type': edge_type
                })
        
        for junction in root.findall('junction'):
            junction_id = junction.get('id')
            if junction_id and not junction_id.startswith(':'):
                x = float(junction.get('x', 0))
                y = float(junction.get('y', 0))
                
                junctions.append({
                    'id': junction_id,
                    'x': x,
                    'y': y
                })
        
        print(f"✅ Found {len(edges)} edges and {len(junctions)} junctions")
        return edges, junctions
        
    except Exception as e:
        print(f"❌ Error extracting edges: {e}")
        return [], []


def categorize_kadikoy_areas(edges, junctions):
    """Categorize edges based on Kadıköy geographic features"""
    
    areas = {
        'ferry_terminal': [],
        'commercial_center': [],
        'metro_station': [],
        'moda_residential': [],
        'fenerbahce': [],
        'main_streets': [],
        'local_streets': []
    }
    
    for edge in edges:
        edge_id = edge['id']
        priority = edge['priority']
        
        # Categorize based on edge characteristics
        if priority >= 7:  # Major roads
            areas['main_streets'].append(edge_id)
        elif priority >= 5:  # Secondary roads
            if 'ferry' in edge_id.lower() or 'iskele' in edge_id.lower():
                areas['ferry_terminal'].append(edge_id)
            elif 'metro' in edge_id.lower() or 'kadikoy' in edge_id.lower():
                areas['metro_station'].append(edge_id)
            elif 'moda' in edge_id.lower():
                areas['moda_residential'].append(edge_id)
            elif 'fenerbahce' in edge_id.lower():
                areas['fenerbahce'].append(edge_id)
            else:
                areas['commercial_center'].append(edge_id)
        else:  # Local streets
            areas['local_streets'].append(edge_id)
    
    # If categorization by name doesn't work, distribute evenly
    if not any(areas[key] for key in ['ferry_terminal', 'commercial_center', 'metro_station']):
        print("📍 Using position-based categorization for Kadıköy areas...")
        main_edges = areas['main_streets']
        
        # Distribute main edges across key areas
        areas['ferry_terminal'] = main_edges[:len(main_edges)//5]
        areas['commercial_center'] = main_edges[len(main_edges)//5:2*len(main_edges)//5]
        areas['metro_station'] = main_edges[2*len(main_edges)//5:3*len(main_edges)//5]
        areas['moda_residential'] = main_edges[3*len(main_edges)//5:4*len(main_edges)//5]
        areas['fenerbahce'] = main_edges[4*len(main_edges)//5:]
    
    # Print area statistics
    for area, edge_list in areas.items():
        print(f"🏛️ {area}: {len(edge_list)} edges")
    
    return areas


def generate_kadikoy_routes():
    """Generate traffic routes for Kadıköy simulation"""
    
    # Load SUMO network
    network_file = "kadikoy_network.net.xml"
    
    if not os.path.exists(network_file):
        print(f"❌ Network file not found: {network_file}")
        print("Please run the main Kadıköy pipeline first.")
        return False
    
    # Extract network data
    edges, junctions = extract_edges_from_sumo_network(network_file)
    
    if not edges:
        print("❌ No edges found in network")
        return False
    
    # Categorize areas
    areas = categorize_kadikoy_areas(edges, junctions)
    
    # Define Kadıköy-specific traffic patterns
    traffic_patterns = [
        # Morning rush - Ferry to Metro/Commercial
        {
            'name': 'Ferry to Metro (Morning)',
            'from_areas': ['ferry_terminal'],
            'to_areas': ['metro_station', 'commercial_center'],
            'vehicles': 200,
            'peak_hours': [7, 8, 9],
            'vehicle_types': ['car', 'bus', 'taxi']
        },
        
        # Reverse commute - Metro to Ferry
        {
            'name': 'Metro to Ferry (Evening)',
            'from_areas': ['metro_station', 'commercial_center'],
            'to_areas': ['ferry_terminal'],
            'vehicles': 180,
            'peak_hours': [17, 18, 19],
            'vehicle_types': ['car', 'bus', 'taxi']
        },
        
        # Commercial traffic
        {
            'name': 'Commercial Activity',
            'from_areas': ['commercial_center'],
            'to_areas': ['moda_residential', 'fenerbahce'],
            'vehicles': 150,
            'peak_hours': [12, 13, 14, 20, 21],
            'vehicle_types': ['car', 'delivery', 'taxi']
        },
        
        # Local residential traffic
        {
            'name': 'Moda Local Traffic',
            'from_areas': ['moda_residential'],
            'to_areas': ['commercial_center', 'ferry_terminal'],
            'vehicles': 100,
            'peak_hours': [10, 11, 15, 16],
            'vehicle_types': ['car', 'taxi']
        },
        
        # Fenerbahçe area traffic
        {
            'name': 'Fenerbahçe Traffic',
            'from_areas': ['fenerbahce'],
            'to_areas': ['commercial_center', 'metro_station'],
            'vehicles': 120,
            'peak_hours': [9, 10, 16, 17],
            'vehicle_types': ['car', 'bus']
        }
    ]
    
    # Generate routes XML
    routes_content = '''<?xml version="1.0" encoding="UTF-8"?>
<routes xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="http://sumo.dlr.de/xsd/routes_file.xsd">

    <!-- Vehicle Types for Kadıköy District -->
    <vType id="car" accel="2.6" decel="4.5" sigma="0.5" length="4.5" maxSpeed="50" color="1,1,0"/>
    <vType id="bus" accel="1.2" decel="4.0" sigma="0.3" length="12.0" maxSpeed="40" color="0,1,0"/>
    <vType id="taxi" accel="2.8" decel="5.0" sigma="0.3" length="4.2" maxSpeed="55" color="1,1,1"/>
    <vType id="delivery" accel="2.0" decel="4.0" sigma="0.4" length="6.0" maxSpeed="45" color="0.5,0.3,0"/>
    
    <!-- Traffic Routes for Kadıköy -->
'''
    
    vehicle_id = 0
    total_vehicles = 0
    
    for pattern in traffic_patterns:
        print(f"\n🚗 Generating {pattern['name']}...")
        
        # Get source and destination edges
        source_edges = []
        for area in pattern['from_areas']:
            source_edges.extend(areas.get(area, []))
        
        dest_edges = []
        for area in pattern['to_areas']:
            dest_edges.extend(areas.get(area, []))
        
        if not source_edges or not dest_edges:
            print(f"⚠️ Skipping {pattern['name']} - no valid edges")
            continue
        
        # Generate vehicles for this pattern
        for i in range(pattern['vehicles']):
            # Select vehicle type
            vehicle_type = random.choice(pattern['vehicle_types'])
            
            # Select source and destination
            source_edge = random.choice(source_edges)
            dest_edge = random.choice(dest_edges)
            
            # Calculate departure time based on peak hours
            peak_hour = random.choice(pattern['peak_hours'])
            departure_time = peak_hour * 3600 + random.randint(0, 3600)  # Within the hour
            
            # Add some randomness to avoid all vehicles starting together
            departure_time += random.randint(0, 300)  # Up to 5 minutes variance
            
            routes_content += f'''    <vehicle id="kadikoy_{vehicle_id}" type="{vehicle_type}" depart="{departure_time}">
        <route edges="{source_edge} {dest_edge}"/>
    </vehicle>
'''
            
            vehicle_id += 1
            total_vehicles += 1
    
    routes_content += "\n</routes>"
    
    # Write routes file
    routes_file = "kadikoy_routes.rou.xml"
    with open(routes_file, 'w', encoding='utf-8') as f:
        f.write(routes_content)
    
    # Generate SUMO configuration
    config_content = '''<?xml version="1.0" encoding="UTF-8"?>
<configuration xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="http://sumo.dlr.de/xsd/sumoConfiguration.xsd">

    <input>
        <net-file value="kadikoy_network.net.xml"/>
        <route-files value="kadikoy_routes.rou.xml"/>
    </input>

    <time>
        <begin value="0"/>
        <end value="86400"/>
        <step-length value="1"/>
    </time>

    <processing>
        <time-to-teleport value="300"/>
        <max-depart-delay value="900"/>
        <routing-algorithm value="dijkstra"/>
    </processing>

    <report>
        <verbose value="true"/>
        <no-step-log value="false"/>
        <log-file value="kadikoy_simulation.log"/>
    </report>
    
    <random_number>
        <seed value="23423"/>
    </random_number>

    <gui_only>
        <gui-settings-file value="gui-settings.xml"/>
    </gui_only>

</configuration>'''
    
    config_file = "kadikoy_simulation.sumocfg"
    with open(config_file, 'w', encoding='utf-8') as f:
        f.write(config_content)
    
    # Create GUI settings for better visualization
    gui_settings = '''<?xml version="1.0" encoding="UTF-8"?>
<viewsettings>
    <viewport zoom="500" x="50" y="50"/>
    <delay value="100"/>
    <scheme name="real world"/>
</viewsettings>'''
    
    with open("gui-settings.xml", 'w') as f:
        f.write(gui_settings)
    
    print(f"\n✅ Kadıköy traffic generation complete!")
    print(f"📊 Generated {total_vehicles} vehicles across {len(traffic_patterns)} traffic patterns")
    print(f"📁 Files created:")
    print(f"   🚗 Routes: {routes_file}")
    print(f"   ⚙️ Config: {config_file}")
    print(f"   🎨 GUI Settings: gui-settings.xml")
    print(f"\n🚀 Launch simulation: sumo-gui {config_file}")
    
    return True


if __name__ == "__main__":
    success = generate_kadikoy_routes()
    if success:
        print("\n🎉 Kadıköy traffic system ready!")
        print("🏛️ Enjoy your professional AV simulation in historic Kadıköy!")
    else:
        print("\n❌ Traffic generation failed. Please check the setup.") 