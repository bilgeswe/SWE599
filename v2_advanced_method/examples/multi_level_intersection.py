"""Example of a multi-level intersection with overpass and underpass."""

from lxml import etree
import math
from typing import List, Tuple

def create_multi_level_intersection() -> etree.Element:
    """Create a test network with a multi-level intersection (overpass/underpass)."""
    root = etree.Element("net")
    
    # Intersection parameters
    center_x, center_y = 0, 0
    road_length = 200  # Length of approach roads
    bridge_length = 100  # Length of bridge/underpass section
    bridge_width = 20  # Width of bridge/underpass
    
    # Add edges
    edges = etree.SubElement(root, "edges")
    
    # Create main roads (horizontal and vertical)
    # Horizontal road (ground level)
    h_road_id = "horizontal_road"
    h_road = etree.SubElement(edges, "edge",
                            id=h_road_id,
                            **{"from": "h_start",
                               "to": "h_end",
                               "priority": "1"})
    
    # Add lanes for horizontal road
    h_lanes = etree.SubElement(h_road, "lanes")
    for lane_idx in range(2):  # Two lanes in each direction
        # Left lane (westbound)
        left_lane = etree.SubElement(h_lanes, "lane",
                                   id=f"{h_road_id}_left_{lane_idx}",
                                   index=str(lane_idx),
                                   speed="13.89",  # 50 km/h
                                   length=str(road_length))
        shape = etree.SubElement(left_lane, "shape")
        shape.text = f"{center_x + road_length/2},{center_y - 3.5 + lane_idx*3.5} {center_x - road_length/2},{center_y - 3.5 + lane_idx*3.5}"
        
        # Right lane (eastbound)
        right_lane = etree.SubElement(h_lanes, "lane",
                                    id=f"{h_road_id}_right_{lane_idx}",
                                    index=str(lane_idx + 2),
                                    speed="13.89",  # 50 km/h
                                    length=str(road_length))
        shape = etree.SubElement(right_lane, "shape")
        shape.text = f"{center_x - road_length/2},{center_y + 3.5 - lane_idx*3.5} {center_x + road_length/2},{center_y + 3.5 - lane_idx*3.5}"
    
    # Vertical road (elevated)
    v_road_id = "vertical_road"
    v_road = etree.SubElement(edges, "edge",
                            id=v_road_id,
                            **{"from": "v_start",
                               "to": "v_end",
                               "priority": "1"})
    
    # Add lanes for vertical road
    v_lanes = etree.SubElement(v_road, "lanes")
    for lane_idx in range(2):  # Two lanes in each direction
        # Bottom lane (southbound)
        bottom_lane = etree.SubElement(v_lanes, "lane",
                                     id=f"{v_road_id}_bottom_{lane_idx}",
                                     index=str(lane_idx),
                                     speed="13.89",  # 50 km/h
                                     length=str(road_length))
        shape = etree.SubElement(bottom_lane, "shape")
        shape.text = f"{center_x - 3.5 + lane_idx*3.5},{center_y + road_length/2} {center_x - 3.5 + lane_idx*3.5},{center_y - road_length/2}"
        
        # Top lane (northbound)
        top_lane = etree.SubElement(v_lanes, "lane",
                                  id=f"{v_road_id}_top_{lane_idx}",
                                  index=str(lane_idx + 2),
                                  speed="13.89",  # 50 km/h
                                  length=str(road_length))
        shape = etree.SubElement(top_lane, "shape")
        shape.text = f"{center_x + 3.5 - lane_idx*3.5},{center_y - road_length/2} {center_x + 3.5 - lane_idx*3.5},{center_y + road_length/2}"
    
    # Create ramp connections
    # North ramp (from horizontal to vertical)
    n_ramp_id = "north_ramp"
    n_ramp = etree.SubElement(edges, "edge",
                            id=n_ramp_id,
                            **{"from": "h_north_j",
                               "to": "v_north_j",
                               "priority": "2"})
    
    # Add lanes for north ramp
    n_ramp_lanes = etree.SubElement(n_ramp, "lanes")
    for lane_idx in range(1):  # Single lane ramp
        lane = etree.SubElement(n_ramp_lanes, "lane",
                              id=f"{n_ramp_id}_{lane_idx}",
                              index=str(lane_idx),
                              speed="8.33",  # 30 km/h
                              length=str(bridge_length))
        shape = etree.SubElement(lane, "shape")
        shape.text = f"{center_x + bridge_width/2},{center_y - bridge_width/2} {center_x + bridge_width/2},{center_y - bridge_length/2}"
    
    # Add junctions
    junctions = etree.SubElement(root, "junctions")
    
    # Create main road junctions
    # Horizontal road junctions
    h_start_j = etree.SubElement(junctions, "junction",
                               id="h_start",
                               type="dead_end",
                               x=str(center_x - road_length/2),
                               y=str(center_y),
                               incLanes="",
                               intLanes=f"{h_road_id}_left_0 {h_road_id}_left_1 {h_road_id}_right_2 {h_road_id}_right_3")
    
    h_end_j = etree.SubElement(junctions, "junction",
                             id="h_end",
                             type="dead_end",
                             x=str(center_x + road_length/2),
                             y=str(center_y),
                             incLanes=f"{h_road_id}_left_0 {h_road_id}_left_1 {h_road_id}_right_2 {h_road_id}_right_3",
                             intLanes="")
    
    # Vertical road junctions
    v_start_j = etree.SubElement(junctions, "junction",
                               id="v_start",
                               type="dead_end",
                               x=str(center_x),
                               y=str(center_y - road_length/2),
                               incLanes="",
                               intLanes=f"{v_road_id}_bottom_0 {v_road_id}_bottom_1 {v_road_id}_top_2 {v_road_id}_top_3")
    
    v_end_j = etree.SubElement(junctions, "junction",
                             id="v_end",
                             type="dead_end",
                             x=str(center_x),
                             y=str(center_y + road_length/2),
                             incLanes=f"{v_road_id}_bottom_0 {v_road_id}_bottom_1 {v_road_id}_top_2 {v_road_id}_top_3",
                             intLanes="")
    
    # Ramp junctions
    h_north_j = etree.SubElement(junctions, "junction",
                               id="h_north_j",
                               type="priority",
                               x=str(center_x + bridge_width/2),
                               y=str(center_y - bridge_width/2),
                               incLanes=f"{h_road_id}_right_2 {h_road_id}_right_3",
                               intLanes=f"{n_ramp_id}_0")
    
    v_north_j = etree.SubElement(junctions, "junction",
                               id="v_north_j",
                               type="priority",
                               x=str(center_x + bridge_width/2),
                               y=str(center_y - bridge_length/2),
                               incLanes=f"{n_ramp_id}_0",
                               intLanes=f"{v_road_id}_top_2 {v_road_id}_top_3")
    
    # Add connections
    connections = etree.SubElement(root, "connections")
    
    # Add connections for horizontal road
    for lane_idx in range(2):
        # Left lanes (westbound)
        connection = etree.SubElement(connections, "connection",
                                   **{"from": h_road_id,
                                      "to": h_road_id,
                                      "fromLane": str(lane_idx),
                                      "toLane": str(lane_idx),
                                      "via": f"{h_road_id}_left_{lane_idx}",
                                      "dir": "s",
                                      "state": "M"})
        
        # Right lanes (eastbound)
        connection = etree.SubElement(connections, "connection",
                                   **{"from": h_road_id,
                                      "to": h_road_id,
                                      "fromLane": str(lane_idx + 2),
                                      "toLane": str(lane_idx + 2),
                                      "via": f"{h_road_id}_right_{lane_idx}",
                                      "dir": "s",
                                      "state": "M"})
    
    # Add connections for vertical road
    for lane_idx in range(2):
        # Bottom lanes (southbound)
        connection = etree.SubElement(connections, "connection",
                                   **{"from": v_road_id,
                                      "to": v_road_id,
                                      "fromLane": str(lane_idx),
                                      "toLane": str(lane_idx),
                                      "via": f"{v_road_id}_bottom_{lane_idx}",
                                      "dir": "s",
                                      "state": "M"})
        
        # Top lanes (northbound)
        connection = etree.SubElement(connections, "connection",
                                   **{"from": v_road_id,
                                      "to": v_road_id,
                                      "fromLane": str(lane_idx + 2),
                                      "toLane": str(lane_idx + 2),
                                      "via": f"{v_road_id}_top_{lane_idx}",
                                      "dir": "s",
                                      "state": "M"})
    
    # Add connections for ramps
    # North ramp connections
    connection = etree.SubElement(connections, "connection",
                               **{"from": h_road_id,
                                  "to": n_ramp_id,
                                  "fromLane": "2",  # Right lane
                                  "toLane": "0",
                                  "via": f"{h_road_id}_right_0_{n_ramp_id}_0",
                                  "dir": "r",  # right turn
                                  "state": "M"})
    
    connection = etree.SubElement(connections, "connection",
                               **{"from": n_ramp_id,
                                  "to": v_road_id,
                                  "fromLane": "0",
                                  "toLane": "2",  # Top lane
                                  "via": f"{n_ramp_id}_0_{v_road_id}_top_0",
                                  "dir": "s",
                                  "state": "M"})
    
    return root

if __name__ == "__main__":
    # Create the multi-level intersection network
    network = create_multi_level_intersection()
    
    # Print the network XML
    print(etree.tostring(network, pretty_print=True, encoding='unicode')) 