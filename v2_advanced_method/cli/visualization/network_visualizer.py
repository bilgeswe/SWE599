"""Network visualizer for road networks."""

import matplotlib.pyplot as plt
import numpy as np
from typing import Dict, List, Tuple, Optional
import networkx as nx
from matplotlib.colors import LinearSegmentedColormap
import matplotlib.cm as cm

class NetworkVisualizer:
    """Visualizes road network data."""
    
    def __init__(self):
        """Initialize the network visualizer."""
        self.fig = None
        self.ax = None
        self.network_data = None
        self.graph = None
    
    def visualize_network(self, network_data: Dict, output_file: Optional[str] = None,
                         show_statistics: bool = True, show_labels: bool = False,
                         color_by: str = "speed") -> None:
        """Visualize the road network.
        
        Args:
            network_data: Network data dictionary
            output_file: Optional file path to save the visualization
            show_statistics: Whether to show network statistics
            show_labels: Whether to show edge and junction labels
            color_by: Attribute to color edges by ("speed", "priority", "function")
        """
        self.network_data = network_data
        self.graph = self._create_graph()
        
        # Create figure
        self.fig, self.ax = plt.subplots(figsize=(12, 8))
        
        # Draw network
        self._draw_network(color_by)
        
        # Add labels if requested
        if show_labels:
            self._add_labels()
        
        # Add statistics if requested
        if show_statistics:
            self._add_statistics()
        
        # Add legend
        self._add_legend(color_by)
        
        # Add title
        plt.title("Road Network Visualization")
        
        # Save or show
        if output_file:
            plt.savefig(output_file, dpi=300, bbox_inches='tight')
        else:
            plt.show()
        
        plt.close()
    
    def _create_graph(self) -> nx.DiGraph:
        """Create a NetworkX graph from the network data.
        
        Returns:
            NetworkX directed graph
        """
        G = nx.DiGraph()
        
        # Add nodes (junctions)
        for junction in self.network_data["junctions"]:
            G.add_node(junction["id"], 
                      pos=(junction["x"], junction["y"]),
                      type=junction["type"])
        
        # Add edges
        for edge in self.network_data["edges"]:
            G.add_edge(edge["from"], edge["to"],
                      id=edge["id"],
                      speed=min(float(lane["speed"]) for lane in edge["lanes"] 
                              if lane.get("speed")),
                      priority=edge.get("priority", 0),
                      function=edge.get("function", "normal"))
        
        return G
    
    def _draw_network(self, color_by: str) -> None:
        """Draw the network on the current axes.
        
        Args:
            color_by: Attribute to color edges by
        """
        # Get node positions
        pos = nx.get_node_attributes(self.graph, 'pos')
        
        # Get edge colors
        if color_by == "speed":
            edge_colors = [self.graph[u][v]["speed"] for u, v in self.graph.edges()]
            cmap = cm.viridis
            vmin, vmax = 0, 200  # Speed range in km/h
        elif color_by == "priority":
            edge_colors = [self.graph[u][v]["priority"] for u, v in self.graph.edges()]
            cmap = cm.plasma
            vmin, vmax = -1, 78  # Priority range
        else:  # function
            functions = {"normal": 0, "internal": 1, "connector": 2}
            edge_colors = [functions[self.graph[u][v]["function"]] 
                          for u, v in self.graph.edges()]
            cmap = cm.Set3
            vmin, vmax = 0, 2
        
        # Draw edges
        nx.draw_networkx_edges(self.graph, pos,
                             edge_color=edge_colors,
                             edge_cmap=cmap,
                             edge_vmin=vmin,
                             edge_vmax=vmax,
                             width=2,
                             arrows=True,
                             arrowsize=20)
        
        # Draw nodes
        node_colors = []
        for node in self.graph.nodes():
            if self.graph.nodes[node]["type"] == "traffic_light":
                node_colors.append("red")
            elif self.graph.nodes[node]["type"] == "priority":
                node_colors.append("green")
            elif self.graph.nodes[node]["type"] == "dead_end":
                node_colors.append("gray")
            else:
                node_colors.append("blue")
        
        nx.draw_networkx_nodes(self.graph, pos,
                             node_color=node_colors,
                             node_size=100)
    
    def _add_labels(self) -> None:
        """Add labels to the network visualization."""
        pos = nx.get_node_attributes(self.graph, 'pos')
        
        # Add junction labels
        nx.draw_networkx_labels(self.graph, pos,
                              font_size=8,
                              font_weight='bold')
        
        # Add edge labels (edge IDs)
        edge_labels = {(u, v): self.graph[u][v]["id"] 
                      for u, v in self.graph.edges()}
        nx.draw_networkx_edge_labels(self.graph, pos,
                                   edge_labels=edge_labels,
                                   font_size=6)
    
    def _add_statistics(self) -> None:
        """Add network statistics to the visualization."""
        stats = [
            f"Total Edges: {len(self.network_data['edges'])}",
            f"Total Junctions: {len(self.network_data['junctions'])}",
            f"Total Lanes: {sum(len(edge['lanes']) for edge in self.network_data['edges'])}",
            f"Total Connections: {len(self.network_data['connections'])}"
        ]
        
        # Add statistics text box
        self.ax.text(0.02, 0.98, "\n".join(stats),
                    transform=self.ax.transAxes,
                    verticalalignment='top',
                    bbox=dict(boxstyle='round',
                            facecolor='white',
                            alpha=0.8))
    
    def _add_legend(self, color_by: str) -> None:
        """Add a legend to the visualization.
        
        Args:
            color_by: Attribute used for coloring
        """
        if color_by == "speed":
            # Create speed colorbar
            norm = plt.Normalize(0, 200)
            sm = plt.cm.ScalarMappable(cmap=cm.viridis, norm=norm)
            sm.set_array([])
            cbar = plt.colorbar(sm)
            cbar.set_label("Speed (km/h)")
        
        elif color_by == "priority":
            # Create priority colorbar
            norm = plt.Normalize(-1, 78)
            sm = plt.cm.ScalarMappable(cmap=cm.plasma, norm=norm)
            sm.set_array([])
            cbar = plt.colorbar(sm)
            cbar.set_label("Priority")
        
        else:  # function
            # Create function legend
            functions = {"normal": "Normal", "internal": "Internal", "connector": "Connector"}
            colors = cm.Set3(np.linspace(0, 1, 3))
            patches = [plt.Rectangle((0, 0), 1, 1, fc=color) 
                      for color in colors]
            self.ax.legend(patches, functions.values(),
                          loc='upper right',
                          title="Edge Function")
    
    def visualize_validation_results(self, validation_result: 'ValidationResult',
                                   output_file: Optional[str] = None) -> None:
        """Visualize validation results.
        
        Args:
            validation_result: Result of network validation
            output_file: Optional file path to save the visualization
        """
        # Create figure
        self.fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
        
        # Plot errors and warnings
        if validation_result.errors or validation_result.warnings:
            categories = ["Errors", "Warnings"]
            counts = [len(validation_result.errors), len(validation_result.warnings)]
            colors = ["red", "orange"]
            
            ax1.bar(categories, counts, color=colors)
            ax1.set_title("Validation Issues")
            ax1.set_ylabel("Count")
            
            # Add count labels
            for i, count in enumerate(counts):
                ax1.text(i, count, str(count),
                        ha='center', va='bottom')
        
        # Plot statistics
        if validation_result.statistics:
            stats = validation_result.statistics
            
            # Plot basic counts
            basic_stats = {
                "Edges": stats["total_edges"],
                "Junctions": stats["total_junctions"],
                "Lanes": stats["total_lanes"],
                "Connections": stats["total_connections"]
            }
            
            ax2.bar(basic_stats.keys(), basic_stats.values())
            ax2.set_title("Network Statistics")
            ax2.set_ylabel("Count")
            
            # Add count labels
            for i, count in enumerate(basic_stats.values()):
                ax2.text(i, count, str(count),
                        ha='center', va='bottom')
        
        plt.tight_layout()
        
        # Save or show
        if output_file:
            plt.savefig(output_file, dpi=300, bbox_inches='tight')
        else:
            plt.show()
        
        plt.close()
    
    def visualize_speed_distribution(self, output_file: Optional[str] = None) -> None:
        """Visualize speed distribution in the network.
        
        Args:
            output_file: Optional file path to save the visualization
        """
        # Collect speed data
        speeds = []
        for edge in self.network_data["edges"]:
            for lane in edge["lanes"]:
                if lane.get("speed"):
                    speeds.append(float(lane["speed"]))
        
        if not speeds:
            return
        
        # Create figure
        self.fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
        
        # Histogram
        ax1.hist(speeds, bins=20, color='blue', alpha=0.7)
        ax1.set_title("Speed Distribution")
        ax1.set_xlabel("Speed (km/h)")
        ax1.set_ylabel("Count")
        
        # Box plot
        ax2.boxplot(speeds, vert=False)
        ax2.set_title("Speed Statistics")
        ax2.set_xlabel("Speed (km/h)")
        
        plt.tight_layout()
        
        # Save or show
        if output_file:
            plt.savefig(output_file, dpi=300, bbox_inches='tight')
        else:
            plt.show()
        
        plt.close()
    
    def visualize_network_density(self, output_file: Optional[str] = None) -> None:
        """Visualize network density.
        
        Args:
            output_file: Optional file path to save the visualization
        """
        # Create figure
        self.fig, ax = plt.subplots(figsize=(10, 10))
        
        # Get node positions
        pos = nx.get_node_attributes(self.graph, 'pos')
        
        # Calculate node degrees
        degrees = dict(self.graph.degree())
        
        # Draw network with node sizes proportional to degree
        nx.draw_networkx_nodes(self.graph, pos,
                             node_size=[degrees[node] * 100 for node in self.graph.nodes()],
                             node_color='blue',
                             alpha=0.6)
        nx.draw_networkx_edges(self.graph, pos,
                             width=1,
                             alpha=0.4)
        
        # Add title
        plt.title("Network Density Visualization\n(Node size indicates number of connections)")
        
        # Save or show
        if output_file:
            plt.savefig(output_file, dpi=300, bbox_inches='tight')
        else:
            plt.show()
        
        plt.close() 