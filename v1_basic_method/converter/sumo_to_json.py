"""Convert SUMO network to JSON format for AV simulation."""

import os
import json
import sumolib
from typing import List, Dict, Any
import numpy as np

def convert_sumo_to_json(sumo_net_path: str, output_dir: str) -> None:
    """Convert SUMO network to JSON format.
    
    Args:
        sumo_net_path: Path to SUMO .net.xml file
        output_dir: Directory to save JSON files
    """
    # Load SUMO network
    net = sumolib.net.readNet(sumo_net_path)
    print(f"Loaded SUMO network with {len(net.getEdges())} edges")
    
    # Convert nodes
    nodes = []
    for node in net.getNodes():
        x, y = node.getCoord()
        nodes.append({
            'id': node.getID(),
            'x': float(x),
            'y': float(y),
            'type': node.getType()
        })
    
    # Convert edges
    edges = []
    for edge in net.getEdges():
        print(f"Processing edge: {edge.getID()}")
        # Get lanes
        lanes = []
        for lane in edge.getLanes():
            lanes.append(lane.getID())
        
        # Get shape points
        shape = edge.getShape()
        shape_points = [(float(x), float(y)) for x, y in shape]
        
        edges.append({
            'id': edge.getID(),
            'from_node': edge.getFromNode().getID(),
            'to_node': edge.getToNode().getID(),
            'lanes': lanes,
            'speed_limit': float(edge.getSpeed()),
            'shape': shape_points
        })
        print(f"Added edge: {edge.getID()} with {len(lanes)} lanes")
    
    # Create traffic lights (with all required fields)
    traffic_lights = []
    for node in net.getNodes():
        if node.getType() == 'traffic_light':
            x, y = node.getCoord()
            traffic_lights.append({
                'id': f"tl_{node.getID()}",
                'position': (float(x), float(y)),
                'state': 'RED',  # Default state
                'phases': ['RED', 'YELLOW', 'GREEN'],
                'current_phase': 0,
                'time_in_phase': 0.0,
                'cycle_time': 60.0
            })
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Save JSON files
    with open(os.path.join(output_dir, 'nodes.json'), 'w') as f:
        json.dump(nodes, f, indent=2)
    
    with open(os.path.join(output_dir, 'edges.json'), 'w') as f:
        json.dump(edges, f, indent=2)
    
    with open(os.path.join(output_dir, 'traffic_lights.json'), 'w') as f:
        json.dump(traffic_lights, f, indent=2)
    
    print(f"Converted SUMO network to JSON format")
    print(f"Saved files to: {output_dir}")
    print(f"Nodes: {len(nodes)}")
    print(f"Edges: {len(edges)}")
    print(f"Traffic Lights: {len(traffic_lights)}")

if __name__ == "__main__":
    # Convert Üsküdar network
    sumo_net_path = "data/sumo/üsküdar__istanbul__turkey.net.xml"
    output_dir = "output/uskudar"
    convert_sumo_to_json(sumo_net_path, output_dir) 