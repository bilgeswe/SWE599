"""Simulation of AV controller on Üsküdar road network."""

import os
import sys
import json
import math
import xml.etree.ElementTree as ET
from typing import List, Tuple
import numpy as np

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.av_algorithms.av_controller import AVController, AVVehicleState, AVState
from src.av_algorithms.path_planner import Node, Edge, PathPlanner
from src.av_algorithms.traffic_light_handler import TrafficLight, TrafficLightState
from src.av_algorithms.visualization import AVVisualizer
from src.utils.coordinate_transform import transform_sumo_coordinates, transform_sumo_network

def load_uskudar_network() -> Tuple[List[Node], List[Edge], List[TrafficLight]]:
    """Load the processed Üsküdar road network data.
    
    Returns:
        Tuple of (nodes, edges, traffic_lights)
    """
    # Load the processed data from the output directory
    output_dir = "output/uskudar"
    
    # Load nodes
    with open(os.path.join(output_dir, "nodes.json"), 'r') as f:
        nodes_data = json.load(f)
        nodes = [Node(**node) for node in nodes_data]
    
    # Load edges
    with open(os.path.join(output_dir, "edges.json"), 'r') as f:
        edges_data = json.load(f)
        edges = [Edge(**edge) for edge in edges_data]
    
    # Load traffic lights
    with open(os.path.join(output_dir, "traffic_lights.json"), 'r') as f:
        traffic_lights_data = json.load(f)
        traffic_lights = [TrafficLight(**light) for light in traffic_lights_data]
    
    return nodes, edges, traffic_lights

def test_reachability(controller, start_lane_id, goal_lane_id):
    """Test if goal is reachable from start using BFS"""
    if start_lane_id not in controller.path_planner.lane_to_edge:
        return False, f"Start lane {start_lane_id} not found"
    if goal_lane_id not in controller.path_planner.lane_to_edge:
        return False, f"Goal lane {goal_lane_id} not found"
        
    start_edge = controller.path_planner.lane_to_edge[start_lane_id]
    goal_edge = controller.path_planner.lane_to_edge[goal_lane_id]
    
    visited = set()
    queue = [start_edge]
    
    while queue:
        current_edge_id = queue.pop(0)
        if current_edge_id == goal_edge:
            return True, "Path exists"
            
        if current_edge_id in visited:
            continue
        visited.add(current_edge_id)
        
        current_edge = controller.path_planner.edges[current_edge_id]
        
        # Check neighbors via nodes
        for node_id in [current_edge.from_node, current_edge.to_node]:
            if node_id in controller.path_planner.nodes:
                node = controller.path_planner.nodes[node_id]
                if hasattr(node, 'edges'):
                    for neighbor_edge in node.edges:
                        neighbor_edge_id = neighbor_edge.id
                        if neighbor_edge_id not in visited:
                            queue.append(neighbor_edge_id)
    
    return False, f"No path found (visited {len(visited)} edges)"

def load_sumo_network_offset(sumo_net_path: str) -> Tuple[float, float]:
    """Load network offset from SUMO .net.xml file.
    
    Args:
        sumo_net_path: Path to SUMO network file
        
    Returns:
        Tuple of (offset_x, offset_y) from netOffset attribute
    """
    try:
        tree = ET.parse(sumo_net_path)
        root = tree.getroot()
        
        location_elem = root.find('location')
        if location_elem is not None:
            net_offset = location_elem.get('netOffset', '0.0,0.0')
            offset_x, offset_y = map(float, net_offset.split(','))
            print(f"Loaded network offset: ({offset_x}, {offset_y})")
            return offset_x, offset_y
        else:
            print("Warning: No location element found in SUMO network file")
            return 0.0, 0.0
            
    except Exception as e:
        print(f"Error loading network offset: {e}")
        return 0.0, 0.0

def simulate_vehicle_movement(controller: AVController, 
                            start_node: Node,
                            start_lane: str,
                            goal_lane: str,
                            edges: List[Edge],
                            time_step: float = 0.1,
                            max_time: float = 300.0) -> List[Tuple[float, float, float]]:
    """Simulate vehicle movement under AV control.
    
    Args:
        controller: AV controller instance
        start_node: Starting node
        start_lane: Starting lane
        goal_lane: Goal lane
        edges: List of edges in the road network
        time_step: Time step for simulation
        max_time: Maximum simulation time
        
    Returns:
        List of (x, y, heading) positions during simulation
    """
    # Initialize vehicle state
    controller.initialize_vehicle(
        x=start_node.x,
        y=start_node.y,
        heading=0.0,  # Initial heading will be set by path planner
        current_lane=start_lane
    )
    
    # Set destination to goal lane instead of node
    controller.set_destination(goal_lane)
    
    # Simulation loop
    positions = []
    current_time = 0.0
    
    # Initialize acceleration tracking
    acceleration = 0.0
    
    while current_time < max_time:
        # Get current vehicle state
        x = controller.vehicle_state.x
        y = controller.vehicle_state.y
        heading = controller.vehicle_state.heading
        current_speed = controller.vehicle_state.speed
        
        # Update vehicle state with current parameters
        controller.update_vehicle_state(x, y, heading, current_speed, acceleration)
        
        # Get control commands
        steering, speed = controller.get_control_commands()
        
        # Calculate acceleration
        acceleration = (speed - current_speed) / time_step if time_step > 0 else 0.0
        
        # Update position using simple kinematic model
        heading += steering * time_step
        x += speed * np.cos(heading) * time_step
        y += speed * np.sin(heading) * time_step
        
        # Update vehicle state
        controller.vehicle_state.x = x
        controller.vehicle_state.y = y
        controller.vehicle_state.heading = heading
        controller.vehicle_state.speed = speed
        
        # Record position
        positions.append((x, y, heading))
        
        # Check if destination reached
        if controller.vehicle_state.state == AVState.COMPLETED:
            print(f"Destination reached at time {current_time:.1f}s")
            break
        
        current_time += time_step
    
    return positions

