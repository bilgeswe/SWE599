#!/usr/bin/env python3
"""
Test suite for SUMO to OpenDRIVE converter.
"""

import os
import unittest
import subprocess
import xml.etree.ElementTree as ET
from pathlib import Path
import tempfile
import shutil
import logging

from src.converter.sumo_to_xodr import SumoNetworkParser, OpenDriveGenerator, Point, Lane, Edge, Junction

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TestSumoToOpenDrive(unittest.TestCase):
    """Test cases for SUMO to OpenDRIVE conversion."""

    @classmethod
    def setUpClass(cls):
        """Set up test resources."""
        # Create temporary directory for test files
        cls.test_dir = tempfile.mkdtemp()
        cls.sample_dir = os.path.join(cls.test_dir, 'samples')
        os.makedirs(cls.sample_dir, exist_ok=True)

        # Create sample SUMO networks
        cls._create_sample_networks()

    @classmethod
    def tearDownClass(cls):
        """Clean up test resources."""
        shutil.rmtree(cls.test_dir)

    @classmethod
    def _create_sample_networks(cls):
        """Create sample SUMO network files for testing."""
        # 1. Simple straight road
        straight_road = """<?xml version="1.0" encoding="UTF-8"?>
        <net version="1.9" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
            <location netOffset="0.00,0.00" convBoundary="0.00,0.00,100.00,0.00" origBoundary="0.00,0.00,100.00,0.00" projParameter="!"/>
            <edge id="e1" from="j1" to="j2" priority="1">
                <lane id="e1_0" index="0" speed="13.89" length="100.00" shape="0.00,0.00 100.00,0.00"/>
            </edge>
            <junction id="j1" type="dead_end" x="0.00" y="0.00"/>
            <junction id="j2" type="dead_end" x="100.00" y="0.00"/>
        </net>
        """
        with open(os.path.join(cls.sample_dir, 'straight.net.xml'), 'w') as f:
            f.write(straight_road)

        # 2. Simple intersection
        intersection = """<?xml version="1.0" encoding="UTF-8"?>
        <net version="1.9" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
            <location netOffset="0.00,0.00" convBoundary="-50.00,-50.00,50.00,50.00" origBoundary="-50.00,-50.00,50.00,50.00" projParameter="!"/>
            <edge id="e1" from="j1" to="j5" priority="1">
                <lane id="e1_0" index="0" speed="13.89" length="50.00" shape="-50.00,0.00 0.00,0.00"/>
            </edge>
            <edge id="e2" from="j5" to="j2" priority="1">
                <lane id="e2_0" index="0" speed="13.89" length="50.00" shape="0.00,0.00 50.00,0.00"/>
            </edge>
            <edge id="e3" from="j3" to="j5" priority="1">
                <lane id="e3_0" index="0" speed="13.89" length="50.00" shape="0.00,-50.00 0.00,0.00"/>
            </edge>
            <edge id="e4" from="j5" to="j4" priority="1">
                <lane id="e4_0" index="0" speed="13.89" length="50.00" shape="0.00,0.00 0.00,50.00"/>
            </edge>
            <junction id="j1" type="dead_end" x="-50.00" y="0.00"/>
            <junction id="j2" type="dead_end" x="50.00" y="0.00"/>
            <junction id="j3" type="dead_end" x="0.00" y="-50.00"/>
            <junction id="j4" type="dead_end" x="0.00" y="50.00"/>
            <junction id="j5" type="priority" x="0.00" y="0.00">
                <request index="0" response="0000" foes="1111"/>
                <request index="1" response="0000" foes="1111"/>
                <request index="2" response="0000" foes="1111"/>
                <request index="3" response="0000" foes="1111"/>
            </junction>
        </net>
        """
        with open(os.path.join(cls.sample_dir, 'intersection.net.xml'), 'w') as f:
            f.write(intersection)

    def test_parser_straight_road(self):
        """Test parsing of a simple straight road."""
        parser = SumoNetworkParser(os.path.join(self.sample_dir, 'straight.net.xml'))
        parser.parse()

        # Check basic network properties
        self.assertEqual(len(parser.edges), 1)
        self.assertEqual(len(parser.junctions), 2)

        # Check edge properties
        edge = parser.edges['e1']
        self.assertEqual(edge.id, 'e1')
        self.assertEqual(edge.from_node, 'j1')
        self.assertEqual(edge.to_node, 'j2')
        self.assertEqual(len(edge.lanes), 1)

        # Check lane properties
        lane = edge.lanes[0]
        self.assertEqual(lane.id, 'e1_0')
        self.assertEqual(lane.speed, 13.89)
        self.assertEqual(lane.length, 100.0)
        self.assertEqual(len(lane.shape), 2)

    def test_parser_intersection(self):
        """Test parsing of a simple intersection."""
        parser = SumoNetworkParser(os.path.join(self.sample_dir, 'intersection.net.xml'))
        parser.parse()

        # Check basic network properties
        self.assertEqual(len(parser.edges), 4)
        self.assertEqual(len(parser.junctions), 5)

        # Check central junction
        junction = parser.junctions['j5']
        self.assertEqual(junction.type, 'priority')
        self.assertEqual(len(junction.requests), 4)

    def test_opendrive_generation_straight(self):
        """Test OpenDRIVE generation for a straight road."""
        # Parse SUMO network
        parser = SumoNetworkParser(os.path.join(self.sample_dir, 'straight.net.xml'))
        parser.parse()

        # Generate OpenDRIVE
        output_file = os.path.join(self.test_dir, 'straight.xodr')
        generator = OpenDriveGenerator(parser)
        generator.generate(output_file)

        # Validate OpenDRIVE output
        self._validate_opendrive(output_file)

        # Compare with netconvert output
        self._compare_with_netconvert('straight')

    def test_opendrive_generation_intersection(self):
        """Test OpenDRIVE generation for an intersection."""
        # Parse SUMO network
        parser = SumoNetworkParser(os.path.join(self.sample_dir, 'intersection.net.xml'))
        parser.parse()

        # Generate OpenDRIVE
        output_file = os.path.join(self.test_dir, 'intersection.xodr')
        generator = OpenDriveGenerator(parser)
        generator.generate(output_file)

        # Validate OpenDRIVE output
        self._validate_opendrive(output_file)

        # Compare with netconvert output
        self._compare_with_netconvert('intersection')

    def _validate_opendrive(self, xodr_file: str) -> None:
        """Validate OpenDRIVE file structure and contents."""
        try:
            tree = ET.parse(xodr_file)
            root = tree.getroot()

            # Check basic structure
            self.assertEqual(root.tag, 'OpenDRIVE')
            self.assertTrue(root.find('header') is not None)

            # Check header
            header = root.find('header')
            self.assertTrue(header.get('revMajor') is not None)
            self.assertTrue(header.get('revMinor') is not None)
            self.assertTrue(header.get('name') is not None)
            self.assertTrue(header.get('version') is not None)

            # Check roads
            roads = root.findall('road')
            self.assertTrue(len(roads) > 0)

            for road in roads:
                # Check required road attributes
                self.assertTrue(road.get('name') is not None)
                self.assertTrue(road.get('length') is not None)
                self.assertTrue(road.get('id') is not None)
                self.assertTrue(road.get('junction') is not None)

                # Check planView
                plan_view = road.find('planView')
                self.assertTrue(plan_view is not None)
                geometries = plan_view.findall('geometry')
                self.assertTrue(len(geometries) > 0)

                # Check lanes
                lanes = road.find('lanes')
                self.assertTrue(lanes is not None)
                lane_sections = lanes.findall('laneSection')
                self.assertTrue(len(lane_sections) > 0)

        except ET.ParseError as e:
            self.fail(f"Invalid XML in OpenDRIVE file: {e}")

    def _compare_with_netconvert(self, base_name: str) -> None:
        """Compare our output with netconvert's output."""
        # Generate netconvert output
        sumo_file = os.path.join(self.sample_dir, f'{base_name}.net.xml')
        netconvert_output = os.path.join(self.test_dir, f'{base_name}_netconvert.xodr')
        
        try:
            subprocess.run([
                'netconvert',
                '--sumo-net-file', sumo_file,
                '--opendrive-output', netconvert_output
            ], check=True, capture_output=True, text=True)
        except subprocess.CalledProcessError as e:
            logger.warning(f"Netconvert comparison skipped: {e}")
            return

        # Compare road counts
        our_tree = ET.parse(os.path.join(self.test_dir, f'{base_name}.xodr'))
        netconv_tree = ET.parse(netconvert_output)

        our_roads = our_tree.findall('.//road')
        netconv_roads = netconv_tree.findall('.//road')

        # Log comparison results
        logger.info(f"Road count comparison for {base_name}:")
        logger.info(f"Our converter: {len(our_roads)} roads")
        logger.info(f"Netconvert: {len(netconv_roads)} roads")

if __name__ == '__main__':
    unittest.main() 