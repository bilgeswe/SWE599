"""Traffic light behavior algorithm for autonomous vehicles."""

import math
from dataclasses import dataclass
from typing import List, Dict, Tuple, Optional
from enum import Enum

class TrafficLightState(Enum):
    """Possible states of a traffic light."""
    RED = "red"
    YELLOW = "yellow"
    GREEN = "green"
    UNKNOWN = "unknown"

@dataclass
class TrafficLight:
    """Represents a traffic light with its properties."""
    id: str
    position: Tuple[float, float]
    state: TrafficLightState
    phases: List[Dict[str, str]]  # List of phase configurations
    current_phase: int
    time_in_phase: float
    cycle_time: float

@dataclass
class VehicleState:
    """Represents the current state of the vehicle."""
    x: float
    y: float
    speed: float
    acceleration: float
    heading: float

class TrafficLightHandler:
    """Handles traffic light behavior for autonomous vehicles."""
    
    def __init__(self, 
                 yellow_light_duration: float = 3.0,
                 min_distance_to_stop: float = 50.0,
                 max_deceleration: float = 3.0):
        """Initialize the traffic light handler.
        
        Args:
            yellow_light_duration: Duration of yellow light in seconds
            min_distance_to_stop: Minimum distance needed to stop safely
            max_deceleration: Maximum deceleration in m/s^2
        """
        self.yellow_light_duration = yellow_light_duration
        self.min_distance_to_stop = min_distance_to_stop
        self.max_deceleration = max_deceleration
        self.traffic_lights: Dict[str, TrafficLight] = {}
        
    def add_traffic_light(self, traffic_light: TrafficLight) -> None:
        """Add a traffic light to the handler.
        
        Args:
            traffic_light: Traffic light to add
        """
        self.traffic_lights[traffic_light.id] = traffic_light
        
    def update_traffic_light(self, light_id: str, state: TrafficLightState, 
                           time_in_phase: float) -> None:
        """Update the state of a traffic light.
        
        Args:
            light_id: ID of the traffic light
            state: New state
            time_in_phase: Time spent in current phase
        """
        if light_id in self.traffic_lights:
            light = self.traffic_lights[light_id]
            light.state = state
            light.time_in_phase = time_in_phase
            
            # Update phase if needed
            if time_in_phase >= light.phases[light.current_phase]["duration"]:
                light.current_phase = (light.current_phase + 1) % len(light.phases)
                light.time_in_phase = 0
                
    def get_nearest_traffic_light(self, vehicle_state: VehicleState) -> Optional[TrafficLight]:
        """Find the nearest traffic light to the vehicle.
        
        Args:
            vehicle_state: Current state of the vehicle
            
        Returns:
            Nearest traffic light or None if no traffic lights are nearby
        """
        nearest_light = None
        min_distance = float('inf')
        
        for light in self.traffic_lights.values():
            distance = math.sqrt(
                (light.position[0] - vehicle_state.x)**2 +
                (light.position[1] - vehicle_state.y)**2
            )
            if distance < min_distance:
                min_distance = distance
                nearest_light = light
                
        return nearest_light if min_distance < 100.0 else None
        
    def calculate_stopping_distance(self, speed: float) -> float:
        """Calculate the distance needed to stop at current speed.
        
        Args:
            speed: Current speed in m/s
            
        Returns:
            Distance needed to stop in meters
        """
        # Using constant deceleration model
        return (speed * speed) / (2 * self.max_deceleration)
        
    def should_stop(self, vehicle_state: VehicleState, 
                   traffic_light: TrafficLight) -> bool:
        """Determine if the vehicle should stop at the traffic light.
        
        Args:
            vehicle_state: Current state of the vehicle
            traffic_light: Traffic light to check
            
        Returns:
            True if the vehicle should stop, False otherwise
        """
        # Calculate distance to traffic light
        distance = math.sqrt(
            (traffic_light.position[0] - vehicle_state.x)**2 +
            (traffic_light.position[1] - vehicle_state.y)**2
        )
        
        # Calculate stopping distance
        stopping_distance = self.calculate_stopping_distance(vehicle_state.speed)
        
        # Check if we need to stop
        if traffic_light.state == TrafficLightState.RED:
            return distance < stopping_distance + self.min_distance_to_stop
            
        elif traffic_light.state == TrafficLightState.YELLOW:
            # Check if we can make it through the intersection
            time_to_intersection = distance / vehicle_state.speed if vehicle_state.speed > 0 else float('inf')
            return time_to_intersection > traffic_light.time_in_phase
            
        return False
        
    def calculate_target_speed(self, vehicle_state: VehicleState,
                             traffic_light: TrafficLight) -> float:
        """Calculate the target speed based on traffic light state.
        
        Args:
            vehicle_state: Current state of the vehicle
            traffic_light: Traffic light to check
            
        Returns:
            Target speed in m/s
        """
        if not self.should_stop(vehicle_state, traffic_light):
            return vehicle_state.speed
            
        # Calculate distance to traffic light
        distance = math.sqrt(
            (traffic_light.position[0] - vehicle_state.x)**2 +
            (traffic_light.position[1] - vehicle_state.y)**2
        )
        
        # Calculate time to stop
        time_to_stop = vehicle_state.speed / self.max_deceleration
        
        # Calculate target speed for smooth deceleration
        if distance > self.min_distance_to_stop:
            target_speed = math.sqrt(2 * self.max_deceleration * 
                                   (distance - self.min_distance_to_stop))
            return max(0, min(target_speed, vehicle_state.speed))
        else:
            return 0
            
    def predict_light_state(self, traffic_light: TrafficLight, 
                          time_ahead: float) -> TrafficLightState:
        """Predict the state of a traffic light at a future time.
        
        Args:
            traffic_light: Traffic light to check
            time_ahead: Time to look ahead in seconds
            
        Returns:
            Predicted state of the traffic light
        """
        current_phase = traffic_light.current_phase
        time_in_phase = traffic_light.time_in_phase + time_ahead
        
        # Find the phase that will be active
        while time_in_phase >= traffic_light.phases[current_phase]["duration"]:
            time_in_phase -= traffic_light.phases[current_phase]["duration"]
            current_phase = (current_phase + 1) % len(traffic_light.phases)
            
        # Get the state from the phase
        phase_state = traffic_light.phases[current_phase]["state"]
        
        # Convert phase state to TrafficLightState
        if "r" in phase_state.lower():
            return TrafficLightState.RED
        elif "y" in phase_state.lower():
            return TrafficLightState.YELLOW
        elif "g" in phase_state.lower():
            return TrafficLightState.GREEN
        else:
            return TrafficLightState.UNKNOWN 