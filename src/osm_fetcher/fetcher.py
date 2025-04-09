"""
OpenStreetMap data fetcher using osmnx and Overpass API.
"""

import os
import osmnx as ox
from typing import Tuple, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OSMFetcher:
    def __init__(self, cache_dir: str = "data/osm"):
        """
        Initialize OSM Fetcher.
        
        Args:
            cache_dir: Directory to cache downloaded OSM data
        """
        self.cache_dir = cache_dir
        os.makedirs(cache_dir, exist_ok=True)
        
        # Configure osmnx settings (updated for newer versions)
        ox.settings.use_cache = True
        ox.settings.log_console = True
    
    def fetch_by_place(self, place_name: str, network_type: str = "drive") -> str:
        """
        Fetch OSM data for a named place.
        
        Args:
            place_name: Name of the place (e.g., "Istanbul, Turkey")
            network_type: Type of network to download ("drive", "walk", "bike", "all")
            
        Returns:
            Path to the saved OSM file
        """
        logger.info(f"Fetching OSM data for {place_name}")
        
        try:
            # Get the street network
            G = ox.graph_from_place(place_name, network_type=network_type)
            
            # Save to OSM file
            output_path = os.path.join(self.cache_dir, f"{place_name.replace(' ', '_')}.osm")
            ox.save_graph_xml(G, filepath=output_path)
            
            logger.info(f"Successfully saved OSM data to {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Error fetching OSM data: {str(e)}")
            raise
    
    def fetch_by_bbox(self, bbox: Tuple[float, float, float, float], 
                     network_type: str = "drive") -> str:
        """
        Fetch OSM data for a bounding box.
        
        Args:
            bbox: Tuple of (north, south, east, west) coordinates
            network_type: Type of network to download
            
        Returns:
            Path to the saved OSM file
        """
        logger.info(f"Fetching OSM data for bbox: {bbox}")
        
        try:
            # Get the street network
            G = ox.graph_from_bbox(*bbox, network_type=network_type)
            
            # Generate filename from coordinates
            filename = f"bbox_{bbox[0]}_{bbox[1]}_{bbox[2]}_{bbox[3]}.osm"
            output_path = os.path.join(self.cache_dir, filename)
            
            # Save to OSM file
            ox.save_graph_xml(G, filepath=output_path)
            
            logger.info(f"Successfully saved OSM data to {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Error fetching OSM data: {str(e)}")
            raise

if __name__ == "__main__":
    # Example usage
    fetcher = OSMFetcher()
    
    # Fetch by place name
    try:
        osm_file = fetcher.fetch_by_place("Besiktas, Istanbul")
        print(f"Downloaded OSM data to: {osm_file}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Fetch by bounding box (example coordinates for a small area)
    try:
        bbox = (41.05, 41.04, 29.01, 29.00)  # Small area in Istanbul
        osm_file = fetcher.fetch_by_bbox(bbox)
        print(f"Downloaded OSM data to: {osm_file}")
    except Exception as e:
        print(f"Error: {e}")