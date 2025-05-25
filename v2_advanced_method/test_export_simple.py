#!/usr/bin/env python3
"""Simple test of OpenDRIVE and OpenSCENARIO exporters."""

import os
import sys
import json
from pathlib import Path

# Add src directory to path for imports
sys.path.append(str(Path(__file__).parent / "src"))

try:
    from exporters.opendrive_exporter import OpenDRIVEExporter
    from exporters.openscenario_exporter import OpenSCENARIOExporter
    print("✅ Exporters imported successfully!")
    
    # Create simple test data
    class TestNode:
        def __init__(self, node_id, x, y):
            self.id = node_id
            self.x = x
            self.y = y
            
    class TestEdge:
        def __init__(self, edge_id, from_node, to_node):
            self.id = edge_id
            self.from_node = from_node
            self.to_node = to_node
            self.lanes = [f"{edge_id}_0"]
            self.speed_limit = 13.89
            
    class TestTrafficLight:
        def __init__(self, tl_id, x, y):
            self.id = tl_id
            self.x = x
            self.y = y
    
    # Create test network
    nodes = [
        TestNode("n1", 0.0, 0.0),
        TestNode("n2", 100.0, 0.0),
        TestNode("n3", 100.0, 100.0)
    ]
    
    edges = [
        TestEdge("e1", "n1", "n2"),
        TestEdge("e2", "n2", "n3")
    ]
    
    traffic_lights = [
        TestTrafficLight("tl1", 50.0, 0.0)
    ]
    
    # Test trajectory data
    trajectory = [
        (0.0, 0.0, 0.0),
        (25.0, 0.0, 0.0),
        (50.0, 0.0, 0.0),
        (75.0, 0.0, 0.0),
        (100.0, 0.0, 1.57),
        (100.0, 25.0, 1.57),
        (100.0, 50.0, 1.57),
        (100.0, 75.0, 1.57),
        (100.0, 100.0, 1.57)
    ]
    
    # Create output directory
    output_dir = "test_export_output"
    os.makedirs(output_dir, exist_ok=True)
    
    # Test OpenDRIVE export
    print("\n🛣️  Testing OpenDRIVE export...")
    opendrive_exporter = OpenDRIVEExporter()
    opendrive_file = os.path.join(output_dir, "test_network.xodr")
    
    opendrive_exporter.export_network(
        nodes=nodes,
        edges=edges,
        traffic_lights=traffic_lights,
        output_path=opendrive_file,
        net_offset=(0.0, 0.0)
    )
    
    # Test OpenSCENARIO export
    print("🎬 Testing OpenSCENARIO export...")
    openscenario_exporter = OpenSCENARIOExporter()
    scenario_file = os.path.join(output_dir, "test_scenario.xosc")
    
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
        }
    }
    
    openscenario_exporter.export_simulation(
        simulation_data=simulation_data,
        vehicle_trajectory=trajectory,
        opendrive_file="test_network.xodr",
        output_path=scenario_file
    )
    
    print("\n✅ **Test Export Successful!**")
    print(f"📁 Files created in: {output_dir}/")
    print(f"🛣️  OpenDRIVE: test_network.xodr")
    print(f"🎬 OpenSCENARIO: test_scenario.xosc")
    
    # Check file sizes
    if os.path.exists(opendrive_file):
        size = os.path.getsize(opendrive_file)
        print(f"   OpenDRIVE file size: {size:,} bytes")
        
    if os.path.exists(scenario_file):
        size = os.path.getsize(scenario_file)
        print(f"   OpenSCENARIO file size: {size:,} bytes")
        
except Exception as e:
    print(f"❌ Test failed: {e}")
    import traceback
    traceback.print_exc() 