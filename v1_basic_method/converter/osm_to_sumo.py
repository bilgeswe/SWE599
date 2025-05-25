"""
Convert OSM files to SUMO network format.

This script uses SUMO's Python tools to convert OpenStreetMap data to SUMO network format.
"""

import os
import sys
import logging
import argparse
import tempfile
import subprocess
import shutil
from pathlib import Path
import xml.etree.ElementTree as ET
import sumolib

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SUMOConverter:
    """Class for converting OSM to SUMO network format."""
    
    def __init__(self):
        """Initialize the converter."""
        self.netconvert_paths = [
            "/opt/homebrew/opt/sumo/bin/netconvert",
            "/usr/local/opt/sumo/bin/netconvert",
            "/usr/bin/netconvert",
            "netconvert"  # Try from PATH
        ]
        
    def find_netconvert(self) -> str:
        """Find the netconvert executable."""
        for path in self.netconvert_paths:
            if shutil.which(path) or (os.path.isfile(path) and os.access(path, os.X_OK)):
                return path
        raise RuntimeError("netconvert not found. Please install SUMO.")
    
    def validate_net_file(self, net_file: str) -> bool:
        """
        Validate the generated SUMO network file.
        
        Args:
            net_file: Path to the .net.xml file
            
        Returns:
            bool: True if valid, False otherwise
        """
        try:
            # Load the network
            net = sumolib.net.readNet(net_file)
            
            # Check for disconnected edges
            disconnected_edges = []
            for edge in net.getEdges():
                if not edge.getOutgoing():
                    disconnected_edges.append(edge.getID())
            
            if disconnected_edges:
                logger.warning(f"Found {len(disconnected_edges)} disconnected edges")
                for edge_id in disconnected_edges:
                    logger.warning(f"Disconnected edge: {edge_id}")
            
            # Check for sharp turns
            sharp_turns = []
            for edge in net.getEdges():
                for lane in edge.getLanes():
                    shape = lane.getShape()
                    if len(shape) >= 3:
                        angles = self._calculate_angles(shape)
                        for i, angle in enumerate(angles):
                            if angle > 150:  # Sharp turn threshold
                                sharp_turns.append((edge.getID(), i, angle))
            
            if sharp_turns:
                logger.warning(f"Found {len(sharp_turns)} sharp turns")
                for edge_id, segment, angle in sharp_turns:
                    logger.warning(f"Sharp turn in edge {edge_id} at segment {segment}: {angle:.1f}°")
            
            # Check for roundabouts
            roundabouts = net.getRoundabouts()
            if roundabouts:
                logger.info(f"Found {len(roundabouts)} roundabouts")
            
            return True
            
        except Exception as e:
            logger.error(f"Error validating network: {str(e)}")
            return False
    
    def _calculate_angles(self, shape):
        """Calculate angles between consecutive segments."""
        angles = []
        for i in range(len(shape) - 2):
            p1, p2, p3 = shape[i:i+3]
            v1 = (p2[0] - p1[0], p2[1] - p1[1])
            v2 = (p3[0] - p2[0], p3[1] - p2[1])
            angle = self._angle_between(v1, v2)
            angles.append(angle)
        return angles
    
    def _angle_between(self, v1, v2):
        """Calculate angle between two vectors in degrees."""
        import math
        dot = v1[0] * v2[0] + v1[1] * v2[1]
        det = v1[0] * v2[1] - v1[1] * v2[0]
        angle = math.degrees(math.atan2(det, dot))
        return abs(angle)
    
    def convert(self, input_file: str, output_file: str) -> bool:
        """
        Convert an OSM file to SUMO network format.
        
        Args:
            input_file: Path to the input OSM file
            output_file: Path to the output SUMO network file
            
        Returns:
            bool: True if conversion successful, False otherwise
        """
        logger.info("Converting to SUMO network format")
        
        try:
            # Create a temporary directory for intermediate files
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_dir = Path(temp_dir)
                
                # Copy input file to temp directory
                temp_osm = temp_dir / "temp.osm"
                with open(input_file, 'r') as src, open(temp_osm, 'w') as dst:
                    dst.write(src.read())
                
                # Convert using osmfilter and netconvert
                logger.info("Converting OSM to SUMO network format...")
                
                # First, try using osmfilter to clean up the OSM file
                osmfilter_cmd = [
                    "osmfilter",
                    str(temp_osm),
                    "--keep=highway=motorway,trunk,primary,secondary,tertiary,residential",
                    "-o=" + str(temp_dir / "filtered.osm")
                ]
                
                try:
                    subprocess.run(osmfilter_cmd, check=True, capture_output=True, text=True)
                    input_for_netconvert = temp_dir / "filtered.osm"
                except (subprocess.CalledProcessError, FileNotFoundError):
                    logger.warning("osmfilter not found or failed, proceeding with original OSM file")
                    input_for_netconvert = temp_osm
                
                # Prepare output directory
                output_path = Path(output_file)
                output_path.parent.mkdir(parents=True, exist_ok=True)
                
                # Get netconvert path
                netconvert = self.find_netconvert()
                
                # Print netconvert version
                try:
                    version_result = subprocess.run([netconvert, "--version"], capture_output=True, text=True)
                    logger.info(f"{netconvert} --version output:\n{version_result.stdout}\n{version_result.stderr}")
                except Exception as e:
                    logger.warning(f"Could not run {netconvert} --version: {e}")
                
                # Try the conversion with essential options
                cmd = [
                    netconvert,
                    "--osm-files", str(input_for_netconvert),
                    "--output-file", output_file,
                    "--geometry.remove",
                    "--roundabouts.guess",
                    "--ramps.guess",
                    "--junctions.join",
                    "--tls.guess-signals",
                    "--tls.discard-simple",
                    "--tls.join",
                    "--osm.all-attributes",
                    "--osm.skip-duplicates-check",
                    "--no-internal-links",
                    "--no-turnarounds",
                    "--geometry.max-grade.fix",
                    "--ignore-errors",
                    # Additional options to handle common issues
                    "--junctions.corner-detail", "5",  # Increase corner detail
                    "--junctions.limit-turn-speed", "5.5",  # Limit turn speeds
                    "--geometry.min-radius", "9",  # Minimum radius for curves
                    "--geometry.max-angle", "150",  # Maximum angle between segments
                    "--geometry.avoid-overlap", "true",  # Avoid overlapping edges
                    "--geometry.min-dist", "0.1"  # Minimum distance between nodes
                ]
                
                result = subprocess.run(cmd, capture_output=True, text=True)
                logger.info(f"STDOUT:\n{result.stdout}")
                logger.info(f"STDERR:\n{result.stderr}")
                
                if result.returncode != 0:
                    raise RuntimeError(f"netconvert failed with code {result.returncode}")
                
                if not os.path.exists(output_file):
                    raise RuntimeError(f"Output file was not created: {output_file}")
                
                # Validate the generated network
                if not self.validate_net_file(output_file):
                    logger.warning("Network validation found issues")
                
                logger.info(f"Successfully converted {input_file} to {output_file}")
                return True
                
        except Exception as e:
            logger.error(f"Error converting OSM to SUMO: {str(e)}")
            return False

def main():
    """Main function for testing the converter."""
    parser = argparse.ArgumentParser(description="Convert OSM file to SUMO network format")
    parser.add_argument("input_file", help="Input OSM file (.osm)")
    parser.add_argument("output_file", help="Output SUMO network file (.net.xml)")
    
    args = parser.parse_args()
    
    # Convert OSM to SUMO
    converter = SUMOConverter()
    success = converter.convert(args.input_file, args.output_file)
    
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main() 