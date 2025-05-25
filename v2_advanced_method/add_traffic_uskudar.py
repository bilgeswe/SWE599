#!/usr/bin/env python3
"""Add traffic simulation to Üsküdar SUMO network."""

import xml.etree.ElementTree as ET
import random

def create_route_file():
    """Create a simple route file for Üsküdar traffic simulation."""
    
    # Create root routes element
    routes = ET.Element("routes")
    
    # Add a vehicle type (car)
    vtype = ET.SubElement(routes, "vType")
    vtype.set("id", "car")
    vtype.set("accel", "2.6")
    vtype.set("decel", "4.5")
    vtype.set("sigma", "0.5")
    vtype.set("length", "4.5")
    vtype.set("maxSpeed", "55.0")
    vtype.set("color", "1,0,0")
    
    # Add some sample routes through Üsküdar
    # Note: These are placeholder routes - actual edge IDs would need to be extracted from the network
    sample_routes = [
        ("route1", ["edge1", "edge2", "edge3"]),
        ("route2", ["edge4", "edge5", "edge6"]),
        ("route3", ["edge7", "edge8", "edge9"]),
    ]
    
    for route_id, edges in sample_routes:
        route = ET.SubElement(routes, "route")
        route.set("id", route_id)
        route.set("edges", " ".join(edges))
    
    # Add vehicles with random routes
    for i in range(10):  # 10 vehicles
        vehicle = ET.SubElement(routes, "vehicle")
        vehicle.set("id", f"car{i}")
        vehicle.set("type", "car")
        vehicle.set("route", f"route{(i % 3) + 1}")
        vehicle.set("depart", str(i * 2))  # Depart every 2 seconds
        vehicle.set("color", f"{random.random():.1f},{random.random():.1f},{random.random():.1f}")
    
    # Write to file
    tree = ET.ElementTree(routes)
    tree.write("uskudar_routes.rou.xml", encoding="utf-8", xml_declaration=True)
    print("Created uskudar_routes.rou.xml")

def create_sumo_config():
    """Create SUMO configuration file."""
    
    config = ET.Element("configuration")
    
    # Input section
    input_section = ET.SubElement(config, "input")
    
    net_file = ET.SubElement(input_section, "net-file")
    net_file.set("value", "uskudar_network.net.xml")
    
    route_files = ET.SubElement(input_section, "route-files")
    route_files.set("value", "uskudar_routes.rou.xml")
    
    # Time section
    time_section = ET.SubElement(config, "time")
    
    begin = ET.SubElement(time_section, "begin")
    begin.set("value", "0")
    
    end = ET.SubElement(time_section, "end")
    end.set("value", "1000")
    
    # Write to file
    tree = ET.ElementTree(config)
    tree.write("uskudar_simulation.sumocfg", encoding="utf-8", xml_declaration=True)
    print("Created uskudar_simulation.sumocfg")

if __name__ == "__main__":
    print("Creating traffic simulation files for Üsküdar...")
    create_route_file()
    create_sumo_config()
    print("\\nTo run traffic simulation:")
    print("sumo-gui uskudar_simulation.sumocfg")
    print("\\nTo view network only:")
    print("sumo-gui uskudar_network.net.xml") 