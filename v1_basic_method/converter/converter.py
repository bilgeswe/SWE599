"""
Converter module for OSM -> SUMO -> OpenDRIVE conversion pipeline.
"""

import os
import subprocess
import logging
from typing import Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MapConverter:
    def __init__(self, sumo_dir: str = "data/sumo", opendrive_dir: str = "data/opendrive"):
        """
        Initialize the converter.
        
        Args:
            sumo_dir: Directory to store SUMO network files
            opendrive_dir: Directory to store OpenDRIVE files
        """
        self.sumo_dir = sumo_dir
        self.opendrive_dir = opendrive_dir
        
        # Create directories if they don't exist
        os.makedirs(sumo_dir, exist_ok=True)
        os.makedirs(opendrive_dir, exist_ok=True)
    
    def osm_to_sumo(self, osm_file: str, output_name: Optional[str] = None) -> str:
        """
        Convert OSM file to SUMO network format using netconvert.
        
        Args:
            osm_file: Path to input OSM file
            output_name: Optional name for output file (without extension)
            
        Returns:
            Path to generated SUMO network file
        """
        if not os.path.exists(osm_file):
            raise FileNotFoundError(f"OSM file not found: {osm_file}")
        
        # Generate output filename if not provided
        if output_name is None:
            output_name = os.path.splitext(os.path.basename(osm_file))[0]
        
        output_file = os.path.join(self.sumo_dir, f"{output_name}.net.xml")
        
        logger.info(f"Converting {osm_file} to SUMO format...")
        
        try:
            # Run netconvert command
            cmd = [
                "netconvert",
                "--osm", osm_file,
                "--output", output_file,
                "--geometry.remove",  # Remove geometry nodes
                "--roundabouts.guess",  # Guess roundabouts
                "--ramps.guess",  # Guess ramps
                "--junctions.join",  # Join junctions
                "--tls.guess-signals",  # Guess traffic lights
                "--tls.discard-simple",  # Remove traffic lights at simple junctions
                "--verbose",
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                raise RuntimeError(f"netconvert failed: {result.stderr}")
            
            logger.info(f"Successfully converted to SUMO format: {output_file}")
            return output_file
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Error running netconvert: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error during conversion: {str(e)}")
            raise
    
    def sumo_to_opendrive(self, sumo_file: str, output_name: Optional[str] = None) -> str:
        """
        Convert SUMO network to OpenDRIVE format.
        
        Args:
            sumo_file: Path to input SUMO network file
            output_name: Optional name for output file (without extension)
            
        Returns:
            Path to generated OpenDRIVE file
        """
        if not os.path.exists(sumo_file):
            raise FileNotFoundError(f"SUMO network file not found: {sumo_file}")
        
        # Generate output filename if not provided
        if output_name is None:
            output_name = os.path.splitext(os.path.splitext(os.path.basename(sumo_file))[0])[0]
        
        output_file = os.path.join(self.opendrive_dir, f"{output_name}.xodr")
        
        logger.info(f"Converting {sumo_file} to OpenDRIVE format...")
        
        try:
            # Run netconvert command for OpenDRIVE conversion
            cmd = [
                "netconvert",
                "--sumo-net-file", sumo_file,
                "--opendrive-output", output_file,
                "--verbose",
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                raise RuntimeError(f"netconvert failed: {result.stderr}")
            
            logger.info(f"Successfully converted to OpenDRIVE format: {output_file}")
            return output_file
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Error running netconvert: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error during conversion: {str(e)}")
            raise

if __name__ == "__main__":
    # Example usage
    converter = MapConverter()
    
    try:
        # Example OSM file (you would need to have this file)
        osm_file = "data/osm/istanbul_43r.osm"
                
        # Convert OSM to SUMO
        sumo_file = converter.osm_to_sumo(osm_file)
        print(f"Created SUMO network file: {sumo_file}")
        
        # Convert SUMO to OpenDRIVE
        opendrive_file = converter.sumo_to_opendrive(sumo_file)
        print(f"Created OpenDRIVE file: {opendrive_file}")
        
    except Exception as e:
        print(f"Error: {e}")