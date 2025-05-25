#!/usr/bin/env python3
"""
Export Üsküdar AV simulation to OpenDRIVE and OpenSCENARIO formats.
This creates industry-standard files that can be used with professional tools like:
- Unreal Engine OpenDRIVE plugin
- esmini
- CARLA
- IPG CarMaker
- etc.
"""

import os
import sys
import json
from pathlib import Path

# Add src directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from av_algorithms.path_planner import PathPlanner, Node, Edge
from av_algorithms.traffic_light_handler import TrafficLightHandler, TrafficLight
from av_algorithms.av_controller import AVController
from av_algorithms.simulation_engine import SimulationEngine
from av_algorithms.vehicle_state import VehicleState
from utils.coordinate_transform import CoordinateTransformer
from exporters.opendrive_exporter import OpenDRIVEExporter
from exporters.openscenario_exporter import OpenSCENARIOExporter


def load_network_data(base_path: str):
    """Load the Üsküdar network data."""
    print("Loading Üsküdar network data...")
    
    # Load network files
    nodes_file = os.path.join(base_path, "uskudar_nodes.json")
    edges_file = os.path.join(base_path, "uskudar_edges.json")
    lanes_file = os.path.join(base_path, "uskudar_lanes.json")
    traffic_lights_file = os.path.join(base_path, "uskudar_traffic_lights.json")
    
    # Load and parse data
    with open(nodes_file, 'r') as f:
        nodes_data = json.load(f)
    with open(edges_file, 'r') as f:
        edges_data = json.load(f)
    with open(traffic_lights_file, 'r') as f:
        traffic_lights_data = json.load(f)
        
    # Create objects
    nodes = [Node(node_id=n['id'], x=n['x'], y=n['y']) for n in nodes_data]
    edges = [Edge(edge_id=e['id'], from_node=e['from'], to_node=e['to'], 
                  lanes=e.get('lanes', []), speed_limit=e.get('maxspeed', 13.89),
                  shape=e.get('shape'), length=e.get('length')) for e in edges_data]
    traffic_lights = [TrafficLight(tl['id'], tl['x'], tl['y']) for tl in traffic_lights_data]
    
    return nodes, edges, traffic_lights


def run_simulation(nodes, edges, traffic_lights):
    """Run the AV simulation and collect trajectory data."""
    print("Running AV simulation...")
    
    # Apply coordinate transformation
    transformer = CoordinateTransformer()
    
    # Get network offset from SUMO data
    net_offset = (-668686.91, -4539963.74)  # From Üsküdar network
    transformer.set_projection_from_bounds(
        orig_boundary=(29.005960, 40.992201, 29.092133, 41.077708),
        net_offset=net_offset
    )
    
    # Transform coordinates
    for node in nodes:
        node.lat, node.lon = transformer.utm_to_latlon(node.x, node.y)
        
    # Create simulation components
    path_planner = PathPlanner(nodes, edges)
    traffic_handler = TrafficLightHandler(traffic_lights)
    
    # Find start and goal positions
    start_lane = "-662200253#0_0"  # Known good start lane
    goal_lane = "986023334#0_0"   # Known good goal lane
    
    print(f"Planning path from {start_lane} to {goal_lane}...")
    
    # Plan path
    path = path_planner.plan_path(start_lane, goal_lane)
    if not path:
        raise ValueError("Could not find path between start and goal")
        
    print(f"Path found with {len(path)} waypoints")
    
    # Create vehicle and controller
    initial_edge = next(e for e in edges if start_lane in e.lanes)
    start_node = next(n for n in nodes if n.id == initial_edge.from_node)
    
    vehicle_state = VehicleState(
        x=start_node.x, y=start_node.y, 
        heading=0.0, speed=0.0
    )
    
    controller = AVController(vehicle_state, traffic_handler)
    
    # Create simulation engine
    simulation = SimulationEngine(controller, path_planner, traffic_handler)
    
    # Run simulation
    print("Running simulation...")
    results = simulation.run_simulation(
        start_lane=start_lane,
        goal_lane=goal_lane, 
        time_limit=300.0,
        time_step=0.1
    )
    
    # Extract trajectory
    trajectory = []
    for step in results['steps']:
        trajectory.append((
            step['vehicle_state']['x'],
            step['vehicle_state']['y'], 
            step['vehicle_state']['heading']
        ))
        
    print(f"Simulation completed with {len(trajectory)} trajectory points")
    
    return trajectory, results, net_offset


