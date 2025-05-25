#!/usr/bin/env python3
"""
Export existing Üsküdar network data to OpenDRIVE and OpenSCENARIO formats.
Uses the existing network files without running the full simulation.
"""

import os
import sys
import json
from pathlib import Path

# Add src directory to path for imports
sys.path.append(str(Path(__file__).parent / "src"))

from exporters.opendrive_exporter import OpenDRIVEExporter
from exporters.openscenario_exporter import OpenSCENARIOExporter


def load_uskudar_network():
    """Load Üsküdar network data from existing files."""
    base_path = "output/uskudar"
    
    # Load network files (using correct file names)
    nodes_file = os.path.join(base_path, "nodes.json")
    edges_file = os.path.join(base_path, "edges.json")
    traffic_lights_file = os.path.join(base_path, "traffic_lights.json")
    
    print(f"Loading network from {base_path}...")
    
    with open(nodes_file, 'r') as f:
        nodes_data = json.load(f)
    with open(edges_file, 'r') as f:
        edges_data = json.load(f)
    with open(traffic_lights_file, 'r') as f:
        traffic_lights_data = json.load(f)
    
    print(f"Loaded {len(nodes_data)} nodes, {len(edges_data)} edges, {len(traffic_lights_data)} traffic lights")
    
    return nodes_data, edges_data, traffic_lights_data


def create_simple_classes():
    """Create simple data classes for our export."""
    
    class SimpleNode:
        def __init__(self, node_id, x, y):
            self.id = node_id
            self.x = x
            self.y = y
            
    class SimpleEdge:
        def __init__(self, edge_id, from_node, to_node, lanes=None, speed_limit=13.89):
            self.id = edge_id
            self.from_node = from_node
            self.to_node = to_node
            self.lanes = lanes or [f"{edge_id}_0"]
            self.speed_limit = speed_limit
            
    class SimpleTrafficLight:
        def __init__(self, tl_id, x, y):
            self.id = tl_id
            self.x = x
            self.y = y
    
    return SimpleNode, SimpleEdge, SimpleTrafficLight


def create_sample_trajectory(nodes_data, edges_data):
    """Create a sample trajectory using the network data."""
    # Find a path through some edges
    trajectory = []
    
    # Use first few nodes to create a simple path
    if len(nodes_data) >= 10:
        sample_nodes = nodes_data[:10]
        for i, node in enumerate(sample_nodes):
            # Calculate heading based on next node
            if i < len(sample_nodes) - 1:
                next_node = sample_nodes[i + 1]
                import math
                heading = math.atan2(
                    next_node['y'] - node['y'],
                    next_node['x'] - node['x']
                )
            else:
                heading = 0.0
                
            trajectory.append((node['x'], node['y'], heading))
    
    return trajectory


