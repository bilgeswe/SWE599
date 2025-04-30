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
        
    def generate(self, output_file: str) -> None:
        """
        Generate OpenDRIVE file.
        
        Args:
            output_file: Path to output file
        """
        
    def add_road(self, road: Road) -> None:
        """
        Add a road to the OpenDRIVE file.
        
        Args:
            road: Road object to add
        """
        
    def add_junction(self, junction: Junction) -> None:
        """
        Add a junction to the OpenDRIVE file.
        
        Args:
            junction: Junction object to add
        """
```

## Validator Module

### `OpenDriveValidator`

```python
class OpenDriveValidator:
    """Validator for OpenDRIVE files."""
    
    def validate_schema(self, xodr_file: str) -> ValidationResult:
        """
        Validate OpenDRIVE file against schema.
        
        Args:
            xodr_file: Path to OpenDRIVE file
            
        Returns:
            ValidationResult object
        """
        
    def validate_geometry(self, xodr_file: str) -> ValidationResult:
        """
        Validate geometry of OpenDRIVE file.
        
        Args:
            xodr_file: Path to OpenDRIVE file
            
        Returns:
            ValidationResult object
        """
        
    def visualize_comparison(self, xodr_file1: str, xodr_file2: str) -> None:
        """
        Visualize comparison of two OpenDRIVE files.
        
        Args:
            xodr_file1: Path to first OpenDRIVE file
            xodr_file2: Path to second OpenDRIVE file
        """
```

## Data Classes

### `Network`

```python
@dataclass
class Network:
    """Represents a road network."""
    
    edges: List[Edge]
    junctions: List[Junction]
    name: str
```

### `Edge`

```python
@dataclass
class Edge:
    """Represents a road edge."""
    
    id: str
    from_node: str
    to_node: str
    lanes: List[Lane]
    geometry: List[Point]
```

### `Junction`

```python
@dataclass
class Junction:
    """Represents a road junction."""
    
    id: str
    connections: List[Connection]
    position: Point
```

### `Lane`

```python
@dataclass
class Lane:
    """Represents a road lane."""
    
    id: str
    width: float
    type: str
    speed: float
```

### `Point`

```python
@dataclass
class Point:
    """Represents a 2D point."""
    
    x: float
    y: float
```

## Utility Functions

### Data Fetching

```python
def download_by_place(place_name: str) -> str:
    """
    Download OSM data by place name.
    
    Args:
        place_name: Name of the place
        
    Returns:
        Path to downloaded file
    """
    
def download_by_coordinates(min_lat: float, max_lat: float,
                          min_lon: float, max_lon: float) -> str:
    """
    Download OSM data by coordinates.
    
    Args:
        min_lat: Minimum latitude
        max_lat: Maximum latitude
        min_lon: Minimum longitude
        max_lon: Maximum longitude
        
    Returns:
        Path to downloaded file
    """
```

### Visualization

```python
def plot_network(network: Network, output_file: str) -> None:
    """
    Plot road network.
    
    Args:
        network: Network to plot
        output_file: Path to output file
    """
    
def create_interactive_map(network: Network, output_file: str) -> None:
    """
    Create interactive map of network.
    
    Args:
        network: Network to plot
        output_file: Path to output file
    """
```

## Error Handling

### `ValidationError`

```python
class ValidationError(Exception):
    """Base class for validation errors."""
    
    def __init__(self, message: str, element: Optional[Element] = None):
        """
        Initialize validation error.
        
        Args:
            message: Error message
            element: XML element causing error
        """
```

### `ConversionError`

```python
class ConversionError(Exception):
    """Base class for conversion errors."""
    
    def __init__(self, message: str, source: str, target: str):
        """
        Initialize conversion error.
        
        Args:
            message: Error message
            source: Source format
            target: Target format
        """
```

## Configuration

### `Config`

```python
@dataclass
class Config:
    """Configuration settings."""
    
    # Validation settings
    validation_tolerance: float = 0.1
    max_road_length: float = 10000.0
    
    # Visualization settings
    plot_width: int = 800
    plot_height: int = 600
    colors: Dict[str, str] = field(default_factory=lambda: {
        'primary': 'red',
        'secondary': 'blue',
        'tertiary': 'green'
    })
```

## Constants

```python
# OpenDRIVE schema version
OPENDRIVE_SCHEMA_VERSION = "1.7.0"

# Default validation settings
DEFAULT_TOLERANCE = 0.1
DEFAULT_MAX_ROAD_LENGTH = 10000.0

# File extensions
OSM_EXTENSION = ".osm"
SUMO_EXTENSION = ".net.xml"
OPENDRIVE_EXTENSION = ".xodr"
``` 