"""Example of a complex roundabout network."""

from lxml import etree
import math
from typing import List, Tuple

def create_roundabout_network() -> etree.Element:
    """Create a test network with a roundabout and multiple entry/exit points."""
    root = etree.Element("net")
    
    # Roundabout parameters
    center_x, center_y = 0, 0
    radius = 50
    num_entries = 4  # Number of entry/exit points
    
    # Add edges
    edges = etree.SubElement(root, "edges")
    
    # Create roundabout edges (circular)
    roundabout_edges = []
    for i in range(num_entries):
        angle1 = i * (2 * math.pi / num_entries)
        angle2 = (i + 1) * (2 * math.pi / num_entries)
        
        # Calculate start and end points
        x1 = center_x + radius * math.cos(angle1)
        y1 = center_y + radius * math.sin(angle1)
        x2 = center_x + radius * math.cos(angle2)
        y2 = center_y + radius * math.sin(angle2)
        
        # Create roundabout edge
        edge_id = f"roundabout_{i}"
        edge = etree.SubElement(edges, "edge", 
                              id=edge_id,
                              **{"from": f"j{i}",
                                 "to": f"j{(i+1)%num_entries}",
                                 "priority": "1"})
        
        # Add lanes for the roundabout
        lanes = etree.SubElement(edge, "lanes")
        for lane_idx in range(2):  # Two lanes in the roundabout
            lane = etree.SubElement(lanes, "lane",
                                  id=f"{edge_id}_{lane_idx}",
                                  index=str(lane_idx),
                                  speed="8.33",  # 30 km/h
                                  length=str(radius * math.pi / num_entries))
            
            # Create curved shape for the lane
            shape = etree.SubElement(lane, "shape")
            # Generate points along the arc
            points = []
            steps = 10
            for step in range(steps + 1):
                angle = angle1 + (angle2 - angle1) * step / steps
                x = center_x + radius * math.cos(angle)
                y = center_y + radius * math.sin(angle)
                points.append(f"{x:.2f},{y:.2f}")
            shape.text = " ".join(points)
        
        roundabout_edges.append(edge)
    
    # Create entry/exit roads
    for i in range(num_entries):
        angle = i * (2 * math.pi / num_entries)
        x = center_x + radius * math.cos(angle)
        y = center_y + radius * math.sin(angle)
        
        # Entry road
        entry_id = f"entry_{i}"
        entry = etree.SubElement(edges, "edge",
                               id=entry_id,
                               **{"from": f"entry_j{i}",
                                  "to": f"j{i}",
                                  "priority": "2"})
        
        # Add lanes for entry road
        entry_lanes = etree.SubElement(entry, "lanes")
        for lane_idx in range(2):
            lane = etree.SubElement(entry_lanes, "lane",
                                  id=f"{entry_id}_{lane_idx}",
                                  index=str(lane_idx),
                                  speed="13.89",  # 50 km/h
                                  length="100.0")
            shape = etree.SubElement(lane, "shape")
            # Straight line from entry to roundabout
            shape.text = f"{x + 100 * math.cos(angle)},{y + 100 * math.sin(angle)} {x},{y}"
        
        # Exit road
        exit_id = f"exit_{i}"
        exit = etree.SubElement(edges, "edge",
                              id=exit_id,
                              **{"from": f"j{i}",
                                 "to": f"exit_j{i}",
                                 "priority": "2"})
        
        # Add lanes for exit road
        exit_lanes = etree.SubElement(exit, "lanes")
        for lane_idx in range(2):
            lane = etree.SubElement(exit_lanes, "lane",
                                  id=f"{exit_id}_{lane_idx}",
                                  index=str(lane_idx),
                                  speed="13.89",  # 50 km/h
                                  length="100.0")
            shape = etree.SubElement(lane, "shape")
            # Straight line from roundabout to exit
            shape.text = f"{x},{y} {x + 100 * math.cos(angle)},{y + 100 * math.sin(angle)}"
    
    # Add junctions
    junctions = etree.SubElement(root, "junctions")
    
    # Create roundabout junctions
    for i in range(num_entries):
        angle = i * (2 * math.pi / num_entries)
        x = center_x + radius * math.cos(angle)
        y = center_y + radius * math.sin(angle)
        
        # Roundabout junction
        j = etree.SubElement(junctions, "junction",
                           id=f"j{i}",
                           type="priority",
                           x=str(x),
                           y=str(y),
                           incLanes=f"roundabout_{(i-1)%num_entries}_0 roundabout_{(i-1)%num_entries}_1 entry_{i}_0 entry_{i}_1",
                           intLanes=f"roundabout_{i}_0 roundabout_{i}_1 exit_{i}_0 exit_{i}_1")
        
        # Entry junction
        entry_j = etree.SubElement(junctions, "junction",
                                 id=f"entry_j{i}",
                                 type="dead_end",
                                 x=str(x + 100 * math.cos(angle)),
                                 y=str(y + 100 * math.sin(angle)),
                                 incLanes="",
                                 intLanes=f"entry_{i}_0 entry_{i}_1")
        
        # Exit junction
        exit_j = etree.SubElement(junctions, "junction",
                                id=f"exit_j{i}",
                                type="dead_end",
                                x=str(x + 100 * math.cos(angle)),
                                y=str(y + 100 * math.sin(angle)),
                                incLanes=f"exit_{i}_0 exit_{i}_1",
                                intLanes="")
    
    # Add connections
    connections = etree.SubElement(root, "connections")
    
    # Add connections for each junction
    for i in range(num_entries):
        # Entry to roundabout connections
        for entry_lane in range(2):
            for roundabout_lane in range(2):
                connection = etree.SubElement(connections, "connection",
                                           **{"from": f"entry_{i}",
                                              "to": f"roundabout_{i}",
                                              "fromLane": str(entry_lane),
                                              "toLane": str(roundabout_lane),
                                              "via": f"entry_{i}_{entry_lane}_roundabout_{i}_{roundabout_lane}",
                                              "dir": "s",
                                              "state": "M"})
        
        # Roundabout to exit connections
        for roundabout_lane in range(2):
            for exit_lane in range(2):
                connection = etree.SubElement(connections, "connection",
                                           **{"from": f"roundabout_{i}",
                                              "to": f"exit_{i}",
                                              "fromLane": str(roundabout_lane),
                                              "toLane": str(exit_lane),
                                              "via": f"roundabout_{i}_{roundabout_lane}_exit_{i}_{exit_lane}",
                                              "dir": "s",
                                              "state": "M"})
        
        # Roundabout to roundabout connections
        for lane in range(2):
            connection = etree.SubElement(connections, "connection",
                                       **{"from": f"roundabout_{i}",
                                          "to": f"roundabout_{(i+1)%num_entries}",
                                          "fromLane": str(lane),
                                          "toLane": str(lane),
                                          "via": f"roundabout_{i}_{lane}_roundabout_{(i+1)%num_entries}_{lane}",
                                          "dir": "s",
                                          "state": "M"})
    
    return root

if __name__ == "__main__":
    # Create the roundabout network
    network = create_roundabout_network()
    
    # Print the network XML
    print(etree.tostring(network, pretty_print=True, encoding='unicode')) 