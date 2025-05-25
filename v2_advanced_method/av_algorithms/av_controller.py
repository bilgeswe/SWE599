"""Main autonomous vehicle controller that integrates all AV algorithms."""

import math
from dataclasses import dataclass
from typing import List, Tuple, Dict, Optional
from enum import Enum

from .lane_follower import LaneFollower, LaneInfo, VehicleState as LaneVehicleState
from .path_planner import PathPlanner, Node, Edge
from .traffic_light_handler import TrafficLightHandler, TrafficLight, TrafficLightState

class AVState(Enum):
    """Possible states of the autonomous vehicle."""
    INITIALIZING = "initializing"
    PLANNING = "planning"
    FOLLOWING_LANE = "following_lane"
    STOPPING = "stopping"
    COMPLETED = "completed"
    ERROR = "error"

@dataclass
class AVVehicleState:
    """Extended vehicle state for the AV controller."""
    x: float
    y: float
    heading: float
    speed: float
    acceleration: float
    current_lane: str
    target_lane: str
    state: AVState

class AVController:
    """Main autonomous vehicle controller that integrates all AV algorithms."""
    
    def __init__(self,
                 lookahead_distance: float = 50.0,
                 yellow_light_duration: float = 3.0,
                 min_distance_to_stop: float = 50.0,
                 max_deceleration: float = 3.0):
        """Initialize the AV controller.
        
        Args:
            lookahead_distance: Distance to look ahead for path planning (meters)
            yellow_light_duration: Duration of yellow light in seconds
            min_distance_to_stop: Minimum distance needed to stop safely
            max_deceleration: Maximum deceleration in m/s^2
        """
        self.lane_follower = LaneFollower(lookahead_distance)
        self.path_planner = PathPlanner()
        self.traffic_light_handler = TrafficLightHandler(
            yellow_light_duration,
            min_distance_to_stop,
            max_deceleration
        )
        self.vehicle_state = None
        self.current_path = []
        self.current_path_points = []
        self.current_lane_info = None
        
    def initialize_vehicle(self, x: float, y: float, heading: float, 
                         current_lane: str) -> None:
        """Initialize the vehicle state.
        
        Args:
            x: Initial x position
            y: Initial y position
            heading: Initial heading angle in radians
            current_lane: ID of the current lane
        """
        self.vehicle_state = AVVehicleState(
            x=x,
            y=y,
            heading=heading,
            speed=0.0,
            acceleration=0.0,
            current_lane=current_lane,
            target_lane=current_lane,
            state=AVState.INITIALIZING
        )
        
    def set_destination(self, target_lane: str) -> None:
        """Set the destination lane for the vehicle.
        
        Args:
            target_lane: ID of the target lane
        """
        if not self.vehicle_state:
            raise ValueError("Vehicle not initialized")
            
        self.vehicle_state.target_lane = target_lane
        self.vehicle_state.state = AVState.PLANNING
        
    def update_vehicle_state(self, x: float, y: float, heading: float, 
                           speed: float, acceleration: float) -> None:
        """Update the current vehicle state.
        
        Args:
            x: Current x position
            y: Current y position
            heading: Current heading angle in radians
            speed: Current speed in m/s
            acceleration: Current acceleration in m/s^2
        """
        if not self.vehicle_state:
            raise ValueError("Vehicle not initialized")
            
        self.vehicle_state.x = x
        self.vehicle_state.y = y
        self.vehicle_state.heading = heading
        self.vehicle_state.speed = speed
        self.vehicle_state.acceleration = acceleration
        
    def update_traffic_light(self, light_id: str, state: TrafficLightState,
                           time_in_phase: float) -> None:
        """Update the state of a traffic light.
        
        Args:
            light_id: ID of the traffic light
            state: New state
            time_in_phase: Time spent in current phase
        """
        self.traffic_light_handler.update_traffic_light(light_id, state, time_in_phase)
        
    def get_control_commands(self) -> Tuple[float, float]:
        """Get the control commands for the vehicle.
        
        Returns:
            Tuple of (steering_angle, target_speed)
        """
        if not self.vehicle_state:
            raise ValueError("Vehicle not initialized")
            
        # Convert AV vehicle state to lane follower vehicle state
        lane_vehicle_state = LaneVehicleState(
            x=self.vehicle_state.x,
            y=self.vehicle_state.y,
            heading=self.vehicle_state.heading,
            speed=self.vehicle_state.speed,
            acceleration=self.vehicle_state.acceleration
        )
        
        # Check if we need to plan a new path
        if (self.vehicle_state.state == AVState.PLANNING or 
            not self.current_path or 
            self.vehicle_state.current_lane != self.current_path[0]):
            try:
                self.current_path = self.path_planner.find_path(
                    self.vehicle_state.current_lane,
                    self.vehicle_state.target_lane
                )
                self.current_path_points = self.path_planner.get_lane_sequence(self.current_path)
                self.vehicle_state.state = AVState.FOLLOWING_LANE
            except ValueError as e:
                self.vehicle_state.state = AVState.ERROR
                raise e
                
        # Check for traffic lights
        nearest_light = self.traffic_light_handler.get_nearest_traffic_light(lane_vehicle_state)
        if nearest_light:
            if self.traffic_light_handler.should_stop(lane_vehicle_state, nearest_light):
                self.vehicle_state.state = AVState.STOPPING
                target_speed = self.traffic_light_handler.calculate_target_speed(
                    lane_vehicle_state, nearest_light)
                return 0.0, target_speed
                
        # Get current lane info
        if not self.current_lane_info:
            # This should be populated from the road network data
            self.current_lane_info = LaneInfo(
                id=self.vehicle_state.current_lane,
                width=3.5,  # Default lane width
                speed_limit=50.0,  # Default speed limit
                shape=self.current_path_points
            )
            
        # Calculate control commands
        steering_angle = self.lane_follower.calculate_steering_angle(
            lane_vehicle_state, self.current_lane_info)
        target_speed = self.lane_follower.calculate_speed(
            lane_vehicle_state, self.current_lane_info)
            
        return steering_angle, target_speed
        
    def update_lane_info(self, lane_id: str, width: float, speed_limit: float,
                        shape: List[Tuple[float, float]]) -> None:
        """Update the information about the current lane.
        
        Args:
            lane_id: ID of the lane
            width: Width of the lane in meters
            speed_limit: Speed limit in m/s
            shape: List of (x,y) points defining lane centerline
        """
        self.current_lane_info = LaneInfo(
            id=lane_id,
            width=width,
            speed_limit=speed_limit,
            shape=shape
        )
        
    def add_road_network_node(self, node: Node) -> None:
        """Add a node to the road network.
        
        Args:
            node: Node to add
        """
        self.path_planner.add_node(node)
        
    def add_road_network_edge(self, edge: Edge) -> None:
        """Add an edge to the road network.
        
        Args:
            edge: Edge to add
        """
        self.path_planner.add_edge(edge)
        
    def add_traffic_light(self, traffic_light: TrafficLight) -> None:
        """Add a traffic light to the handler.
        
        Args:
            traffic_light: Traffic light to add
        """
        self.traffic_light_handler.add_traffic_light(traffic_light) 