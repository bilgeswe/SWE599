"""Coordinate transformation utilities for converting between different coordinate systems."""

import math
from typing import Tuple
import pyproj


class CoordinateTransformer:
    """Utility class for transforming coordinates between different systems."""
    
    def __init__(self, utm_zone: int = 35, utm_hemisphere: str = 'N'):
        """Initialize the coordinate transformer.
        
        Args:
            utm_zone: UTM zone number (default 35 for Istanbul)
            utm_hemisphere: UTM hemisphere ('N' or 'S')
        """
        self.utm_zone = utm_zone
        self.utm_hemisphere = utm_hemisphere
        
        # Define coordinate systems
        self.utm_crs = pyproj.CRS(f'+proj=utm +zone={utm_zone} +ellps=WGS84 +datum=WGS84 +units=m +no_defs')
        self.wgs84_crs = pyproj.CRS('EPSG:4326')  # WGS84 lat/lon
        
        # Create transformer
        self.transformer = pyproj.Transformer.from_crs(self.utm_crs, self.wgs84_crs, always_xy=True)
        self.reverse_transformer = pyproj.Transformer.from_crs(self.wgs84_crs, self.utm_crs, always_xy=True)
    
    def utm_to_latlon(self, x: float, y: float, offset_x: float = 0, offset_y: float = 0) -> Tuple[float, float]:
        """Convert UTM coordinates to latitude/longitude.
        
        Args:
            x: UTM easting coordinate (relative to network origin)
            y: UTM northing coordinate (relative to network origin)
            offset_x: X offset to add (from SUMO netOffset)
            offset_y: Y offset to add (from SUMO netOffset)
            
        Returns:
            Tuple of (longitude, latitude) in decimal degrees
        """
        # Add offset to get absolute UTM coordinates
        # Note: netOffset is typically negative, so adding it gives us the absolute coordinates
        utm_x = x - offset_x  # Subtract because netOffset is usually negative
        utm_y = y - offset_y  # Subtract because netOffset is usually negative
        
        # Transform to lat/lon
        lon, lat = self.transformer.transform(utm_x, utm_y)
        return lon, lat
    
    def latlon_to_utm(self, lon: float, lat: float, offset_x: float = 0, offset_y: float = 0) -> Tuple[float, float]:
        """Convert latitude/longitude to UTM coordinates.
        
        Args:
            lon: Longitude in decimal degrees
            lat: Latitude in decimal degrees
            offset_x: X offset to subtract (from SUMO netOffset)
            offset_y: Y offset to subtract (from SUMO netOffset)
            
        Returns:
            Tuple of (x, y) in UTM meters
        """
        # Transform to UTM
        utm_x, utm_y = self.reverse_transformer.transform(lon, lat)
        
        # Subtract offset to get relative coordinates
        x = utm_x - offset_x
        y = utm_y - offset_y
        
        return x, y


def get_uskudar_transformer() -> CoordinateTransformer:
    """Get a coordinate transformer configured for Üsküdar, Istanbul.
    
    Returns:
        CoordinateTransformer configured for UTM Zone 35N
    """
    return CoordinateTransformer(utm_zone=35, utm_hemisphere='N')


def transform_sumo_coordinates(positions: list, net_offset: Tuple[float, float]) -> list:
    """Transform SUMO coordinates to lat/lon for visualization.
    
    Args:
        positions: List of (x, y, heading) positions in SUMO coordinates
        net_offset: Network offset (netOffset from SUMO file)
        
    Returns:
        List of (lon, lat, heading) positions in WGS84 coordinates
    """
    transformer = get_uskudar_transformer()
    offset_x, offset_y = net_offset
    
    transformed_positions = []
    for x, y, heading in positions:
        lon, lat = transformer.utm_to_latlon(x, y, offset_x, offset_y)
        transformed_positions.append((lon, lat, heading))
    
    return transformed_positions


def transform_sumo_network(nodes: list, edges: list, net_offset: Tuple[float, float]) -> Tuple[list, list]:
    """Transform SUMO network coordinates to lat/lon.
    
    Args:
        nodes: List of Node objects with x, y coordinates
        edges: List of Edge objects with shape coordinates
        net_offset: Network offset (netOffset from SUMO file)
        
    Returns:
        Tuple of (transformed_nodes, transformed_edges)
    """
    transformer = get_uskudar_transformer()
    offset_x, offset_y = net_offset
    
    # Transform nodes
    for node in nodes:
        node.lon, node.lat = transformer.utm_to_latlon(node.x, node.y, offset_x, offset_y)
    
    # Transform edge shapes
    for edge in edges:
        if hasattr(edge, 'shape') and edge.shape:
            transformed_shape = []
            for x, y in edge.shape:
                lon, lat = transformer.utm_to_latlon(x, y, offset_x, offset_y)
                transformed_shape.append((lon, lat))
            edge.shape_latlon = transformed_shape
    
    return nodes, edges 