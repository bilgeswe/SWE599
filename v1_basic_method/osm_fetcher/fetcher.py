"""
OpenStreetMap data fetcher using osmnx and Overpass API.
"""

import os
import osmnx as ox
import networkx as nx
from typing import Tuple, Optional, Dict
import logging
import argparse

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configure OSMnx
ox.settings.use_cache = True
ox.settings.cache_folder = 'data/cache'
ox.settings.all_oneway = True
ox.settings.useful_tags_path = [
    'bridge', 'tunnel', 'oneway', 'lanes', 'ref', 'name',
    'highway', 'maxspeed', 'service', 'access', 'area',
    'landuse', 'width', 'est_width', 'junction'
]

class OSMFetcher:
    def __init__(self, cache_dir: str = "data/osm"):
        """
        Initialize OSM Fetcher.
        
        Args:
            cache_dir: Directory to cache downloaded OSM data
        """
        self.cache_dir = cache_dir
        os.makedirs(cache_dir, exist_ok=True)
        os.makedirs('data/cache', exist_ok=True)
        
        # Configure osmnx settings
        ox.settings.use_cache = True
        ox.settings.log_console = True
        ox.settings.all_oneway = True
        ox.settings.simplify_graph = False  # Don't simplify for OSM XML export
    
    def _normalize_place_name(self, place_name: str) -> str:
        """
        Normalize the place name to match the Makefile's PLACE_TO_FILENAME logic.
        Lowercase, replace spaces and commas with underscores.
        """
        return place_name.strip().lower().replace(' ', '_').replace(',', '_')

    def fetch_by_place(self, place_name: str, network_type: str = "all") -> str:
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
            # Download with custom filter to include all road types
            custom_filter = (
                '["highway"]'
                '["highway"!~"abandoned|construction|proposed|platform|raceway"]'
                '["area"!~"yes"]'
                '["service"!~"private"]'
            )
            
            # Get the street network without simplification
            G = ox.graph_from_place(
                place_name,
                network_type=network_type,
                simplify=False,
                retain_all=True,
                truncate_by_edge=True,
                custom_filter=custom_filter
            )
            
            # Use normalized full place name for filename
            place_name_simple = self._normalize_place_name(place_name)
            output_path = os.path.join(self.cache_dir, f"{place_name_simple}.osm")
            ox.save_graph_xml(G, filepath=output_path)
            
            # Log network statistics
            self._log_network_stats(G)
            
            logger.info(f"Successfully saved OSM data to {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Error fetching OSM data: {str(e)}")
            logger.info("Trying with a smaller area...")
            try:
                G = ox.graph_from_place(
                    place_name,
                    network_type=network_type,
                    simplify=False,
                    retain_all=True,
                    truncate_by_edge=True,
                    custom_filter=custom_filter,
                    which_result=1
                )
                
                # Use normalized full place name for filename
                place_name_simple = self._normalize_place_name(place_name)
                output_path = os.path.join(self.cache_dir, f"{place_name_simple}.osm")
                ox.save_graph_xml(G, filepath=output_path)
                
                # Log network statistics
                self._log_network_stats(G)
                
                logger.info(f"Successfully saved OSM data to {output_path}")
                return output_path
                
            except Exception as e:
                logger.error(f"Error fetching OSM data with smaller area: {str(e)}")
                raise
    
    def fetch_by_bbox(self, bbox: Tuple[float, float, float, float], 
                     network_type: str = "all") -> str:
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
            # Download with custom filter
            custom_filter = (
                '["highway"]'
                '["highway"!~"abandoned|construction|proposed|platform|raceway"]'
                '["area"!~"yes"]'
                '["service"!~"private"]'
            )
            
            # Get the street network without simplification
            north, south, east, west = bbox
            G = ox.graph.graph_from_bbox(
                north, south, east, west,
                network_type=network_type,
                simplify=False,
                retain_all=True,
                truncate_by_edge=True,
                custom_filter=custom_filter
            )
            
            # Generate filename from coordinates
            filename = f"bbox_{bbox[0]}_{bbox[1]}_{bbox[2]}_{bbox[3]}.osm"
            output_path = os.path.join(self.cache_dir, filename)
            
            # Save to OSM file
            ox.save_graph_xml(G, filepath=output_path)
            
            # Log network statistics
            self._log_network_stats(G)
            
            logger.info(f"Successfully saved OSM data to {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Error fetching OSM data: {str(e)}")
            raise
    
    def _log_network_stats(self, G: nx.Graph) -> None:
        """
        Log network statistics.
        
        Args:
            G: NetworkX graph object
        """
        logger.info("\nNetwork Statistics:")
        logger.info(f"Total nodes: {len(G.nodes())}")
        logger.info(f"Total edges: {len(G.edges())}")
        
        # Count road types
        road_types: Dict[str, int] = {}
        for _, _, data in G.edges(data=True):
            road_type = data.get('highway', 'unknown')
            if isinstance(road_type, list):
                road_type = road_type[0]
            road_types[road_type] = road_types.get(road_type, 0) + 1
        
        logger.info("\nRoad Types:")
        for road_type, count in sorted(road_types.items()):
            logger.info(f"{road_type}: {count} segments")

def main():
    """Command line interface for the OSM Fetcher."""
    parser = argparse.ArgumentParser(description='Download OSM road network data')
    parser.add_argument('place_name', help='Name of the place (e.g., "Levent, Istanbul, Turkey")')
    parser.add_argument('--output-dir', default='data/osm', help='Output directory')
    parser.add_argument('--network-type', default='all', 
                      choices=['drive', 'walk', 'bike', 'all'],
                      help='Type of network to download')
    
    args = parser.parse_args()
    
    try:
        fetcher = OSMFetcher(cache_dir=args.output_dir)
        output_path = fetcher.fetch_by_place(args.place_name, args.network_type)
        print(f"\nSuccessfully downloaded and saved road network to: {output_path}")
    except Exception as e:
        print(f"Error: {str(e)}")
        exit(1)

if __name__ == "__main__":
    main()