"""OpenSCENARIO exporter for converting AV simulations to OpenSCENARIO XML format."""

import xml.etree.ElementTree as ET
from xml.dom import minidom
from typing import List, Dict, Tuple, Optional, Any
import math
from datetime import datetime

# Use try-catch for imports to handle different contexts
try:
    from av_algorithms.path_planner import Node, Edge  
    from av_algorithms.traffic_light_handler import TrafficLight
except ImportError:
    # Fallback for when running from different directory
    import sys
    from pathlib import Path
    sys.path.append(str(Path(__file__).parent.parent.parent))
    from av_algorithms.path_planner import Node, Edge  
    from av_algorithms.traffic_light_handler import TrafficLight


class OpenSCENARIOExporter:
    """Exports AV simulation data to OpenSCENARIO XML format."""
    
    def __init__(self):
        """Initialize the OpenSCENARIO exporter."""
        self.entities = {}
        self.scenario_actions = []
        
    def export_simulation(self, 
                         simulation_data: Dict[str, Any],
                         vehicle_trajectory: List[Tuple[float, float, float]],
                         opendrive_file: str,
                         output_path: str) -> str:
        """Export AV simulation to OpenSCENARIO format.
        
        Args:
            simulation_data: Dictionary containing simulation parameters
            vehicle_trajectory: List of (x, y, heading) positions over time
            opendrive_file: Path to the corresponding OpenDRIVE file
            output_path: Path to save the OpenSCENARIO file
            
        Returns:
            Path to the exported OpenSCENARIO file
        """
        # Create root OpenSCENARIO element
        root = ET.Element("OpenSCENARIO")
        
        # Add file header
        self._add_file_header(root)
        
        # Add parameter declarations
        self._add_parameter_declarations(root, simulation_data)
        
        # Add catalog locations
        self._add_catalog_locations(root)
        
        # Add road network (reference to OpenDRIVE)
        self._add_road_network(root, opendrive_file)
        
        # Add entities (vehicles, pedestrians, etc.)
        self._add_entities(root, simulation_data)
        
        # Add storyboard (scenario logic)
        self._add_storyboard(root, vehicle_trajectory, simulation_data)
        
        # Write to file
        self._write_xml(root, output_path)
        
        return output_path
        
    def _add_file_header(self, root: ET.Element):
        """Add OpenSCENARIO file header."""
        file_header = ET.SubElement(root, "FileHeader")
        file_header.set("revMajor", "1")
        file_header.set("revMinor", "1")
        file_header.set("date", datetime.now().isoformat())
        file_header.set("description", "Uskudar AV Simulation Scenario")
        file_header.set("name", "Uskudar_AV_Scenario")
        file_header.set("author", "SWE599_AV_Simulation")
        
    def _add_parameter_declarations(self, root: ET.Element, simulation_data: Dict[str, Any]):
        """Add parameter declarations."""
        param_declarations = ET.SubElement(root, "ParameterDeclarations")
        
        # Add simulation parameters as scenario parameters
        params = [
            ("EgoVehicleSpeed", "13.89", "m/s", "Initial speed of ego vehicle"),
            ("WeatherCondition", "clear", "enum", "Weather condition"),
            ("TimeOfDay", "12:00:00", "string", "Time of day for simulation"),
            ("TrafficDensity", "normal", "enum", "Traffic density level")
        ]
        
        for name, value, param_type, description in params:
            param_decl = ET.SubElement(param_declarations, "ParameterDeclaration")
            param_decl.set("name", name)
            param_decl.set("parameterType", param_type)
            param_decl.set("value", value)
            
    def _add_catalog_locations(self, root: ET.Element):
        """Add catalog locations (references to vehicle, pedestrian catalogs)."""
        catalog_locations = ET.SubElement(root, "CatalogLocations")
        
        # Vehicle catalog
        vehicle_catalog = ET.SubElement(catalog_locations, "VehicleCatalog")
        directory = ET.SubElement(vehicle_catalog, "Directory")
        directory.set("path", "./Catalogs/Vehicles")
        
        # Pedestrian catalog  
        pedestrian_catalog = ET.SubElement(catalog_locations, "PedestrianCatalog")
        directory = ET.SubElement(pedestrian_catalog, "Directory")
        directory.set("path", "./Catalogs/Pedestrians")
        
        # Misc object catalog
        misc_catalog = ET.SubElement(catalog_locations, "MiscObjectCatalog")
        directory = ET.SubElement(misc_catalog, "Directory")
        directory.set("path", "./Catalogs/MiscObjects")
        
    def _add_road_network(self, root: ET.Element, opendrive_file: str):
        """Add road network reference."""
        road_network = ET.SubElement(root, "RoadNetwork")
        
        # Logic file (OpenDRIVE)
        logic_file = ET.SubElement(road_network, "LogicFile")
        logic_file.set("filepath", opendrive_file)
        
        # Scene graph file (optional - for 3D visualization)
        # scene_graph = ET.SubElement(road_network, "SceneGraphFile")
        # scene_graph.set("filepath", "./SceneGraph/uskudar_scene.osgb")
        
    def _add_entities(self, root: ET.Element, simulation_data: Dict[str, Any]):
        """Add scenario entities (vehicles, pedestrians)."""
        entities = ET.SubElement(root, "Entities")
        
        # Add ego vehicle (our AV)
        self._add_ego_vehicle(entities, simulation_data)
        
        # Add traffic vehicles (if any)
        # self._add_traffic_vehicles(entities, simulation_data)
        
    def _add_ego_vehicle(self, entities: ET.Element, simulation_data: Dict[str, Any]):
        """Add the ego vehicle (autonomous vehicle)."""
        scenario_object = ET.SubElement(entities, "ScenarioObject")
        scenario_object.set("name", "EgoVehicle")
        
        # Catalog reference for vehicle properties
        catalog_ref = ET.SubElement(scenario_object, "CatalogReference")
        catalog_ref.set("catalogName", "VehicleCatalog")
        catalog_ref.set("entryName", "car_white")  # Standard vehicle model
        
        # Alternative: Inline vehicle definition
        # vehicle = ET.SubElement(scenario_object, "Vehicle")
        # vehicle.set("name", "EgoVehicle")
        # vehicle.set("vehicleCategory", "car")
        
        # properties = ET.SubElement(vehicle, "Properties")
        # properties.set("mass", "1500.0")
        # properties.set("maxSpeed", "55.0")
        
        # bounding_box = ET.SubElement(vehicle, "BoundingBox")
        # center = ET.SubElement(bounding_box, "Center")
        # center.set("x", "1.3")
        # center.set("y", "0.0") 
        # center.set("z", "0.75")
        # dimensions = ET.SubElement(bounding_box, "Dimensions")
        # dimensions.set("width", "2.0")
        # dimensions.set("length", "4.5")
        # dimensions.set("height", "1.5")
        
    def _add_storyboard(self, root: ET.Element, 
                       vehicle_trajectory: List[Tuple[float, float, float]], 
                       simulation_data: Dict[str, Any]):
        """Add scenario storyboard with init and story elements."""
        storyboard = ET.SubElement(root, "Storyboard")
        
        # Add init actions
        self._add_init_actions(storyboard, vehicle_trajectory, simulation_data)
        
        # Add story (main scenario logic)
        self._add_story(storyboard, vehicle_trajectory, simulation_data)
        
        # Add stop trigger
        self._add_stop_trigger(storyboard)
        
    def _add_init_actions(self, storyboard: ET.Element, 
                         vehicle_trajectory: List[Tuple[float, float, float]],
                         simulation_data: Dict[str, Any]):
        """Add initialization actions."""
        init = ET.SubElement(storyboard, "Init")
        
        # Actions for ego vehicle
        actions = ET.SubElement(init, "Actions")
        
        # Private action for ego vehicle
        private = ET.SubElement(actions, "Private")
        private.set("entityRef", "EgoVehicle")
        
        # Private action - initial position
        private_action = ET.SubElement(private, "PrivateAction")
        
        teleport_action = ET.SubElement(private_action, "TeleportAction")
        position = ET.SubElement(teleport_action, "Position")
        
        # Use first position from trajectory as start position
        if vehicle_trajectory:
            start_x, start_y, start_heading = vehicle_trajectory[0]
            
            world_position = ET.SubElement(position, "WorldPosition")
            world_position.set("x", f"{start_x:.6f}")
            world_position.set("y", f"{start_y:.6f}")
            world_position.set("z", "0.0")
            world_position.set("h", f"{start_heading:.6f}")
            world_position.set("p", "0.0")
            world_position.set("r", "0.0")
            
        # Private action - initial speed
        private_action_speed = ET.SubElement(private, "PrivateAction")
        
        longitudinal_action = ET.SubElement(private_action_speed, "LongitudinalAction")
        speed_action = ET.SubElement(longitudinal_action, "SpeedAction")
        
        speed_action_dynamics = ET.SubElement(speed_action, "SpeedActionDynamics")
        speed_action_dynamics.set("dynamicsShape", "step")
        speed_action_dynamics.set("value", "0.0")
        speed_action_dynamics.set("dynamicsDimension", "time")
        
        speed_target = ET.SubElement(speed_action, "SpeedTarget")
        absolute_speed = ET.SubElement(speed_target, "AbsoluteSpeed")
        absolute_speed.set("value", "13.89")  # 50 km/h
        
    def _add_story(self, storyboard: ET.Element,
                  vehicle_trajectory: List[Tuple[float, float, float]],
                  simulation_data: Dict[str, Any]):
        """Add main story with vehicle trajectory."""
        story = ET.SubElement(storyboard, "Story")
        story.set("name", "AVPathFollowingStory")
        
        # Create act for path following
        act = ET.SubElement(story, "Act")
        act.set("name", "PathFollowingAct")
        
        # Create maneuver group
        maneuver_group = ET.SubElement(act, "ManeuverGroup")
        maneuver_group.set("maximumExecutionCount", "1")
        maneuver_group.set("name", "EgoVehicleManeuverGroup")
        
        # Actors (assign ego vehicle to this maneuver group)
        actors = ET.SubElement(maneuver_group, "Actors")
        actors.set("selectTriggeringEntities", "false")
        
        entity_ref = ET.SubElement(actors, "EntityRef")
        entity_ref.set("entityRef", "EgoVehicle")
        
        # Create maneuver for path following
        maneuver = ET.SubElement(maneuver_group, "Maneuver")
        maneuver.set("name", "PathFollowingManeuver")
        
        # Create event for trajectory following
        event = ET.SubElement(maneuver, "Event")
        event.set("name", "FollowTrajectoryEvent")
        event.set("priority", "overwrite")
        
        # Start trigger - immediately
        start_trigger = ET.SubElement(event, "StartTrigger")
        condition_group = ET.SubElement(start_trigger, "ConditionGroup")
        condition = ET.SubElement(condition_group, "Condition")
        condition.set("name", "StartCondition")
        condition.set("delay", "0.0")
        condition.set("conditionEdge", "rising")
        
        by_value_condition = ET.SubElement(condition, "ByValueCondition")
        simulation_time_condition = ET.SubElement(by_value_condition, "SimulationTimeCondition")
        simulation_time_condition.set("value", "0.0")
        simulation_time_condition.set("rule", "greaterThan")
        
        # Action - trajectory following
        action = ET.SubElement(event, "Action")
        action.set("name", "FollowTrajectoryAction")
        
        private_action = ET.SubElement(action, "PrivateAction")
        routing_action = ET.SubElement(private_action, "RoutingAction")
        
        # For now, use a simple follow trajectory action
        # In a full implementation, this would contain the actual trajectory points
        follow_trajectory_action = ET.SubElement(routing_action, "FollowTrajectoryAction")
        
        # Trajectory definition (simplified)
        trajectory = ET.SubElement(follow_trajectory_action, "Trajectory")
        trajectory.set("name", "EgoVehicleTrajectory")
        trajectory.set("closed", "false")
        
        # Add trajectory shape with key points (sample every 10th point to keep manageable)
        shape = ET.SubElement(trajectory, "Shape")
        
        sample_interval = max(1, len(vehicle_trajectory) // 50)  # Max 50 points
        for i, (x, y, heading) in enumerate(vehicle_trajectory[::sample_interval]):
            vertex = ET.SubElement(shape, "Vertex")
            vertex.set("time", f"{i * sample_interval * 0.1:.1f}")  # Assuming 0.1s time steps
            
            position = ET.SubElement(vertex, "Position")
            world_position = ET.SubElement(position, "WorldPosition")
            world_position.set("x", f"{x:.6f}")
            world_position.set("y", f"{y:.6f}")
            world_position.set("z", "0.0")
            world_position.set("h", f"{heading:.6f}")
            world_position.set("p", "0.0")
            world_position.set("r", "0.0")
            
        # Act start trigger
        act_start_trigger = ET.SubElement(act, "StartTrigger")
        act_condition_group = ET.SubElement(act_start_trigger, "ConditionGroup")
        act_condition = ET.SubElement(act_condition_group, "Condition")
        act_condition.set("name", "ActStartCondition")
        act_condition.set("delay", "0.0")
        act_condition.set("conditionEdge", "rising")
        
        act_by_value = ET.SubElement(act_condition, "ByValueCondition")
        act_sim_time = ET.SubElement(act_by_value, "SimulationTimeCondition")
        act_sim_time.set("value", "0.0")
        act_sim_time.set("rule", "greaterThan")
        
    def _add_stop_trigger(self, storyboard: ET.Element):
        """Add stop trigger for scenario completion."""
        stop_trigger = ET.SubElement(storyboard, "StopTrigger")
        
        condition_group = ET.SubElement(stop_trigger, "ConditionGroup")
        condition = ET.SubElement(condition_group, "Condition")
        condition.set("name", "EndCondition")
        condition.set("delay", "0.0")
        condition.set("conditionEdge", "rising")
        
        # Stop after simulation time
        by_value_condition = ET.SubElement(condition, "ByValueCondition")
        simulation_time_condition = ET.SubElement(by_value_condition, "SimulationTimeCondition")
        simulation_time_condition.set("value", "300.0")  # 5 minutes max
        simulation_time_condition.set("rule", "greaterThan")
        
    def _write_xml(self, root: ET.Element, output_path: str):
        """Write XML to file with proper formatting."""
        # Convert to string
        rough_string = ET.tostring(root, 'unicode')
        
        # Parse and pretty print
        reparsed = minidom.parseString(rough_string)
        pretty_string = reparsed.toprettyxml(indent="  ")
        
        # Remove extra blank lines
        lines = [line for line in pretty_string.split('\n') if line.strip()]
        final_string = '\n'.join(lines)
        
        # Write to file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(final_string)
            
        print(f"OpenSCENARIO file exported to: {output_path}") 