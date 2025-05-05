"""Test data and helper methods for network testing."""

from lxml import etree
from typing import Dict, List, Tuple

def create_simple_network() -> etree.Element:
    """Create a simple test network with basic elements."""
    root = etree.Element("net")
    
    # Add edges
    edges = etree.SubElement(root, "edges")
    edge1 = etree.SubElement(edges, "edge", id="edge1", **{"from": "j1", "to": "j2", "priority": "1"})
    edge2 = etree.SubElement(edges, "edge", id="edge2", **{"from": "j2", "to": "j3", "priority": "2"})
    
    # Add lanes with shape
    for edge in [edge1, edge2]:
        lanes = etree.SubElement(edge, "lanes")
        for i in range(2):
            lane = etree.SubElement(lanes, "lane", 
                                  id=f"{edge.get('id')}_{i}", 
                                  index=str(i), 
                                  speed="13.89", 
                                  length="100.0")
            shape = etree.SubElement(lane, "shape")
            if edge.get("id") == "edge1":
                shape.text = "0,0 100,0"
            else:
                shape.text = "100,0 200,0"
    
    # Add junctions
    junctions = etree.SubElement(root, "junctions")
    
    # Junction 1 (start)
    j1 = etree.SubElement(junctions, "junction",
                         id="j1",
                         type="priority",
                         x="0", y="0",
                         incLanes="",
                         intLanes="edge1_0 edge1_1")
    
    # Add connection request for j1
    request_j1 = etree.SubElement(j1, "request",
                                 index="0",
                                 response="0",
                                 foes="0",
                                 cont="0")
    
    # Junction 2 (middle)
    j2 = etree.SubElement(junctions, "junction",
                         id="j2",
                         type="priority",
                         x="100", y="0",
                         incLanes="edge1_0 edge1_1",
                         intLanes="edge2_0 edge2_1")
    
    # Add connection request for j2
    request_j2 = etree.SubElement(j2, "request",
                                 index="0",
                                 response="0",
                                 foes="0",
                                 cont="0")
    
    # Junction 3 (end)
    j3 = etree.SubElement(junctions, "junction",
                         id="j3",
                         type="priority",
                         x="200", y="0",
                         incLanes="edge2_0 edge2_1",
                         intLanes="")
    
    # Add connection request for j3
    request_j3 = etree.SubElement(j3, "request",
                                 index="0",
                                 response="0",
                                 foes="0",
                                 cont="0")
    
    # Add connections
    connections = etree.SubElement(root, "connections")
    
    # Connection from j1 to edge1
    connection0 = etree.SubElement(connections, "connection",
                                 **{"from": "j1",
                                    "to": "edge1",
                                    "fromLane": "0",
                                    "toLane": "0",
                                    "via": "j1_0_edge1_0",
                                    "dir": "s",  # straight
                                    "state": "M"})  # merged
    
    # Connection from edge1 to edge2 at j2
    connection1 = etree.SubElement(connections, "connection",
                                 **{"from": "edge1",
                                    "to": "edge2",
                                    "fromLane": "0",
                                    "toLane": "0",
                                    "via": "edge1_0_edge2_0",
                                    "dir": "s",  # straight
                                    "state": "M"})  # merged
    
    connection2 = etree.SubElement(connections, "connection",
                                 **{"from": "edge1",
                                    "to": "edge2",
                                    "fromLane": "1",
                                    "toLane": "1",
                                    "via": "edge1_1_edge2_1",
                                    "dir": "s",  # straight
                                    "state": "M"})  # merged
    
    # Connection from edge2 to j3
    connection3 = etree.SubElement(connections, "connection",
                                 **{"from": "edge2",
                                    "to": "j3",
                                    "fromLane": "0",
                                    "toLane": "0",
                                    "via": "edge2_0_j3_0",
                                    "dir": "s",  # straight
                                    "state": "M"})  # merged
    
    connection4 = etree.SubElement(connections, "connection",
                                 **{"from": "edge2",
                                    "to": "j3",
                                    "fromLane": "1",
                                    "toLane": "1",
                                    "via": "edge2_1_j3_1",
                                    "dir": "s",  # straight
                                    "state": "M"})  # merged
    
    return root

def create_network_with_traffic_signals() -> etree.Element:
    """Create a test network with traffic signals."""
    root = create_simple_network()
    
    # Add traffic signals
    tls = etree.SubElement(root, "tlLogic")
    tls.set("id", "j2")
    tls.set("type", "static")
    tls.set("programID", "0")
    tls.set("offset", "0")
    
    phase = etree.SubElement(tls, "phase", duration="31", state="GGrr")
    
    return root

def create_network_with_invalid_connections() -> etree.Element:
    """Create a test network with invalid connections."""
    root = create_simple_network()
    
    # Add invalid connection to junction j2
    connections = root.find(".//connections")
    invalid_connection = etree.SubElement(connections, "connection",
                                        **{"from": "edge1",
                                           "to": "edge2",
                                           "fromLane": "2",  # Invalid lane index
                                           "toLane": "0",
                                           "via": "edge1_2_edge2_0",
                                           "dir": "s",  # straight
                                           "state": "M"})  # merged
    
    # Add the invalid connection to junction j2's connections
    j2 = root.find(".//junction[@id='j2']")
    if j2 is not None:
        j2.set("incLanes", "edge1_0 edge1_1 edge1_2")  # Add invalid lane to incoming lanes
        j2.set("intLanes", "edge2_0 edge2_1")  # Keep internal lanes valid
    
    return root

def create_network_with_curved_geometry() -> etree.Element:
    """Create a test network with curved geometry."""
    root = create_simple_network()
    
    # Modify edge shapes to include curves
    for edge in root.findall(".//edge"):
        for lane in edge.findall(".//lane"):
            shape = lane.find("shape")
            shape.text = "0,0 50,50 100,0"  # Curved path
    
    return root

def create_network_with_elevation() -> etree.Element:
    """Create a test network with elevation changes."""
    root = create_simple_network()
    
    # Add elevation to junctions
    for junction in root.findall(".//junction"):
        junction.set("z", "10")  # Add elevation
    
    return root 