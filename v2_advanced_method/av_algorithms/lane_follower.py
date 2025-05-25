"""Lane following algorithm for autonomous vehicles."""

import math
import numpy as np
from dataclasses import dataclass
from typing import List, Tuple, Optional

@dataclass
class VehicleState:
    """Represents the current state of the vehicle."""
    x: float  # x position
    y: float  # y position
    heading: float  # heading angle in radians
    speed: float  # current speed in m/s
    acceleration: float  # current acceleration in m/s^2

@dataclass
class LaneInfo:
    """Represents information about a lane."""
    id: str
    width: float
    speed_limit: float
    shape: List[Tuple[float, float]]  # List of (x,y) points defining lane centerline

class LaneFollower:
    """Implements lane following behavior for autonomous vehicles."""
    
    def __init__(self, lookahead_distance: float = 50.0):
        """Initialize the lane follower.
        
        Args:
            lookahead_distance: Distance to look ahead for path planning (meters)
        """
        self.lookahead_distance = lookahead_distance
        self.lateral_error = 0.0
        self.heading_error = 0.0
        
    def find_closest_point(self, vehicle_state: VehicleState, lane: LaneInfo) -> Tuple[float, float]:
        """Find the closest point on the lane centerline to the vehicle.
        
        Args:
            vehicle_state: Current state of the vehicle
            lane: Information about the current lane
            
        Returns:
            Tuple of (x, y) coordinates of the closest point
        """
        min_dist = float('inf')
        closest_point = None
        
        for point in lane.shape:
            dist = math.sqrt((point[0] - vehicle_state.x)**2 + 
                           (point[1] - vehicle_state.y)**2)
            if dist < min_dist:
                min_dist = dist
                closest_point = point
                
        return closest_point
    
    def calculate_lateral_error(self, vehicle_state: VehicleState, lane: LaneInfo) -> float:
        """Calculate the lateral error (distance from lane centerline).
        
        Args:
            vehicle_state: Current state of the vehicle
            lane: Information about the current lane
            
        Returns:
            Lateral error in meters (positive if vehicle is to the right of centerline)
        """
        closest_point = self.find_closest_point(vehicle_state, lane)
        
        # Calculate vector from closest point to vehicle
        dx = vehicle_state.x - closest_point[0]
        dy = vehicle_state.y - closest_point[1]
        
        # Calculate perpendicular distance
        lane_heading = self.calculate_lane_heading(closest_point, lane)
        lateral_error = dx * math.sin(lane_heading) - dy * math.cos(lane_heading)
        
        self.lateral_error = lateral_error
        return lateral_error
    
    def calculate_lane_heading(self, point: Tuple[float, float], lane: LaneInfo) -> float:
        """Calculate the heading of the lane at a given point.
        
        Args:
            point: (x,y) coordinates of the point
            lane: Information about the current lane
            
        Returns:
            Lane heading in radians
        """
        # Find the next point in the lane shape
        point_idx = lane.shape.index(point)
        if point_idx < len(lane.shape) - 1:
            next_point = lane.shape[point_idx + 1]
            dx = next_point[0] - point[0]
            dy = next_point[1] - point[1]
            return math.atan2(dy, dx)
        else:
            # If at the end of the lane, use the previous heading
            prev_point = lane.shape[point_idx - 1]
            dx = point[0] - prev_point[0]
            dy = point[1] - prev_point[1]
            return math.atan2(dy, dx)
    
    def calculate_heading_error(self, vehicle_state: VehicleState, lane: LaneInfo) -> float:
        """Calculate the heading error between vehicle and lane.
        
        Args:
            vehicle_state: Current state of the vehicle
            lane: Information about the current lane
            
        Returns:
            Heading error in radians
        """
        closest_point = self.find_closest_point(vehicle_state, lane)
        lane_heading = self.calculate_lane_heading(closest_point, lane)
        
        # Calculate heading error (normalized to [-pi, pi])
        heading_error = lane_heading - vehicle_state.heading
        heading_error = math.atan2(math.sin(heading_error), math.cos(heading_error))
        
        self.heading_error = heading_error
        return heading_error
    
    def calculate_steering_angle(self, vehicle_state: VehicleState, lane: LaneInfo) -> float:
        """Calculate the required steering angle for lane following.
        
        Args:
            vehicle_state: Current state of the vehicle
            lane: Information about the current lane
            
        Returns:
            Steering angle in radians (positive for right turn)
        """
        # Calculate errors
        lateral_error = self.calculate_lateral_error(vehicle_state, lane)
        heading_error = self.calculate_heading_error(vehicle_state, lane)
        
        # PID controller parameters
        kp_lateral = 0.1  # Proportional gain for lateral error
        kp_heading = 0.5  # Proportional gain for heading error
        
        # Calculate steering angle
        steering_angle = (kp_lateral * lateral_error + 
                         kp_heading * heading_error)
        
        # Limit steering angle to reasonable range
        max_steering = math.radians(45)  # 45 degrees
        return max(-max_steering, min(max_steering, steering_angle))
    
    def calculate_speed(self, vehicle_state: VehicleState, lane: LaneInfo) -> float:
        """Calculate the target speed based on lane properties and vehicle state.
        
        Args:
            vehicle_state: Current state of the vehicle
            lane: Information about the current lane
            
        Returns:
            Target speed in m/s
        """
        # Consider lane speed limit
        target_speed = lane.speed_limit
        
        # Reduce speed based on curvature
        closest_point = self.find_closest_point(vehicle_state, lane)
        lane_heading = self.calculate_lane_heading(closest_point, lane)
        
        # Calculate curvature (simplified)
        if len(lane.shape) > 2:
            point_idx = lane.shape.index(closest_point)
            if point_idx > 0 and point_idx < len(lane.shape) - 1:
                prev_point = lane.shape[point_idx - 1]
                next_point = lane.shape[point_idx + 1]
                
                # Calculate angle between segments
                v1 = (closest_point[0] - prev_point[0], 
                      closest_point[1] - prev_point[1])
                v2 = (next_point[0] - closest_point[0], 
                      next_point[1] - closest_point[1])
                
                angle = math.atan2(v2[1], v2[0]) - math.atan2(v1[1], v1[0])
                angle = math.atan2(math.sin(angle), math.cos(angle))
                
                # Reduce speed based on angle
                speed_factor = 1.0 - min(1.0, abs(angle) / math.pi)
                target_speed *= speed_factor
        
        return target_speed 