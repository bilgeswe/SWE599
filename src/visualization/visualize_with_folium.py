#!/usr/bin/env python3
import os
import folium
import osmnx as ox
from folium import plugins
import argparse

def get_road_style(feature):
    """Style function for road types"""
    highway = feature['properties'].get('highway', 'other')
    if isinstance(highway, list):
        highway = highway[0]
    
    if highway in ['motorway', 'trunk']:
        return {'color': '#e31a1c', 'weight': 4, 'opacity': 0.9}
    elif highway in ['motorway_link', 'trunk_link']:
        return {'color': '#e31a1c', 'weight': 3, 'opacity': 0.7}
    elif highway in ['primary']:
        return {'color': '#fb9a99', 'weight': 3, 'opacity': 0.9}
    elif highway in ['primary_link']:
        return {'color': '#fb9a99', 'weight': 2.5, 'opacity': 0.7}
    elif highway in ['secondary']:
        return {'color': '#33a02c', 'weight': 2.5, 'opacity': 0.9}
    elif highway in ['secondary_link']:
        return {'color': '#33a02c', 'weight': 2, 'opacity': 0.7}
    elif highway in ['tertiary']:
        return {'color': '#b2df8a', 'weight': 2, 'opacity': 0.9}
    elif highway in ['tertiary_link']:
        return {'color': '#b2df8a', 'weight': 1.5, 'opacity': 0.7}
    elif highway in ['residential', 'living_street']:
        return {'color': '#a6cee3', 'weight': 1.5, 'opacity': 0.9}
    elif highway in ['service', 'unclassified']:
        return {'color': '#cab2d6', 'weight': 1, 'opacity': 0.8}
    elif highway in ['pedestrian', 'footway', 'path']:
        return {'color': '#dddddd', 'weight': 1, 'opacity': 0.6}
    else:
        return {'color': '#666666', 'weight': 1, 'opacity': 0.5}

def visualize_with_folium(osm_file, output_dir='data/visualizations'):
    """
    Create an interactive visualization of a road network using Folium.
    
    Args:
        osm_file (str): Path to the OSM file
        output_dir (str): Directory to save the HTML file
    """
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Load the graph from OSM file
    print(f"Loading network from {osm_file}...")
    G = ox.graph_from_xml(osm_file)
    
    # Convert graph to GeoDataFrame
    nodes, edges = ox.graph_to_gdfs(G)
    
    # Calculate center point
    center_lat = nodes.geometry.y.mean()
    center_lon = nodes.geometry.x.mean()
    
    # Create a map centered on the area
    m = folium.Map(location=[center_lat, center_lon],
                  zoom_start=15,  # Increased zoom level
                  tiles='cartodbpositron')
    
    # Add different tile layers
    folium.TileLayer('openstreetmap').add_to(m)
    folium.TileLayer('cartodbdark_matter').add_to(m)
    folium.TileLayer('Stamen Terrain').add_to(m)
    
    # Add the road network with tooltips
    folium.GeoJson(
        edges,
        style_function=get_road_style,
        tooltip=folium.GeoJsonTooltip(
            fields=['name', 'highway', 'oneway', 'lanes', 'maxspeed', 'length'],
            aliases=['Name:', 'Type:', 'One-way:', 'Lanes:', 'Speed Limit:', 'Length (m):'],
            localize=True,
            sticky=False,
            labels=True
        )
    ).add_to(m)
    
    # Add useful plugins
    plugins.Fullscreen().add_to(m)
    plugins.MiniMap().add_to(m)
    plugins.MousePosition().add_to(m)
    
    # Add a legend
    legend_html = """
    <div style="position: fixed; bottom: 50px; left: 50px; z-index: 1000; background-color: white; padding: 10px; border: 2px solid grey; border-radius: 5px;">
    <p><strong>Road Types</strong></p>
    <p><span style='color: #e31a1c;'>━━</span> Motorway/Trunk</p>
    <p><span style='color: #fb9a99;'>━━</span> Primary</p>
    <p><span style='color: #33a02c;'>━━</span> Secondary</p>
    <p><span style='color: #b2df8a;'>━━</span> Tertiary</p>
    <p><span style='color: #a6cee3;'>━━</span> Residential</p>
    <p><span style='color: #cab2d6;'>━━</span> Service/Unclassified</p>
    <p><span style='color: #dddddd;'>━━</span> Pedestrian/Path</p>
    </div>
    """
    m.get_root().html.add_child(folium.Element(legend_html))
    
    # Get the base filename without extension and path
    base_name = os.path.splitext(os.path.basename(osm_file))[0]
    output_file = os.path.join(output_dir, f"{base_name}_interactive.html")
    
    # Save the map
    m.save(output_file)
    print(f"Interactive visualization saved as '{output_file}'")
    print("\nInstructions:")
    print("1. Open the generated HTML file in your web browser")
    print("2. Use mouse wheel or +/- buttons to zoom in/out")
    print("3. Click and drag to pan")
    print("4. Hover over roads to see their details")
    print("5. Use the layer control to switch between different map styles")
    print("6. Use the fullscreen button for a better view")
    print("7. Mini-map helps with orientation")
    print("8. Mouse position shows coordinates")
    print("9. Check the legend in the bottom-left corner")

def main():
    parser = argparse.ArgumentParser(description='Create interactive visualization of OSM road network')
    parser.add_argument('osm_file', help='Path to the OSM file')
    parser.add_argument('--output-dir', default='data/visualizations', help='Output directory for HTML files')
    
    args = parser.parse_args()
    visualize_with_folium(args.osm_file, args.output_dir)

if __name__ == "__main__":
    main() 