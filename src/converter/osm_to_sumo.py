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

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def convert_osm_to_sumo(input_file: str, output_file: str) -> None:
    """
    Convert an OSM file to SUMO network format.
    
    Args:
        input_file: Path to the input OSM file
        output_file: Path to the output SUMO network file
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
            
            # Try different netconvert paths
            netconvert_paths = [
                "/opt/homebrew/opt/sumo/bin/netconvert",
                "/usr/local/opt/sumo/bin/netconvert",
                "/usr/bin/netconvert",
                "netconvert"  # Try from PATH
            ]
            
            success = False
            for netconvert in netconvert_paths:
                logger.info(f"Trying netconvert at: {netconvert}")
                # Check if the binary exists and is executable
                if not shutil.which(netconvert) and not (os.path.isfile(netconvert) and os.access(netconvert, os.X_OK)):
                    logger.warning(f"Not found or not executable: {netconvert}")
                    continue
                # Print netconvert version
                try:
                    version_result = subprocess.run([netconvert, "--version"], capture_output=True, text=True)
                    logger.info(f"{netconvert} --version output:\n{version_result.stdout}\n{version_result.stderr}")
                except Exception as e:
                    logger.warning(f"Could not run {netconvert} --version: {e}")
                # Try the conversion
                try:
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
                        "--ignore-errors"
                    ]
                    result = subprocess.run(cmd, capture_output=True, text=True)
                    logger.info(f"STDOUT:\n{result.stdout}")
                    logger.info(f"STDERR:\n{result.stderr}")
                    if result.returncode == 0:
                        success = True
                        break
                    else:
                        logger.error(f"netconvert failed with code {result.returncode}")
                except FileNotFoundError:
                    logger.warning(f"FileNotFoundError for {netconvert}")
                    continue
            
            if not success:
                raise RuntimeError("Failed to convert OSM to SUMO network: netconvert failed")
            
            if not os.path.exists(output_file):
                raise RuntimeError(f"Output file was not created: {output_file}")
            
            logger.info(f"Successfully converted {input_file} to {output_file}")
            
    except Exception as e:
        logger.error(f"Error converting OSM to SUMO: {str(e)}")
        raise RuntimeError("Failed to convert OSM to SUMO network")

def main():
    """Main function for testing the converter."""
    parser = argparse.ArgumentParser(description="Convert OSM file to SUMO network format")
    parser.add_argument("input_file", help="Input OSM file (.osm)")
    parser.add_argument("output_file", help="Output SUMO network file (.net.xml)")
    
    args = parser.parse_args()
    
    # Convert OSM to SUMO
    convert_osm_to_sumo(args.input_file, args.output_file)

if __name__ == "__main__":
    main() 