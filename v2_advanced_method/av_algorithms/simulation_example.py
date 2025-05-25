"""Example simulation demonstrating the AV controller in action."""

import math
import time
from typing import List, Tuple
import numpy as np

from .av_controller import AVController, AVState
from .path_planner import Node, Edge
from .traffic_light_handler import TrafficLight, TrafficLightState
from .visualization import AVVisualizer

def create_simple_road_network() -> Tuple[List[Node], List[Edge], List[TrafficLight]]:
    """Create a simple road network for simulation.
    
    Returns:
        Tuple of (nodes, edges, traffic_lights)
    """
    # Create nodes (intersections)
    nodes = [
        Node("n1", 0.0, 0.0, ["e1", "e2"]),
        Node("n2", 100.0, 0.0, ["e1", "e3"]),
        Node("n3", 100.0, 100.0, ["e2", "e3", "e4"]),
        Node("n4", 0.0, 100.0, ["e2", "e4"])
    ]
    
    # Create edges (road segments)
    edges = [
        Edge("e1", "n1", "n2", 100.0, 50.0, ["l1", "l2"]),  # Horizontal road
        Edge("e2", "n1", "n3", 141.4, 50.0, ["l3", "l4"]),  # Diagonal road
        Edge("e3", "n2", "n3", 100.0, 50.0, ["l5", "l6"]),  # Vertical road
        Edge("e4", "n3", "n4", 100.0, 50.0, ["l7", "l8"])   # Horizontal road
    ]
    
    # Create traffic lights
    traffic_lights = [
        TrafficLight(
            id="tl1",
            position=(50.0, 0.0),  # Middle of horizontal road
            state=TrafficLightState.RED,
            phases=[
                {"state": "r", "duration": 30.0},
                {"state": "g", "duration": 30.0},
                {"state": "y", "duration": 3.0}
            ],
            current_phase=0,
            time_in_phase=0.0,
            cycle_time=63.0
        ),
        TrafficLight(
            id="tl2",
            position=(100.0, 50.0),  # Middle of vertical road
            state=TrafficLightState.GREEN,
            phases=[
                {"state": "g", "duration": 30.0},
                {"state": "y", "duration": 3.0},
                {"state": "r", "duration": 30.0}
            ],
            current_phase=0,
            time_in_phase=0.0,
            cycle_time=63.0
        )
    ]
    
    return nodes, edges, traffic_lights

def simulate_vehicle_movement(controller: AVController, 
                            target_position: Tuple[float, float],
                            time_step: float = 0.1,
                            max_simulation_time: float = 60.0) -> List[Tuple[float, float, float]]:
    """Simulate vehicle movement under AV control.
    
    Args:
        controller: AV controller instance
        target_position: Target (x, y) position
        time_step: Simulation time step in seconds
        max_simulation_time: Maximum simulation time in seconds
        
    Returns:
        List of (x, y, heading) positions during simulation
    """
    positions = []
    current_time = 0.0
    
    while current_time < max_simulation_time:
        # Get control commands
        steering_angle, target_speed = controller.get_control_commands()
        
        # Update vehicle state based on control commands
        vehicle_state = controller.vehicle_state
        heading = vehicle_state.heading + steering_angle * time_step
        speed = target_speed
        
        # Update position
        x = vehicle_state.x + speed * math.cos(heading) * time_step
        y = vehicle_state.y + speed * math.sin(heading) * time_step
        
        # Update controller state
        controller.update_vehicle_state(x, y, heading, speed, 0.0)
        
        # Record position
        positions.append((x, y, heading))
        
        # Check if we've reached the target
        distance_to_target = math.sqrt(
            (x - target_position[0])**2 + 
            (y - target_position[1])**2
        )
        if distance_to_target < 1.0:  # Within 1 meter of target
            break
            
        current_time += time_step
        
    return positions

def run_simulation():
    """Run the AV simulation example."""
    # Create road network
    nodes, edges, traffic_lights = create_simple_road_network()
    
    # Initialize AV controller
    controller = AVController()
    
    # Add road network to controller
    for node in nodes:
        controller.add_road_network_node(node)
    for edge in edges:
        controller.add_road_network_edge(edge)
    for light in traffic_lights:
        controller.add_traffic_light(light)
        
    # Initialize vehicle at start position
    controller.initialize_vehicle(
        x=0.0,
        y=0.0,
        heading=math.radians(45),  # Point towards diagonal road
        current_lane="l3"  # Start on diagonal road
    )
    
    # Set destination
    controller.set_destination("l7")  # Target lane on horizontal road
    
    # Update lane information
    controller.update_lane_info(
        lane_id="l3",
        width=3.5,
        speed_limit=50.0,
        shape=[(0.0, 0.0), (50.0, 50.0), (100.0, 100.0)]
    )
    
    # Create visualizer
    visualizer = AVVisualizer()
    
    # Run simulation
    print("Starting simulation...")
    positions = simulate_vehicle_movement(
        controller,
        target_position=(50.0, 100.0),  # Target position
        time_step=0.1,
        max_simulation_time=60.0
    )
    
    # Create visualizations
    visualizer.create_simulation_visualization(
        controller,
        positions,
        nodes,
        edges,
        traffic_lights
    )
    
    # Create simulation summary
    visualizer.create_simulation_summary(controller, positions)
    
    # Print simulation results
    print(f"\nSimulation completed in {len(positions) * 0.1:.1f} seconds")
    print(f"Final position: ({positions[-1][0]:.1f}, {positions[-1][1]:.1f})")
    print(f"Final heading: {math.degrees(positions[-1][2]):.1f} degrees")
    
    # Print vehicle states during simulation
    print("\nVehicle states during simulation:")
    for i, (x, y, heading) in enumerate(positions):
        if i % 10 == 0:  # Print every second
            print(f"Time {i * 0.1:.1f}s: Position ({x:.1f}, {y:.1f}), "
                  f"Heading {math.degrees(heading):.1f}°")

if __name__ == "__main__":
    run_simulation() 