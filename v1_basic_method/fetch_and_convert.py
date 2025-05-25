#!/usr/bin/env python3
"""
🏗️ VERSION 1: Basic OSM Data Fetching & Conversion
=================================================

This is the basic, primitive method for:
1. Fetching OSM data for Üsküdar, Istanbul
2. Converting to SUMO network format
3. Creating basic output

WHAT THIS VERSION CREATES:
- data/osm/üsküdar__istanbul__turkey.osm (7.4 MB)
- Basic SUMO network files
- Foundation for advanced processing
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__)))

from osm_fetcher.fetcher import OSMFetcher
from converter.osm_to_sumo import convert_osm_to_sumo
import subprocess


def main():
    """Main pipeline for Version 1: Basic data creation"""
    
    print("=" * 60)
    print("🏗️ VERSION 1: BASIC OSM DATA FETCHING & CONVERSION")
    print("=" * 60)
    
    # Step 1: Fetch OSM Data
    print("\n📍 Step 1: Fetching Üsküdar OSM Data...")
    fetcher = OSMFetcher()
    
    # Create data directory
    os.makedirs("data/osm", exist_ok=True)
    
    try:
        osm_file = fetcher.fetch_by_place_name(
            place_name="Üsküdar, Istanbul, Turkey",
            output_file="data/osm/üsküdar__istanbul__turkey.osm"
        )
        print(f"✅ OSM data saved: {osm_file}")
        
        # Get file stats
        if os.path.exists(osm_file):
            size_mb = os.path.getsize(osm_file) / (1024 * 1024)
            print(f"📊 File size: {size_mb:.1f} MB")
        
    except Exception as e:
        print(f"❌ Failed to fetch OSM data: {e}")
        return False
    
    # Step 2: Convert to SUMO
    print("\n🔄 Step 2: Converting OSM to SUMO...")
    
    try:
        # Create basic output directory
        basic_output = "data/sumo_basic"
        os.makedirs(basic_output, exist_ok=True)
        
        # Convert using netconvert
        sumo_file = os.path.join(basic_output, "uskudar_basic.net.xml")
        
        cmd = [
            "netconvert",
            "--osm-files", osm_file,
            "-o", sumo_file,
            "--geometry.remove",
            "--roundabouts.guess",
            "--ramps.guess",
            "--junctions.join",
            "--tls.guess-signals",
            "--tls.discard-simple"
        ]
        
        print(f"Running: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"✅ SUMO network created: {sumo_file}")
            
            if os.path.exists(sumo_file):
                size_mb = os.path.getsize(sumo_file) / (1024 * 1024)
                print(f"📊 SUMO file size: {size_mb:.1f} MB")
        else:
            print(f"❌ SUMO conversion failed: {result.stderr}")
            return False
            
    except FileNotFoundError:
        print("❌ SUMO not found! Please install SUMO.")
        return False
    except Exception as e:
        print(f"❌ Error during conversion: {e}")
        return False
    
    # Summary
    print("\n" + "=" * 60)
    print("🎉 VERSION 1 COMPLETE!")
    print("=" * 60)
    print("📁 Created files:")
    print(f"   🗺️  OSM Data: {osm_file}")
    print(f"   🚗 SUMO Network: {sumo_file}")
    print("\n💡 This forms the foundation for Version 2 advanced processing!")
    
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 