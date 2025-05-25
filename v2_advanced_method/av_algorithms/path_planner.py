"""Path planning algorithm for autonomous vehicles."""

import math
import numpy as np
from dataclasses import dataclass
from typing import List, Tuple, Dict, Set, Optional
from collections import defaultdict

@dataclass
class Node:
    """Represents a node in the road network."""
    
    def __init__(self, id: str, x: float, y: float, type: str = "default"):
        """Initialize a node.
        
        Args:
            id: Unique identifier for the node
            x: X coordinate
            y: Y coordinate
            type: Node type (e.g., "default", "traffic_light", "priority")
        """
        self.id = id
        self.x = x
        self.y = y
        self.type = type
        self.edges = []  # List of connected edges
        
    def add_edge(self, edge: 'Edge') -> None:
        """Add a connected edge to this node.
        
        Args:
            edge: Edge to add
        """
        self.edges.append(edge)
        
    def __str__(self) -> str:
        return f"Node(id={self.id}, x={self.x:.2f}, y={self.y:.2f}, type={self.type})"

@dataclass
class Edge:
    """Represents an edge (road segment) in the road network."""
    def __init__(self, id: str, from_node: str, to_node: str, length=None, speed_limit: float = None, lanes=None, shape=None, **kwargs):
        self.id = id
        self.from_node = from_node
        self.to_node = to_node
        self.length = length  # can be None if not provided
        self.speed_limit = speed_limit
        self.lanes = lanes if lanes is not None else []
        self.shape = shape
        # Ignore any extra kwargs

