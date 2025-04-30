"""
Script to create an interactive visualization of Kadıköy's road network using Folium.
"""

import os
import folium
import osmnx as ox
from folium import plugins
import networkx as nx

def create_interactive_map(place_name="Kadıköy, Istanbul, Turkey", 
                         output_file="data/plots/kadikoy_interactive.html"):
    """
    Create an interactive web map of the road network.
    
    Args:
        place_name: Name of the place to visualize
        output_file: Path to save the HTML map
    """
    print(f"Loading data for {place_name}...")
    
    # Get the network
    G = ox.graph_from_place(place_name, network_type="drive")
    
    # Get the center point
    center_point = ox.geocode(place_name)
    
    # Create a map centered on Kadıköy
    m = folium.Map(location=[center_point[0], center_point[1]], 
                  zoom_start=14,
                  tiles='cartodbpositron')  # Using a clean map style
    
    # Add different map tile layers
    folium.TileLayer(
        'OpenStreetMap',
        attr='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
    ).add_to(m)
    
    folium.TileLayer(
        'CartoDB dark_matter',
        attr='&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="http://cartodb.com/attributions">CartoDB</a>'
    ).add_to(m)
    
    # Convert network to GeoDataFrame
    nodes, edges = ox.graph_to_gdfs(G)
    
    # Add edges (roads) to the map with different colors based on road type
    def get_color(highway_type):
        colors = {
            'motorway': 'red',
            'trunk': 'orange',
            'primary': 'yellow',
            'secondary': 'green',
            'tertiary': 'blue',
            'residential': 'purple',
            'living_street': 'pink'
        }
        return colors.get(highway_type, 'gray')
    
    # Add edges with popup information
    for _, row in edges.iterrows():
        # Get road properties
        highway_type = row.get('highway', 'unknown')
        if isinstance(highway_type, list):
            highway_type = highway_type[0]
        
        # Create popup content
        popup_content = f"""
        <b>Road Type:</b> {highway_type}<br>
        <b>Name:</b> {row.get('name', 'Unnamed')}<br>
        <b>Oneway:</b> {row.get('oneway', 'No')}<br>
        """
        
        # Draw the road segment
        folium.PolyLine(
            locations=[(lat, lon) for lon, lat in row['geometry'].coords],
            color=get_color(highway_type),
            weight=2,
            opacity=0.8,
            popup=folium.Popup(popup_content, max_width=300)
        ).add_to(m)
    
    # Add important locations (nodes) with high degree centrality
    node_centrality = nx.degree_centrality(G)
    important_nodes = sorted(node_centrality.items(), key=lambda x: x[1], reverse=True)[:10]
    
    for node_id, _ in important_nodes:
        node = G.nodes[node_id]
        folium.CircleMarker(
            location=(node['y'], node['x']),
            radius=5,
            color='red',
            fill=True,
            popup=f'Major Intersection\nID: {node_id}'
        ).add_to(m)
    
    # Add map features
    folium.LayerControl().add_to(m)  # Layer control
    plugins.Fullscreen().add_to(m)    # Fullscreen button
    plugins.MiniMap().add_to(m)       # Mini map
    
    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    # Save the map
    m.save(output_file)
    print(f"\nInteractive map saved to {output_file}")
    print("\nInstructions:")
    print("1. Open the generated HTML file in your web browser")
    print("2. Use mouse wheel or +/- buttons to zoom in/out")
    print("3. Click and drag to pan around")
    print("4. Click on roads to see their properties")
    print("5. Use the layer control in the top right to switch base maps")
    print("6. Click the fullscreen button to view in full screen")

if __name__ == "__main__":
    create_interactive_map() 