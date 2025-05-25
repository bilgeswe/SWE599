#!/usr/bin/env python3
"""
Detect and report common issues in SUMO network files (.net.xml).

- Disconnected edges
- Sharp turns
- Orphaned lanes
- Incomplete roundabouts

Usage:
    python network_issue_detector.py path/to/network.net.xml
"""
import sys
import math
import logging
import sumolib
from collections import defaultdict
import xml.etree.ElementTree as ET

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SHARP_TURN_THRESHOLD = 150  # degrees


def calculate_angles(shape):
    """Calculate angles between consecutive segments."""
    angles = []
    for i in range(len(shape) - 2):
        p1, p2, p3 = shape[i:i+3]
        v1 = (p2[0] - p1[0], p2[1] - p1[1])
        v2 = (p3[0] - p2[0], p3[1] - p2[1])
        dot = v1[0] * v2[0] + v1[1] * v2[1]
        det = v1[0] * v2[1] - v1[1] * v2[0]
        angle = math.degrees(math.atan2(det, dot))
        angles.append(abs(angle))
    return angles


def filter_problematic_elements(net_file: str) -> None:
    """Filter out problematic edges and lanes from the network file."""
    tree = ET.parse(net_file)
    root = tree.getroot()
    
    # Get all edges
    edges = root.findall('.//edge')
    
    # Track edges to remove
    edges_to_remove = set()
    
    # Check each edge
    for edge in edges:
        edge_id = edge.get('id')
        
        # Check if edge has shape
        shape = edge.find('.//shape')
        if shape is None or not shape.text.strip():
            edges_to_remove.add(edge_id)
            continue
            
        # Check if edge has valid lanes
        lanes = edge.findall('.//lane')
        if not lanes:
            edges_to_remove.add(edge_id)
            continue
            
        # Check each lane
        for lane in lanes:
            # Check required attributes
            if not all(lane.get(attr) for attr in ['id', 'index', 'speed', 'width']):
                edges_to_remove.add(edge_id)
                break
    
    # Remove problematic edges
    for edge in edges:
        if edge.get('id') in edges_to_remove:
            root.remove(edge)

    # Remove <connection> elements that reference removed edges
    connections = root.findall('.//connection')
    for conn in connections:
        from_edge = conn.get('from')
        to_edge = conn.get('to')
        if (from_edge in edges_to_remove) or (to_edge in edges_to_remove):
            root.remove(conn)

    # Save the filtered network
    tree.write(net_file)


def detect_issues(net_file: str) -> None:
    """Detect and report network issues."""
    logger.info(f"Loaded network: {net_file}")
    
    # Filter out problematic elements first
    filter_problematic_elements(net_file)
    
    # Load the filtered network
    net = sumolib.net.readNet(net_file)

    # 1. Disconnected edges
    disconnected_edges = [edge for edge in net.getEdges() if not edge.getOutgoing()]
    logger.info(f"Disconnected edges: {len(disconnected_edges)}")
    for edge in disconnected_edges[:20]:  # Show up to 20
        logger.info(f"  {edge.getID()}")
    if len(disconnected_edges) > 20:
        logger.info(f"  ... and {len(disconnected_edges) - 20} more")

    # 2. Sharp turns
    sharp_turns = []
    for edge in net.getEdges():
        for lane in edge.getLanes():
            shape = lane.getShape()
            if len(shape) >= 3:
                angles = calculate_angles(shape)
                for i, angle in enumerate(angles):
                    if angle > SHARP_TURN_THRESHOLD:
                        sharp_turns.append((edge.getID(), i, angle))
    logger.info(f"Sharp turns (>{SHARP_TURN_THRESHOLD}°): {len(sharp_turns)}")
    for edge_id, segment, angle in sharp_turns[:20]:
        logger.info(f"  Edge {edge_id} at segment {segment}: {angle:.1f}°")
    if len(sharp_turns) > 20:
        logger.info(f"  ... and {len(sharp_turns) - 20} more")

    # 3. Orphaned lanes
    orphaned_lanes = []
    for edge in net.getEdges():
        for lane in edge.getLanes():
            if not lane.getIncoming():
                orphaned_lanes.append(lane.getID())
    logger.info(f"Orphaned lanes: {len(orphaned_lanes)}")
    for lane_id in orphaned_lanes[:20]:
        logger.info(f"  {lane_id}")
    if len(orphaned_lanes) > 20:
        logger.info(f"  ... and {len(orphaned_lanes) - 20} more")

    # 4. Incomplete roundabouts
    roundabouts = net.getRoundabouts()
    incomplete_roundabouts = []
    for r in roundabouts:
        edges = r.getEdges() if hasattr(r, 'getEdges') else r  # fallback for older sumolib
        try:
            if any(edge_id not in [e.getID() for e in net.getEdge(edge_id).getOutgoing()] for edge_id in edges):
                incomplete_roundabouts.append(list(edges))
        except KeyError:
            # Skip roundabouts with missing edges
            continue
    logger.info(f"Incomplete roundabouts: {len(incomplete_roundabouts)}")
    for r in incomplete_roundabouts[:5]:
        logger.info(f"  Roundabout edges: {r}")
    if len(incomplete_roundabouts) > 5:
        logger.info(f"  ... and {len(incomplete_roundabouts) - 5} more")

    logger.info("Detection complete.")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python network_issue_detector.py path/to/network.net.xml")
        sys.exit(1)
    detect_issues(sys.argv[1]) 