class PathPlanner:
    """Implements path planning for autonomous vehicles."""
    
    def __init__(self):
        """Initialize the path planner."""
        self.nodes: Dict[str, Node] = {}
        self.edges: Dict[str, Edge] = {}
        self.lane_to_edge: Dict[str, str] = {}  # Maps lane IDs to edge IDs
        
    def add_node(self, node: Node) -> None:
        """Add a node to the road network.
        
        Args:
            node: Node to add
        """
        self.nodes[node.id] = node
        
    def add_edge(self, edge: Edge) -> None:
        """Add an edge to the road network.
        
        Args:
            edge: Edge to add
        """
        self.edges[edge.id] = edge
        for lane in edge.lanes:
            self.lane_to_edge[lane] = edge.id
            
    def find_path(self, start_lane: str, goal_lane: str) -> List[str]:
        """Find a path from start lane to goal lane using A* algorithm.
        
        Args:
            start_lane: ID of the starting lane
            goal_lane: ID of the goal lane
            
        Returns:
            List of lane IDs representing the path
        """
        if start_lane not in self.lane_to_edge or goal_lane not in self.lane_to_edge:
            raise ValueError("Start or goal lane not found in network")
            
        start_edge = self.edges[self.lane_to_edge[start_lane]]
        goal_edge = self.edges[self.lane_to_edge[goal_lane]]
        
        # Initialize open and closed sets
        open_set: Set[str] = {start_edge.id}
        closed_set: Set[str] = set()
        
        # Initialize cost and parent maps
        g_score: Dict[str, float] = defaultdict(lambda: float('inf'))
        g_score[start_edge.id] = 0
        
        f_score: Dict[str, float] = defaultdict(lambda: float('inf'))
        f_score[start_edge.id] = self._heuristic(start_edge, goal_edge)
        
        parent: Dict[str, str] = {}
        
        while open_set:
            # Find node with lowest f_score
            current = min(open_set, key=lambda x: f_score[x])
            
            if current == goal_edge.id:
                return self._reconstruct_path(parent, current, start_lane, goal_lane)
                
            open_set.remove(current)
            closed_set.add(current)
            
            # Check neighbors
            current_edge = self.edges[current]
            for node_id in [current_edge.from_node, current_edge.to_node]:
                if node_id in self.nodes:
                    node = self.nodes[node_id]
                    if hasattr(node, 'edges'):
                        for edge_obj in node.edges:
                            # Convert edge object to edge ID
                            edge_id = edge_obj.id if hasattr(edge_obj, 'id') else str(edge_obj)
                            
                            if edge_id in closed_set:
                                continue
                                
                            if edge_id not in self.edges:
                                continue
                                
                            neighbor = self.edges[edge_id]
                            tentative_g_score = g_score[current] + self._edge_cost(current_edge, neighbor)
                            
                            if tentative_g_score < g_score[edge_id]:
                                parent[edge_id] = current
                                g_score[edge_id] = tentative_g_score
                                f_score[edge_id] = tentative_g_score + self._heuristic(neighbor, goal_edge)
                                
                                if edge_id not in open_set:
                                    open_set.add(edge_id)
                            
        raise ValueError("No path found")
        
    def _heuristic(self, edge1: Edge, edge2: Edge) -> float:
        """Calculate heuristic cost between two edges.
        
        Args:
            edge1: First edge
            edge2: Second edge
            
        Returns:
            Heuristic cost
        """
        # Use Euclidean distance between edge centers
        node1 = self.nodes[edge1.from_node]
        node2 = self.nodes[edge2.from_node]
        return math.sqrt((node1.x - node2.x)**2 + (node1.y - node2.y)**2)
        
    def _edge_cost(self, edge1: Edge, edge2: Edge) -> float:
        """Calculate cost between two connected edges.
        
        Args:
            edge1: First edge
            edge2: Second edge
            
        Returns:
            Cost of moving from edge1 to edge2
        """
        # Base cost is the length of edge2 (use default if None)
        length = edge2.length if edge2.length is not None else 100.0  # Default 100m
        cost = length
        
        # Add penalty for speed limit changes (use defaults if None)
        speed1 = edge1.speed_limit if edge1.speed_limit is not None else 13.89  # Default ~50 km/h
        speed2 = edge2.speed_limit if edge2.speed_limit is not None else 13.89  # Default ~50 km/h
        speed_diff = abs(speed1 - speed2)
        cost += speed_diff * 0.1  # Penalty factor
        
        return cost
        
    def _reconstruct_path(self, parent: Dict[str, str], current: str, 
                         start_lane: str, goal_lane: str) -> List[str]:
        """Reconstruct the path from parent map.
        
        Args:
            parent: Map of edge IDs to their parent edge IDs
            current: Current edge ID
            start_lane: Starting lane ID
            goal_lane: Goal lane ID
            
        Returns:
            List of lane IDs representing the path
        """
        path = []
        while current in parent:
            edge = self.edges[current]
            # Add the appropriate lane from this edge
            if len(path) == 0:
                path.append(goal_lane)
            else:
                # Choose the lane that connects best with the previous lane
                best_lane = self._choose_best_lane(edge.lanes, path[-1])
                path.append(best_lane)
            current = parent[current]
            
        # Add the starting lane
        path.append(start_lane)
        return list(reversed(path))
        
    def _choose_best_lane(self, lanes: List[str], prev_lane: str) -> str:
        """Choose the best lane from a list of lanes based on the previous lane.
        
        Args:
            lanes: List of available lane IDs
            prev_lane: Previous lane ID
            
        Returns:
            Best lane ID
        """
        # For now, just return the first lane
        # This could be improved by considering lane connections and traffic rules
        return lanes[0]
        
    def get_lane_sequence(self, path: List[str]) -> List[Tuple[float, float]]:
        """Convert a path of lane IDs into a sequence of (x,y) points.
        
        Args:
            path: List of lane IDs
            
        Returns:
            List of (x,y) points representing the path
        """
        points = []
        for lane_id in path:
            edge_id = self.lane_to_edge[lane_id]
            edge = self.edges[edge_id]
            
            # Get the center points of the edge
            from_node = self.nodes[edge.from_node]
            to_node = self.nodes[edge.to_node]
            
            # Add points along the edge
            length = edge.length if edge.length is not None else 100.0  # Default 100m
            num_points = max(2, int(length / 10))  # One point every 10 meters
            for i in range(num_points):
                t = i / (num_points - 1)
                x = from_node.x + t * (to_node.x - from_node.x)
                y = from_node.y + t * (to_node.y - from_node.y)
                points.append((x, y))
                
        return points 