def export_to_opendrive_scenario():
    """Main function to export Üsküdar simulation to OpenDRIVE/OpenSCENARIO."""
    
    # Paths
    base_path = "output/uskudar"
    export_path = "output/uskudar/opendrive_scenario"
    os.makedirs(export_path, exist_ok=True)
    
    try:
        # Load network data
        nodes, edges, traffic_lights = load_network_data(base_path)
        print(f"Loaded {len(nodes)} nodes, {len(edges)} edges, {len(traffic_lights)} traffic lights")
        
        # Run simulation
        trajectory, simulation_results, net_offset = run_simulation(nodes, edges, traffic_lights)
        
        # Export to OpenDRIVE
        print("\\nExporting to OpenDRIVE format...")
        opendrive_exporter = OpenDRIVEExporter()
        opendrive_file = os.path.join(export_path, "uskudar_network.xodr")
        
        opendrive_exporter.export_network(
            nodes=nodes,
            edges=edges, 
            traffic_lights=traffic_lights,
            output_path=opendrive_file,
            net_offset=net_offset
        )
        
        # Export to OpenSCENARIO
        print("\\nExporting to OpenSCENARIO format...")
        openscenario_exporter = OpenSCENARIOExporter()
        scenario_file = os.path.join(export_path, "uskudar_av_scenario.xosc")
        
        # Prepare simulation data
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
            'scenario_params': simulation_results.get('parameters', {})
        }
        
        openscenario_exporter.export_simulation(
            simulation_data=simulation_data,
            vehicle_trajectory=trajectory,
            opendrive_file="uskudar_network.xodr",  # Relative path
            output_path=scenario_file
        )
        
        # Create summary report
        summary_file = os.path.join(export_path, "export_summary.json")
        summary = {
            'export_timestamp': simulation_results.get('timestamp', 'unknown'),
            'network_stats': {
                'nodes': len(nodes),
                'edges': len(edges), 
                'traffic_lights': len(traffic_lights)
            },
            'simulation_stats': {
                'trajectory_points': len(trajectory),
                'simulation_time': len(trajectory) * 0.1,
                'path_length': simulation_results.get('total_distance', 0),
                'average_speed': simulation_results.get('average_speed', 0)
            },
            'files_generated': {
                'opendrive': os.path.basename(opendrive_file),
                'openscenario': os.path.basename(scenario_file),
                'summary': os.path.basename(summary_file)
            },
            'coordinate_info': {
                'net_offset': net_offset,
                'projection': "UTM Zone 35N",
                'datum': "WGS84"
            }
        }
        
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)
            
        # Print success message
        print(f"\\n✅ **Export completed successfully!**")
        print(f"📁 Files saved to: {export_path}")
        print(f"🛣️  OpenDRIVE: {os.path.basename(opendrive_file)}")
        print(f"🎬 OpenSCENARIO: {os.path.basename(scenario_file)}")
        print(f"📊 Summary: {os.path.basename(summary_file)}")
        print(f"\\n🚀 **Ready for use with:**")
        print("   • Unreal Engine OpenDRIVE plugin")
        print("   • esmini")
        print("   • CARLA")
        print("   • IPG CarMaker")
        print("   • And other OpenX-compliant tools!")
        
        return export_path
        
    except Exception as e:
        print(f"❌ Export failed: {e}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == "__main__":
    export_to_opendrive_scenario() 