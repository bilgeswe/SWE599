"""
Script to visualize OSM data using osmnx and folium.
"""

import folium
import osmnx as ox
from folium import plugins

def visualize_area(place_name: str = "Beşiktaş, Istanbul, Turkey", 
                  output_file: str = "map.html",
                  network_type: str = 'all'):
    """
    Visualize an area using OSMnx and Folium.
    
    Args:
        place_name: Name of the place to visualize
        output_file: Path to save the HTML map
        network_type: Type of network to extract ('all', 'drive', 'bike', 'walk')
    """
    print(f"Loading data for {place_name}...")
    
    # Load the street network
    graph = ox.graph_from_place(place_name, network_type=network_type)
    
    # Get the center point
    center_point = ox.geocode(place_name)
    
    # Create a map centered on the area
    m = folium.Map(location=[center_point[0], center_point[1]], 
                  zoom_start=14,
                  tiles='cartodbpositron')  # Using a clean map style
    
    # Convert graph to GeoDataFrame
    nodes, edges = ox.graph_to_gdfs(graph)
    
    # Add edges to the map
    style_function = lambda x: {'color': 'blue', 'weight': 2, 'opacity': 0.7}
    folium.GeoJson(
        edges,
        style_function=style_function,
        tooltip=folium.GeoJsonTooltip(fields=['name'], labels=False)
    ).add_to(m)
    
    # Add layer control and fullscreen option
    folium.LayerControl().add_to(m)
    plugins.Fullscreen().add_to(m)
    
    # Save the map
    m.save(output_file)
    print(f"\nMap saved to {output_file}")
    print("\nInstructions:")
    print("1. Open the generated HTML file in your web browser")
    print("2. Use mouse wheel or +/- buttons to zoom in/out")
    print("3. Click and drag to pan")
    print("4. Hover over streets to see their names (if available)")
    print("5. Use the layer control in the top right to switch base maps")
    print("6. Click the fullscreen button to view the map in full screen")

if __name__ == "__main__":
    visualize_area() 