def run_uskudar_simulation():
    """Run the AV simulation on Üsküdar road network."""
    print("Loading Üsküdar road network...")
    nodes, edges, traffic_lights = load_uskudar_network()
    
    # Load network offset for coordinate transformation
    sumo_net_path = "data/sumo/üsküdar__istanbul__turkey.net.xml"
    net_offset = load_sumo_network_offset(sumo_net_path)
    
    print(f"Loaded {len(nodes)} nodes, {len(edges)} edges, {len(traffic_lights)} traffic lights")
    
    # Debug: Check edge and lane information
    total_lanes = 0
    edges_with_lanes = 0
    for edge in edges:
        if edge.lanes and len(edge.lanes) > 0:
            edges_with_lanes += 1
            total_lanes += len(edge.lanes)
    
    print(f"Edges with lanes: {edges_with_lanes}/{len(edges)}")
    print(f"Total lanes: {total_lanes}")
    
    # Show a few examples of lanes
    if edges_with_lanes > 0:
        print("\nFirst few edges with lanes:")
        count = 0
        for edge in edges:
            if edge.lanes and len(edge.lanes) > 0 and count < 3:
                print(f"  Edge {edge.id}: lanes = {edge.lanes}")
                count += 1
    
    # Create AV controller and path planner
    print("\nInitializing AV controller...")
    controller = AVController()
    
    # Add debugging to check nodes and edges are connected properly
    for node in nodes:
        controller.path_planner.add_node(node)
    for edge in edges:
        controller.path_planner.add_edge(edge)
    
    # Manually connect edges to nodes (this fixes the connectivity issue)
    for edge in edges:
        from_node = controller.path_planner.nodes.get(edge.from_node)
        to_node = controller.path_planner.nodes.get(edge.to_node)
        
        if from_node:
            if not hasattr(from_node, 'edges'):
                from_node.edges = []
            from_node.edges.append(edge)
        
        if to_node:
            if not hasattr(to_node, 'edges'):
                to_node.edges = []
            to_node.edges.append(edge)
    
    print(f"\nPath planner has {len(controller.path_planner.lane_to_edge)} lanes registered")
    
    # Debug: Check connectivity issues
    print("\n=== CONNECTIVITY DEBUGGING ===")
    
    # Check if nodes have edges assigned
    nodes_with_edges = 0
    total_node_edges = 0
    for node_id, node in controller.path_planner.nodes.items():
        if hasattr(node, 'edges') and node.edges:
            nodes_with_edges += 1
            total_node_edges += len(node.edges)
    
    print(f"Nodes with edges: {nodes_with_edges}/{len(controller.path_planner.nodes)}")
    print(f"Total node-edge connections: {total_node_edges}")
    
    # Check edge-to-node connectivity
    edge_connections = 0
    for edge_id, edge in controller.path_planner.edges.items():
        if edge.from_node in controller.path_planner.nodes and edge.to_node in controller.path_planner.nodes:
            edge_connections += 1
    
    print(f"Valid edge connections: {edge_connections}/{len(controller.path_planner.edges)}")
    
    # Find nodes with outgoing edges (potential start points)
    start_candidates = []
    for node_id, node in controller.path_planner.nodes.items():
        if hasattr(node, 'edges') and node.edges:
            # Check if this node has outgoing edges
            outgoing_edges = [e for e in node.edges if e.from_node == node_id]
            if outgoing_edges:
                start_candidates.append((node_id, node, len(outgoing_edges)))
    
    print(f"\nNodes with outgoing edges: {len(start_candidates)}")
    
    if len(start_candidates) < 2:
        print("ERROR: Not enough nodes with outgoing edges for simulation")
        return
    
    # Sort by number of outgoing edges and pick start/end
    start_candidates.sort(key=lambda x: x[2], reverse=True)
    start_node_id, start_node, _ = start_candidates[0]
    end_node_id, end_node, _ = start_candidates[-1]
    
    print(f"Selected start node: {start_node_id} at ({start_node.x:.2f}, {start_node.y:.2f})")
    print(f"Selected end node: {end_node_id} at ({end_node.x:.2f}, {end_node.y:.2f})")
    
    # Find start and goal lanes
    start_lane = None
    goal_lane = None
    
    # Find a lane connected to start node (check both from and to)
    for edge in edges:
        if (edge.from_node == start_node_id or edge.to_node == start_node_id) and edge.lanes:
            start_lane = edge.lanes[0]
            print(f"Found start lane {start_lane} from edge {edge.id} (from: {edge.from_node}, to: {edge.to_node})")
            break
    
    # Find a lane connected to end node (check both from and to)
    for edge in edges:
        if (edge.from_node == end_node_id or edge.to_node == end_node_id) and edge.lanes:
            goal_lane = edge.lanes[0]
            print(f"Found goal lane {goal_lane} from edge {edge.id} (from: {edge.from_node}, to: {edge.to_node})")
            break
    
    # If still no lanes found, use any available lanes
    if not start_lane:
        for edge in edges:
            if edge.lanes:
                start_lane = edge.lanes[0]
                print(f"Fallback: using start lane {start_lane} from edge {edge.id}")
                break
    
    if not goal_lane:
        for edge in edges:
            if edge.lanes and edge.lanes[0] != start_lane:  # Different from start
                goal_lane = edge.lanes[0]
                print(f"Fallback: using goal lane {goal_lane} from edge {edge.id}")
                break
    
    if not start_lane or not goal_lane:
        print("ERROR: Could not find valid start or goal lanes")
        return
    
    print(f"Start lane: {start_lane}")
    print(f"Goal lane: {goal_lane}")
    
    # Check if lanes are in the path planner
    print(f"Start lane '{start_lane}' in path planner: {start_lane in controller.path_planner.lane_to_edge}")
    print(f"Goal lane '{goal_lane}' in path planner: {goal_lane in controller.path_planner.lane_to_edge}")
    
    # Test reachability before running simulation
    print("\n=== TESTING REACHABILITY ===")
    reachable, message = test_reachability(controller, start_lane, goal_lane)
    print(f"Reachability test: {message}")
    
    if not reachable:
        print("WARNING: Goal may not be reachable from start. Proceeding anyway...")
        # Try to find a different goal that is reachable
        print("Searching for reachable goal...")
        for edge in edges[:10]:  # Try first 10 edges
            if edge.lanes:
                test_goal = edge.lanes[0]
                if test_goal != start_lane:
                    reachable, _ = test_reachability(controller, start_lane, test_goal)
                    if reachable:
                        goal_lane = test_goal
                        print(f"Found reachable goal: {goal_lane}")
                        break
    
    # Run simulation with proper lane IDs
    positions = simulate_vehicle_movement(controller, start_node, start_lane, goal_lane, edges)
    
    # Transform coordinates for visualization
    print("\n=== TRANSFORMING COORDINATES ===")
    print(f"Original positions range: x=({min(p[0] for p in positions):.2f}, {max(p[0] for p in positions):.2f}), y=({min(p[1] for p in positions):.2f}, {max(p[1] for p in positions):.2f})")
    
    # Transform positions
    transformed_positions = transform_sumo_coordinates(positions, net_offset)
    print(f"Transformed positions range: lon=({min(p[0] for p in transformed_positions):.6f}, {max(p[0] for p in transformed_positions):.6f}), lat=({min(p[1] for p in transformed_positions):.6f}, {max(p[1] for p in transformed_positions):.6f})")
    
    # Transform network
    transformed_nodes, transformed_edges = transform_sumo_network(nodes, edges, net_offset)
    
    # Create visualization with transformed coordinates
    print("\n=== CREATING VISUALIZATION ===")
    visualizer = AVVisualizer(output_dir="output/uskudar/simulation")
    
    # Use transformed coordinates for visualization
    # Convert positions to lat/lon format for visualization (swap to lat, lon, heading)
    visualization_positions = [(lat, lon, heading) for lon, lat, heading in transformed_positions]
    
    visualizer.create_simulation_visualization(
        controller=controller,
        positions=visualization_positions,
        nodes=transformed_nodes,
        edges=transformed_edges,
        traffic_lights=traffic_lights
    )
    
    # Create summary
    visualizer.create_simulation_summary(controller, positions)
    
    print("\n=== SIMULATION COMPLETE ===")
    print(f"Simulated {len(positions)} time steps")
    print(f"Start position: ({positions[0][0]:.2f}, {positions[0][1]:.2f}) -> ({transformed_positions[0][0]:.6f}, {transformed_positions[0][1]:.6f})")
    print(f"End position: ({positions[-1][0]:.2f}, {positions[-1][1]:.2f}) -> ({transformed_positions[-1][0]:.6f}, {transformed_positions[-1][1]:.6f})")
    print("Visualization saved to output/uskudar/simulation/")

if __name__ == "__main__":
    run_uskudar_simulation() 