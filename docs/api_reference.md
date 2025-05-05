# API Reference

This document provides detailed API documentation for the road network conversion and validation system.

## Converter Module

### `SumoNetworkParser`

```python
class SumoNetworkParser:
    """Parser for SUMO network files."""
    
    def __init__(self, net_file: str):
        """
        Initialize parser with SUMO network file.
        
        Args:
            net_file: Path to SUMO network file
        """
        
    def parse(self) -> Network:
        """
        Parse the SUMO network file.
        
        Returns:
            Network object containing parsed data
        """
        
    def get_edges(self) -> List[Edge]:
        """
        Get all edges from the network.
        
        Returns:
            List of Edge objects
        """
        
    def get_junctions(self) -> List[Junction]:
        """
        Get all junctions from the network.
        
        Returns:
            List of Junction objects
        """
        
    def get_traffic_lights(self) -> List[TrafficLight]:
        """
        Get all traffic lights from the network.
        
        Returns:
            List of TrafficLight objects
        """
```

### `OpenDriveGenerator`

```python
class OpenDriveGenerator:
    """Generator for OpenDRIVE files."""
    
    def __init__(self, network: Network):
        """
        Initialize generator with network data.
        
        Args:
            network: Network object to convert
        """
        
    def generate(self) -> ElementTree:
        """
        Generate OpenDRIVE XML structure.
        
        Returns:
            ElementTree containing OpenDRIVE data
        """
        
    def save(self, output_file: str) -> None:
        """
        Save OpenDRIVE file.
        
        Args:
            output_file: Path to save the file
        """
```

### `NetworkConverter`

```python
class NetworkConverter:
    """Main class for network format conversion."""
    
    def osm_to_sumo(self, osm_file: str, output_file: str, 
                    additional_options: Optional[List[str]] = None) -> bool:
        """
        Convert OSM file to SUMO network format.
        
        Args:
            osm_file: Path to input OSM file
            output_file: Path to output SUMO file
            additional_options: Optional list of netconvert options
            
        Returns:
            bool: True if conversion successful
        """
        
    def sumo_to_opendrive(self, sumo_file: str, output_file: str,
                         additional_options: Optional[List[str]] = None) -> bool:
        """
        Convert SUMO network to OpenDRIVE format.
        
        Args:
            sumo_file: Path to input SUMO file
            output_file: Path to output OpenDRIVE file
            additional_options: Optional list of netconvert options
            
        Returns:
            bool: True if conversion successful
        """
```

## Validator Module

### `NetworkValidator`

```python
class NetworkValidator:
    """Validator for road networks."""
    
    def __init__(self, network: Network):
        """
        Initialize validator with network data.
        
        Args:
            network: Network object to validate
        """
        
    def validate_structure(self) -> List[str]:
        """
        Validate network structure.
        
        Returns:
            List of validation errors
        """
        
    def validate_geometry(self) -> List[str]:
        """
        Validate network geometry.
        
        Returns:
            List of validation errors
        """
        
    def validate_connections(self) -> List[str]:
        """
        Validate network connections.
        
        Returns:
            List of validation errors
        """
```

### `JunctionValidator`

```python
class JunctionValidator:
    """Validator for network junctions."""
    
    def __init__(self, junction: Junction):
        """
        Initialize validator with junction data.
        
        Args:
            junction: Junction object to validate
        """
        
    def validate_type(self) -> bool:
        """
        Validate junction type.
        
        Returns:
            bool: True if type is valid
        """
        
    def validate_connections(self) -> List[str]:
        """
        Validate junction connections.
        
        Returns:
            List of validation errors
        """
        
    def validate_traffic_lights(self) -> List[str]:
        """
        Validate traffic light configuration.
        
        Returns:
            List of validation errors
        """
```

## Visualization Module

### `NetworkVisualizer`

```python
class NetworkVisualizer:
    """Visualizer for road networks."""
    
    def __init__(self, network: Network):
        """
        Initialize visualizer with network data.
        
        Args:
            network: Network object to visualize
        """
        
    def visualize_in_sumo(self) -> None:
        """
        Visualize network in SUMO GUI.
        """
        
    def create_interactive_map(self, output_file: str) -> None:
        """
        Create interactive map visualization.
        
        Args:
            output_file: Path to save the HTML file
        """
```

## Utility Module

### `CoordinateConverter`

```python
class CoordinateConverter:
    """Converter for coordinate systems."""
    
    @staticmethod
    def osm_to_sumo(lat: float, lon: float) -> Tuple[float, float]:
        """
        Convert OSM coordinates to SUMO coordinates.
        
        Args:
            lat: Latitude
            lon: Longitude
            
        Returns:
            Tuple of (x, y) coordinates
        """
        
    @staticmethod
    def sumo_to_opendrive(x: float, y: float) -> Tuple[float, float]:
        """
        Convert SUMO coordinates to OpenDRIVE coordinates.
        
        Args:
            x: X coordinate
            y: Y coordinate
            
        Returns:
            Tuple of (x, y) coordinates
        """
```

### `NetworkUtils`

```python
class NetworkUtils:
    """Utility functions for network operations."""
    
    @staticmethod
    def calculate_network_bounds(network: Network) -> Tuple[float, float, float, float]:
        """
        Calculate network boundaries.
        
        Args:
            network: Network object
            
        Returns:
            Tuple of (min_x, min_y, max_x, max_y)
        """
        
    @staticmethod
    def validate_file_path(file_path: str) -> bool:
        """
        Validate file path.
        
        Args:
            file_path: Path to validate
            
        Returns:
            bool: True if path is valid
        """
```

## Examples

### Converting OSM to SUMO
```python
from src.converter import NetworkConverter

# Initialize converter
converter = NetworkConverter()

# Convert OSM to SUMO
success = converter.osm_to_sumo(
    "data/networks/kadıköy.osm",
    "data/networks/kadıköy.net.xml",
    additional_options=["--geometry.remove", "--roundabouts.guess"]
)
```

### Validating Network
```python
from src.validator import NetworkValidator
from src.converter import SumoNetworkParser

# Parse network
parser = SumoNetworkParser("data/networks/kadıköy.net.xml")
network = parser.parse()

# Validate network
validator = NetworkValidator(network)
structure_errors = validator.validate_structure()
geometry_errors = validator.validate_geometry()
```

### Creating Interactive Map
```python
from src.visualization import NetworkVisualizer
from src.converter import SumoNetworkParser

# Parse network
parser = SumoNetworkParser("data/networks/kadıköy.net.xml")
network = parser.parse()

# Create visualization
visualizer = NetworkVisualizer(network)
visualizer.create_interactive_map("data/visualizations/kadıköy_interactive.html")
```

## Notes

- All classes are in the `src` directory
- Import paths are relative to the project root
- Make sure to have required dependencies installed
- Check the documentation for more detailed examples