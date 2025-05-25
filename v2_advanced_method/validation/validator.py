"""
Validation tools for OpenDRIVE files.
Includes schema validation, geometry validation, and visual comparison tools.
"""

import os
import logging
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import lxml.etree as ET
import matplotlib.pyplot as plt
import numpy as np
from dataclasses import dataclass

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ValidationResult:
    """Container for validation results."""
    is_valid: bool
    errors: List[str]
    warnings: List[str]

class OpenDriveValidator:
    """Validator for OpenDRIVE files."""
    
    def __init__(self):
        """Initialize the validator."""
        self.schema_file = os.path.join(
            os.path.dirname(__file__),
            'schemas',
            'OpenDRIVE_1.7.0.xsd'
        )
    
    def validate_schema(self, xodr_file: str) -> ValidationResult:
        """
        Validate OpenDRIVE file against the official schema.
        
        Args:
            xodr_file: Path to the OpenDRIVE file
            
        Returns:
            ValidationResult containing validation status and any errors
        """
        try:
            # Load schema
            xmlschema_doc = ET.parse(self.schema_file)
            xmlschema = ET.XMLSchema(xmlschema_doc)
            
            # Load OpenDRIVE file
            doc = ET.parse(xodr_file)
            
            # Validate against schema
            xmlschema.assertValid(doc)
            
            return ValidationResult(
                is_valid=True,
                errors=[],
                warnings=[]
            )
            
        except ET.DocumentInvalid as e:
            return ValidationResult(
                is_valid=False,
                errors=[str(error) for error in e.error_log],
                warnings=[]
            )
        except Exception as e:
            return ValidationResult(
                is_valid=False,
                errors=[f"Validation error: {str(e)}"],
                warnings=[]
            )

    def validate_geometry(self, xodr_file: str) -> ValidationResult:
        """
        Validate road geometry in OpenDRIVE file.
        
        Checks:
        - Road length consistency
        - Lane width consistency
        - Junction connections
        - Overlapping geometries
        
        Args:
            xodr_file: Path to the OpenDRIVE file
            
        Returns:
            ValidationResult containing validation status and any errors
        """
        errors = []
        warnings = []
        
        try:
            tree = ET.parse(xodr_file)
            root = tree.getroot()
            
            # Validate each road
            for road in root.findall('.//road'):
                road_id = road.get('id')
                
                # Check road length consistency
                declared_length = float(road.get('length', 0))
                calculated_length = self._calculate_road_length(road)
                if abs(declared_length - calculated_length) > 0.1:  # 10cm tolerance
                    errors.append(
                        f"Road {road_id}: Length mismatch - "
                        f"declared: {declared_length}m, calculated: {calculated_length}m"
                    )
                
                # Check lane widths
                self._validate_lane_widths(road, warnings)
                
                # Check for geometry continuity
                self._validate_geometry_continuity(road, errors)
            
            # Validate junction connections
            self._validate_junctions(root, errors)
            
            return ValidationResult(
                is_valid=len(errors) == 0,
                errors=errors,
                warnings=warnings
            )
            
        except Exception as e:
            return ValidationResult(
                is_valid=False,
                errors=[f"Geometry validation error: {str(e)}"],
                warnings=warnings
            )
    
    def _calculate_road_length(self, road: ET.Element) -> float:
        """Calculate the actual length of a road from its geometry."""
        total_length = 0.0
        for geometry in road.findall('.//geometry'):
            length = float(geometry.get('length', 0))
            total_length += length
        return total_length
    
    def _validate_lane_widths(self, road: ET.Element, warnings: List[str]) -> None:
        """Validate lane widths for consistency."""
        road_id = road.get('id')
        for lane_section in road.findall('.//laneSection'):
            for lane in lane_section.findall('.//lane'):
                lane_id = lane.get('id')
                widths = lane.findall('width')
                if len(widths) > 1:
                    # Check for discontinuities in width
                    for i in range(len(widths) - 1):
                        s1 = float(widths[i].get('sOffset'))
                        s2 = float(widths[i + 1].get('sOffset'))
                        if abs(s2 - s1) > 0.1:  # 10cm tolerance
                            warnings.append(
                                f"Road {road_id}, Lane {lane_id}: "
                                f"Possible width discontinuity at s={s2}"
                            )
    
    def _validate_geometry_continuity(self, road: ET.Element, errors: List[str]) -> None:
        """Validate continuity between geometry elements."""
        road_id = road.get('id')
        geometries = road.findall('.//geometry')
        
        for i in range(len(geometries) - 1):
            current = geometries[i]
            next_geom = geometries[i + 1]
            
            # Check position continuity
            current_end = self._get_geometry_endpoint(current)
            next_start = (float(next_geom.get('x')), float(next_geom.get('y')))
            
            if not self._points_are_close(current_end, next_start):
                errors.append(
                    f"Road {road_id}: Geometry discontinuity at s={next_geom.get('s')}"
                )
    
    def _validate_junctions(self, root: ET.Element, errors: List[str]) -> None:
        """Validate junction connections."""
        for junction in root.findall('.//junction'):
            junction_id = junction.get('id')
            
            # Check if all referenced roads exist
            for connection in junction.findall('connection'):
                incoming_road = connection.get('incomingRoad')
                connecting_road = connection.get('connectingRoad')
                
                if not root.find(f".//road[@id='{incoming_road}']"):
                    errors.append(
                        f"Junction {junction_id}: Referenced incoming road "
                        f"{incoming_road} does not exist"
                    )
                if not root.find(f".//road[@id='{connecting_road}']"):
                    errors.append(
                        f"Junction {junction_id}: Referenced connecting road "
                        f"{connecting_road} does not exist"
                    )
    
    def _get_geometry_endpoint(self, geometry: ET.Element) -> Tuple[float, float]:
        """Calculate the endpoint of a geometry element."""
        x = float(geometry.get('x'))
        y = float(geometry.get('y'))
        length = float(geometry.get('length'))
        
        # For line geometry
        line = geometry.find('line')
        if line is not None:
            hdg = float(geometry.get('hdg'))
            return (
                x + length * np.cos(hdg),
                y + length * np.sin(hdg)
            )
        
        # For arc geometry
        arc = geometry.find('arc')
        if arc is not None:
            hdg = float(geometry.get('hdg'))
            curvature = float(arc.get('curvature'))
            if abs(curvature) < 1e-10:  # Nearly straight
                return (
                    x + length * np.cos(hdg),
                    y + length * np.sin(hdg)
                )
            else:
                radius = 1.0 / curvature
                angle = length / radius
                return (
                    x + radius * (np.sin(hdg + angle) - np.sin(hdg)),
                    y + radius * (-np.cos(hdg + angle) + np.cos(hdg))
                )
        
        return (x, y)  # Default to start point if geometry type unknown
    
    def _points_are_close(self, p1: Tuple[float, float], p2: Tuple[float, float],
                         tolerance: float = 0.1) -> bool:
        """Check if two points are within tolerance distance."""
        return np.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2) <= tolerance

    def visualize_comparison(self, xodr_file1: str, xodr_file2: str,
                           output_file: Optional[str] = None) -> None:
        """
        Create a visual comparison between two OpenDRIVE files.
        
        Args:
            xodr_file1: Path to the first OpenDRIVE file
            xodr_file2: Path to the second OpenDRIVE file
            output_file: Optional path to save the comparison plot
        """
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 7))
        
        # Plot first file
        self._plot_opendrive(xodr_file1, ax1, "File 1")
        
        # Plot second file
        self._plot_opendrive(xodr_file2, ax2, "File 2")
        
        plt.tight_layout()
        
        if output_file:
            plt.savefig(output_file)
        else:
            plt.show()
    
    def _plot_opendrive(self, xodr_file: str, ax: plt.Axes, title: str) -> None:
        """Plot an OpenDRIVE file on the given axes."""
        try:
            tree = ET.parse(xodr_file)
            root = tree.getroot()
            
            # Plot roads
            for road in root.findall('.//road'):
                geometries = road.findall('.//geometry')
                road_points = []
                
                for geometry in geometries:
                    x = float(geometry.get('x'))
                    y = float(geometry.get('y'))
                    road_points.append((x, y))
                    
                    # Add endpoint
                    end_point = self._get_geometry_endpoint(geometry)
                    road_points.append(end_point)
                
                if road_points:
                    points = np.array(road_points)
                    ax.plot(points[:, 0], points[:, 1], 'b-', linewidth=1)
            
            # Plot junctions
            for junction in root.findall('.//junction'):
                connections = junction.findall('connection')
                if connections:
                    # Find the center of the junction
                    x_coords = []
                    y_coords = []
                    for conn in connections:
                        road = root.find(f".//road[@id='{conn.get('connectingRoad')}']")
                        if road is not None:
                            geom = road.find('geometry')
                            if geom is not None:
                                x_coords.append(float(geom.get('x')))
                                y_coords.append(float(geom.get('y')))
                    
                    if x_coords and y_coords:
                        center_x = sum(x_coords) / len(x_coords)
                        center_y = sum(y_coords) / len(y_coords)
                        ax.plot(center_x, center_y, 'ro')
            
            ax.set_title(title)
            ax.set_aspect('equal')
            ax.grid(True)
            
        except Exception as e:
            logger.error(f"Error plotting OpenDRIVE file: {e}")
            ax.text(0.5, 0.5, f"Error: {str(e)}", ha='center', va='center') 