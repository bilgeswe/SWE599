"""Example of a diamond interchange with grade-separated roads and ramps."""

from lxml import etree
import math
from typing import List, Tuple

def create_diamond_interchange() -> etree.Element:
    """Create a test network with a diamond interchange."""
    root = etree.Element("net")
    
    # Intersection parameters
    center_x, center_y = 0, 0
    road_length = 300  # Length of approach roads
    bridge_length = 100  # Length of bridge section
    bridge_width = 20  # Width of bridge
    ramp_length = 150  # Length of ramps
    
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
    
    # Create ramp connections (diamond pattern)
    # North-east ramp
    ne_ramp_id = "ne_ramp"
    ne_ramp = etree.SubElement(edges, "edge",
                             id=ne_ramp_id,
                             **{"from": "h_ne_j",
                                "to": "v_ne_j",
                                "priority": "2"})
    
    # Add lanes for north-east ramp
    ne_ramp_lanes = etree.SubElement(ne_ramp, "lanes")
    for lane_idx in range(1):  # Single lane ramp
        lane = etree.SubElement(ne_ramp_lanes, "lane",
                              id=f"{ne_ramp_id}_{lane_idx}",
                              index=str(lane_idx),
                              speed="8.33",  # 30 km/h
                              length=str(ramp_length))
        shape = etree.SubElement(lane, "shape")
        shape.text = f"{center_x + bridge_width/2},{center_y - bridge_width/2} {center_x + bridge_width/2},{center_y - ramp_length/2}"
    
    # North-west ramp
    nw_ramp_id = "nw_ramp"
    nw_ramp = etree.SubElement(edges, "edge",
                             id=nw_ramp_id,
                             **{"from": "v_nw_j",
                                "to": "h_nw_j",
                                "priority": "2"})
    
    # Add lanes for north-west ramp
    nw_ramp_lanes = etree.SubElement(nw_ramp, "lanes")
    for lane_idx in range(1):  # Single lane ramp
        lane = etree.SubElement(nw_ramp_lanes, "lane",
                              id=f"{nw_ramp_id}_{lane_idx}",
                              index=str(lane_idx),
                              speed="8.33",  # 30 km/h
                              length=str(ramp_length))
        shape = etree.SubElement(lane, "shape")
        shape.text = f"{center_x - bridge_width/2},{center_y - ramp_length/2} {center_x - bridge_width/2},{center_y - bridge_width/2}"
    
    # South-east ramp
    se_ramp_id = "se_ramp"
    se_ramp = etree.SubElement(edges, "edge",
                             id=se_ramp_id,
                             **{"from": "v_se_j",
                                "to": "h_se_j",
                                "priority": "2"})
    
    # Add lanes for south-east ramp
    se_ramp_lanes = etree.SubElement(se_ramp, "lanes")
    for lane_idx in range(1):  # Single lane ramp
        lane = etree.SubElement(se_ramp_lanes, "lane",
                              id=f"{se_ramp_id}_{lane_idx}",
                              index=str(lane_idx),
                              speed="8.33",  # 30 km/h
                              length=str(ramp_length))
        shape = etree.SubElement(lane, "shape")
        shape.text = f"{center_x + bridge_width/2},{center_y + ramp_length/2} {center_x + bridge_width/2},{center_y + bridge_width/2}"
    
    # South-west ramp
    sw_ramp_id = "sw_ramp"
    sw_ramp = etree.SubElement(edges, "edge",
                             id=sw_ramp_id,
                             **{"from": "h_sw_j",
                                "to": "v_sw_j",
                                "priority": "2"})
    
    # Add lanes for south-west ramp
    sw_ramp_lanes = etree.SubElement(sw_ramp, "lanes")
    for lane_idx in range(1):  # Single lane ramp
        lane = etree.SubElement(sw_ramp_lanes, "lane",
                              id=f"{sw_ramp_id}_{lane_idx}",
                              index=str(lane_idx),
                              speed="8.33",  # 30 km/h
                              length=str(ramp_length))
        shape = etree.SubElement(lane, "shape")
        shape.text = f"{center_x - bridge_width/2},{center_y + bridge_width/2} {center_x - bridge_width/2},{center_y + ramp_length/2}"
    
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
    
    # Create ramp junctions
    # North-east ramp junctions
    h_ne_j = etree.SubElement(junctions, "junction",
                            id="h_ne_j",
                            type="priority",
                            x=str(center_x + bridge_width/2),
                            y=str(center_y - bridge_width/2),
                            incLanes=f"{h_road_id}_right_2 {h_road_id}_right_3",
                            intLanes=f"{ne_ramp_id}_0")
    
    v_ne_j = etree.SubElement(junctions, "junction",
                            id="v_ne_j",
                            type="priority",
                            x=str(center_x + bridge_width/2),
                            y=str(center_y - ramp_length/2),
                            incLanes=f"{ne_ramp_id}_0",
                            intLanes=f"{v_road_id}_top_2 {v_road_id}_top_3")
    
    # North-west ramp junctions
    h_nw_j = etree.SubElement(junctions, "junction",
                            id="h_nw_j",
                            type="priority",
                            x=str(center_x - bridge_width/2),
                            y=str(center_y - bridge_width/2),
                            incLanes=f"{nw_ramp_id}_0",
                            intLanes=f"{h_road_id}_left_0 {h_road_id}_left_1")
    
    v_nw_j = etree.SubElement(junctions, "junction",
                            id="v_nw_j",
                            type="priority",
                            x=str(center_x - bridge_width/2),
                            y=str(center_y - ramp_length/2),
                            incLanes=f"{v_road_id}_top_2 {v_road_id}_top_3",
                            intLanes=f"{nw_ramp_id}_0")
    
    # South-east ramp junctions
    h_se_j = etree.SubElement(junctions, "junction",
                            id="h_se_j",
                            type="priority",
                            x=str(center_x + bridge_width/2),
                            y=str(center_y + bridge_width/2),
                            incLanes=f"{se_ramp_id}_0",
                            intLanes=f"{h_road_id}_right_2 {h_road_id}_right_3")
    
    v_se_j = etree.SubElement(junctions, "junction",
                            id="v_se_j",
                            type="priority",
                            x=str(center_x + bridge_width/2),
                            y=str(center_y + ramp_length/2),
                            incLanes=f"{v_road_id}_bottom_0 {v_road_id}_bottom_1",
                            intLanes=f"{se_ramp_id}_0")
    
    # South-west ramp junctions
    h_sw_j = etree.SubElement(junctions, "junction",
                            id="h_sw_j",
                            type="priority",
                            x=str(center_x - bridge_width/2),
                            y=str(center_y + bridge_width/2),
                            incLanes=f"{h_road_id}_left_0 {h_road_id}_left_1",
                            intLanes=f"{sw_ramp_id}_0")
    
    v_sw_j = etree.SubElement(junctions, "junction",
                            id="v_sw_j",
                            type="priority",
                            x=str(center_x - bridge_width/2),
                            y=str(center_y + ramp_length/2),
                            incLanes=f"{sw_ramp_id}_0",
                            intLanes=f"{v_road_id}_bottom_0 {v_road_id}_bottom_1")
    
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
    # North-east ramp connections
    connection = etree.SubElement(connections, "connection",
                               **{"from": h_road_id,
                                  "to": ne_ramp_id,
                                  "fromLane": "2",  # Right lane
                                  "toLane": "0",
                                  "via": f"{h_road_id}_right_0_{ne_ramp_id}_0",
                                  "dir": "r",  # right turn
                                  "state": "M"})
    
    connection = etree.SubElement(connections, "connection",
                               **{"from": ne_ramp_id,
                                  "to": v_road_id,
                                  "fromLane": "0",
                                  "toLane": "2",  # Top lane
                                  "via": f"{ne_ramp_id}_0_{v_road_id}_top_0",
                                  "dir": "s",
                                  "state": "M"})
    
    # North-west ramp connections
    connection = etree.SubElement(connections, "connection",
                               **{"from": v_road_id,
                                  "to": nw_ramp_id,
                                  "fromLane": "2",  # Top lane
                                  "toLane": "0",
                                  "via": f"{v_road_id}_top_0_{nw_ramp_id}_0",
                                  "dir": "l",  # left turn
                                  "state": "M"})
    
    connection = etree.SubElement(connections, "connection",
                               **{"from": nw_ramp_id,
                                  "to": h_road_id,
                                  "fromLane": "0",
                                  "toLane": "0",  # Left lane
                                  "via": f"{nw_ramp_id}_0_{h_road_id}_left_0",
                                  "dir": "s",
                                  "state": "M"})
    
    # South-east ramp connections
    connection = etree.SubElement(connections, "connection",
                               **{"from": v_road_id,
                                  "to": se_ramp_id,
                                  "fromLane": "0",  # Bottom lane
                                  "toLane": "0",
                                  "via": f"{v_road_id}_bottom_0_{se_ramp_id}_0",
                                  "dir": "r",  # right turn
                                  "state": "M"})
    
    connection = etree.SubElement(connections, "connection",
                               **{"from": se_ramp_id,
                                  "to": h_road_id,
                                  "fromLane": "0",
                                  "toLane": "2",  # Right lane
                                  "via": f"{se_ramp_id}_0_{h_road_id}_right_0",
                                  "dir": "s",
                                  "state": "M"})
    
    # South-west ramp connections
    connection = etree.SubElement(connections, "connection",
                               **{"from": h_road_id,
                                  "to": sw_ramp_id,
                                  "fromLane": "0",  # Left lane
                                  "toLane": "0",
                                  "via": f"{h_road_id}_left_0_{sw_ramp_id}_0",
                                  "dir": "l",  # left turn
                                  "state": "M"})
    
    connection = etree.SubElement(connections, "connection",
                               **{"from": sw_ramp_id,
                                  "to": v_road_id,
                                  "fromLane": "0",
                                  "toLane": "0",  # Bottom lane
                                  "via": f"{sw_ramp_id}_0_{v_road_id}_bottom_0",
                                  "dir": "s",
                                  "state": "M"})
    
    return root

if __name__ == "__main__":
    # Create the diamond interchange network
    network = create_diamond_interchange()
    
    # Print the network XML
    print(etree.tostring(network, pretty_print=True, encoding='unicode')) 