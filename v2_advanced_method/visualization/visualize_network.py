#!/usr/bin/env python3
import os
import osmnx as ox
import networkx as nx
import matplotlib.pyplot as plt
import argparse

def get_edge_colors(G):
    """Get colors for different road types"""
    colors = []
    for _, _, data in G.edges(data=True):
        if 'highway' in data:
            if isinstance(data['highway'], list):
                highway = data['highway'][0]
            else:
                highway = data['highway']
            
            if highway in ['motorway', 'trunk']:
                colors.append('#e31a1c')  # red
            elif highway in ['motorway_link', 'trunk_link']:
                colors.append('#fb9a99')  # light red
            elif highway in ['primary']:
                colors.append('#fb9a99')  # light red
            elif highway in ['primary_link']:
                colors.append('#fdbf6f')  # orange
            elif highway in ['secondary']:
                colors.append('#33a02c')  # green
            elif highway in ['secondary_link']:
                colors.append('#b2df8a')  # light green
            elif highway in ['tertiary']:
                colors.append('#b2df8a')  # light green
            elif highway in ['tertiary_link']:
                colors.append('#a6cee3')  # light blue
            elif highway in ['residential', 'living_street']:
                colors.append('#a6cee3')  # light blue
            elif highway in ['service', 'unclassified']:
                colors.append('#cab2d6')  # purple
            elif highway in ['pedestrian', 'footway', 'path']:
                colors.append('#dddddd')  # light grey
            else:
                colors.append('#666666')  # grey
        else:
            colors.append('#666666')  # grey
    return colors

def get_edge_widths(G):
    """Get widths for different road types"""
    widths = []
    for _, _, data in G.edges(data=True):
        if 'highway' in data:
            if isinstance(data['highway'], list):
                highway = data['highway'][0]
            else:
                highway = data['highway']
            
            if highway in ['motorway', 'trunk']:
                widths.append(2.0)
            elif highway in ['motorway_link', 'trunk_link']:
                widths.append(1.5)
            elif highway in ['primary']:
                widths.append(1.5)
            elif highway in ['primary_link']:
                widths.append(1.2)
            elif highway in ['secondary']:
                widths.append(1.2)
            elif highway in ['secondary_link']:
                widths.append(1.0)
            elif highway in ['tertiary']:
                widths.append(1.0)
            elif highway in ['tertiary_link']:
                widths.append(0.8)
            elif highway in ['residential', 'living_street']:
                widths.append(0.8)
            elif highway in ['service', 'unclassified']:
                widths.append(0.5)
            elif highway in ['pedestrian', 'footway', 'path']:
                widths.append(0.5)
            else:
                widths.append(0.5)
        else:
            widths.append(0.5)
    return widths

def visualize_network(osm_file, output_dir='data/plots'):
    """
    Visualize a road network from an OSM file and save it as PNG.
    
    Args:
        osm_file (str): Path to the OSM file
        output_dir (str): Directory to save the output PNG file
    """
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Load the graph from OSM file
    print(f"Loading network from {osm_file}...")
    G = ox.graph_from_xml(osm_file)
    
    # Get edge colors and widths based on road types
    edge_colors = get_edge_colors(G)
    edge_widths = get_edge_widths(G)
    
    # Create the visualization
    print("Creating visualization...")
    fig, ax = ox.plot_graph(G, 
                           node_size=0,  # Hide nodes for cleaner look
                           edge_color=edge_colors,
                           edge_linewidth=edge_widths,
                           edge_alpha=0.7,
                           bgcolor='black',
                           show=False,
                           close=False)
    
    # Add legend
    legend_elements = [
        plt.Line2D([0], [0], color='#e31a1c', linewidth=2, label='Motorway/Trunk'),
        plt.Line2D([0], [0], color='#fb9a99', linewidth=1.5, label='Primary'),
        plt.Line2D([0], [0], color='#33a02c', linewidth=1.2, label='Secondary'),
        plt.Line2D([0], [0], color='#b2df8a', linewidth=1.0, label='Tertiary'),
        plt.Line2D([0], [0], color='#a6cee3', linewidth=0.8, label='Residential'),
        plt.Line2D([0], [0], color='#cab2d6', linewidth=0.5, label='Service'),
        plt.Line2D([0], [0], color='#dddddd', linewidth=0.5, label='Pedestrian'),
    ]
    ax.legend(handles=legend_elements, loc='upper right', bbox_to_anchor=(1.1, 1.1),
             facecolor='black', edgecolor='white', labelcolor='white')
    
    # Get the base filename without extension and path
    base_name = os.path.splitext(os.path.basename(osm_file))[0]
    output_file = os.path.join(output_dir, f"{base_name}_network.png")
    
    # Save the plot with high DPI and tight layout
    plt.savefig(output_file, dpi=300, bbox_inches='tight', facecolor='black', edgecolor='none')
    print(f"Network visualization saved as '{output_file}'")
    plt.close()

def main():
    parser = argparse.ArgumentParser(description='Visualize OSM road network and save as PNG')
    parser.add_argument('osm_file', help='Path to the OSM file')
    parser.add_argument('--output-dir', default='data/plots', help='Output directory for PNG files')
    
    args = parser.parse_args()
    visualize_network(args.osm_file, args.output_dir)

if __name__ == "__main__":
    main() 