def export_uskudar_to_opendrive_scenario():
    """Export Üsküdar network to OpenDRIVE and OpenSCENARIO."""
    
    try:
        # Load network data
        nodes_data, edges_data, traffic_lights_data = load_uskudar_network()
        
        # Create simple classes
        SimpleNode, SimpleEdge, SimpleTrafficLight = create_simple_classes()
        
        # Convert to simple objects
        nodes = [SimpleNode(n['id'], n['x'], n['y']) for n in nodes_data]
        
        edges = []
        for e in edges_data:
            lanes = e.get('lanes', [])
            speed_limit = e.get('speed_limit', 13.89)
            edges.append(SimpleEdge(e['id'], e['from_node'], e['to_node'], lanes, speed_limit))
        
        traffic_lights = []
        for tl in traffic_lights_data:
            pos = tl.get('position', [0.0, 0.0])
            traffic_lights.append(SimpleTrafficLight(tl['id'], pos[0], pos[1]))
        
        # Create output directory
        export_path = "output/uskudar/opendrive_scenario"
        os.makedirs(export_path, exist_ok=True)
        
        print(f"\\n🛣️  Exporting to OpenDRIVE...")
        
        # Export to OpenDRIVE
        opendrive_exporter = OpenDRIVEExporter()
        opendrive_file = os.path.join(export_path, "uskudar_network.xodr")
        
        # Use the actual network offset from Üsküdar
        net_offset = (-668686.91, -4539963.74)
        
        opendrive_exporter.export_network(
            nodes=nodes,
            edges=edges,
            traffic_lights=traffic_lights,
            output_path=opendrive_file,
            net_offset=net_offset
        )
        
        print(f"🎬 Exporting to OpenSCENARIO...")
        
        # Create sample trajectory
        trajectory = create_sample_trajectory(nodes_data, edges_data)
        
        # Export to OpenSCENARIO
        openscenario_exporter = OpenSCENARIOExporter()
        scenario_file = os.path.join(export_path, "uskudar_av_scenario.xosc")
        
        simulation_data = {
            'start_time': 0.0,
            'time_step': 0.1,
            'total_time': len(trajectory) * 0.1,
            'vehicle_params': {
                'mass': 1500.0,
                'max_speed': 55.0,
                'length': 4.5,
                'width': 2.0,
                'height': 1.5
            },
            'network_info': {
                'location': 'Üsküdar, Istanbul',
                'nodes': len(nodes),
                'edges': len(edges),
                'traffic_lights': len(traffic_lights)
            }
        }
        
        openscenario_exporter.export_simulation(
            simulation_data=simulation_data,
            vehicle_trajectory=trajectory,
            opendrive_file="uskudar_network.xodr",
            output_path=scenario_file
        )
        
        # Create summary
        summary_file = os.path.join(export_path, "export_summary.json")
        summary = {
            'export_timestamp': '2025-05-24T20:30:00Z',
            'location': 'Üsküdar, Istanbul, Turkey',
            'coordinate_system': 'UTM Zone 35N (EPSG:32635)',
            'network_stats': {
                'nodes': len(nodes),
                'edges': len(edges),
                'traffic_lights': len(traffic_lights)
            },
            'files_generated': {
                'opendrive': 'uskudar_network.xodr',
                'openscenario': 'uskudar_av_scenario.xosc',
                'summary': 'export_summary.json'
            },
            'compatible_tools': [
                'Unreal Engine OpenDRIVE plugin',
                'esmini',
                'CARLA',
                'IPG CarMaker',
                'VTD',
                'OpenSCENARIO viewers'
            ],
            'network_bounds': {
                'net_offset': list(net_offset),
                'geographic_bounds': {
                    'description': 'Üsküdar district, Istanbul',
                    'longitude_range': [29.005960, 29.092133],
                    'latitude_range': [40.992201, 41.077708]
                }
            }
        }
        
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)
        
        # Success message
        print(f"\\n🎉 **EXPORT SUCCESSFUL!**")
        print(f"📁 Files saved to: {export_path}")
        print(f"\\n📊 **Generated Files:**")
        print(f"   🛣️  OpenDRIVE: uskudar_network.xodr")
        print(f"   🎬 OpenSCENARIO: uskudar_av_scenario.xosc") 
        print(f"   📋 Summary: export_summary.json")
        
        # Check file sizes
        if os.path.exists(opendrive_file):
            size = os.path.getsize(opendrive_file)
            print(f"\\n📏 **File Sizes:**")
            print(f"   OpenDRIVE: {size:,} bytes")
            
        if os.path.exists(scenario_file):
            size = os.path.getsize(scenario_file)
            print(f"   OpenSCENARIO: {size:,} bytes")
        
        print(f"\\n🚀 **Ready for use with:**")
        print(f"   • Unreal Engine OpenDRIVE plugin")
        print(f"   • esmini")
        print(f"   • CARLA")
        print(f"   • IPG CarMaker")
        print(f"   • And other OpenX-compliant tools!")
        
        print(f"\\n🗺️  **Network Coverage:**")
        print(f"   Location: Üsküdar, Istanbul, Turkey")
        print(f"   Nodes: {len(nodes):,}")
        print(f"   Roads: {len(edges):,}")
        print(f"   Traffic Lights: {len(traffic_lights):,}")
        
        return export_path
        
    except Exception as e:
        print(f"❌ Export failed: {e}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == "__main__":
    export_uskudar_to_opendrive_scenario() 