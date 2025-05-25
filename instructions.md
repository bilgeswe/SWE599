# 🏙️ Üsküdar AV Simulation Project - Complete Instructions

> **Comprehensive guide for building professional OpenDRIVE/OpenSCENARIO export systems and AV simulation environments using real-world Istanbul data.**

## 📋 Table of Contents

1. [🚀 Quick Start](#-quick-start)
2. [🏗️ Project Architecture](#️-project-architecture)
3. [📦 Installation & Setup](#-installation--setup)
4. [🔄 Format Specifications](#-format-specifications)
5. [🎯 Version 1: Basic Method](#-version-1-basic-method)
6. [🚀 Version 2: Advanced Method](#-version-2-advanced-method)
7. [🧪 Testing & Validation](#-testing--validation)
8. [📊 Visualization Methods](#-visualization-methods)
9. [🔧 Development Guidelines](#-development-guidelines)
10. [🔍 API Reference](#-api-reference)
11. [🛠️ Troubleshooting](#️-troubleshooting)

---

## 🚀 Quick Start

### **Recommended: Full Pipeline**
```bash
# Step 1: Create foundation data (Version 1)
cd v1_basic_method
python fetch_and_convert.py

# Step 2: Build advanced simulation (Version 2)
cd ../v2_advanced_method  
python advanced_uskudar_pipeline.py

# Step 3: Launch interactive simulation
cd output/uskudar/opendrive_scenario
sumo-gui uskudar_simulation.sumocfg
```

### **Alternative: Use Existing Results**
```bash
# Launch our pre-built Üsküdar simulation
cd v2_advanced_method/output/uskudar/opendrive_scenario
sumo-gui uskudar_simulation.sumocfg
```

---

## 🏗️ Project Architecture

The system consists of two main versions representing the evolution from basic to advanced AV simulation capabilities. This two-version architecture demonstrates the progression from simple OSM data processing to professional autonomous vehicle simulation tools.

### **System Components**

1. **Data Processing Engine**: OSM data parsing, validation, and coordinate system conversion with support for Istanbul's geographic specifics.

2. **Conversion Pipeline**: Multi-stage conversion system supporting OSM → SUMO → OpenDRIVE format transformation with advanced error handling and intermediate format processing.

3. **Export Algorithms**: Professional-grade OpenDRIVE and OpenSCENARIO export systems specifically designed for AV simulation compatibility with industry-standard tools.

4. **Validation Framework**: Comprehensive network structure validation, geometry verification, connection analysis, and traffic signal validation ensuring data quality throughout the pipeline.

5. **Visualization System**: Multi-modal visualization supporting SUMO GUI integration, interactive web maps, network comparison tools, and professional error visualization.

### **Data Flow Architecture**

The system follows a structured data flow from raw OSM data to professional AV simulation formats:

```
OSM Data → Network Parser → SUMO Converter → OpenDRIVE Generator → AV Simulation Tools
    ↓           ↓               ↓                ↓                    ↓
Validation → Structure Check → Geometry Fix → Format Validation → Quality Report
```

### **Version Comparison**

| Aspect | Version 1 (Basic) | Version 2 (Advanced) |
|--------|-------------------|----------------------|
| **Purpose** | Foundation data creation | Professional AV simulation |
| **Output Formats** | OSM, Basic SUMO | OpenDRIVE, OpenSCENARIO, Advanced SUMO |
| **Traffic Generation** | None | Intelligent real edge ID extraction |
| **Visualization** | Basic SUMO GUI | Interactive simulation with moving vehicles |
| **Industry Integration** | Limited | Compatible with esmini, Unreal Engine, CARLA |
| **Algorithm Complexity** | Simple conversion | Advanced export algorithms |

---

## 📦 Installation & Setup

### **Prerequisites**

Ensure your development environment meets the following requirements for optimal performance:

- **Operating System**: macOS 10.15+, Ubuntu 18.04+, or Windows 10+
- **Python**: Version 3.8 or higher with pip package manager
- **Memory**: Minimum 8GB RAM (16GB recommended for large networks)
- **Storage**: At least 2GB free space for network data and outputs

### **1. Repository Setup**

```bash
# Clone the repository
git clone [repository-url]
cd SWE599

# Verify project structure
ls -la  # Should show v1_basic_method/ and v2_advanced_method/
```

### **2. Python Environment Configuration**

Creating an isolated Python environment ensures dependency compatibility and prevents conflicts with system packages:

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Upgrade pip to latest version
pip install --upgrade pip

# Install project dependencies
pip install -r requirements.txt
```

### **3. SUMO Installation**

SUMO (Simulation of Urban Mobility) is essential for traffic simulation and network conversion:

```bash
# macOS Installation
brew install sumo

# Ubuntu Installation
sudo add-apt-repository ppa:sumo/stable
sudo apt-get update
sudo apt-get install sumo sumo-tools sumo-doc

# Verify SUMO installation
sumo --version
netconvert --version
```

### **4. XQuartz Setup (macOS Only)**

XQuartz enables GUI applications to run on macOS, essential for SUMO visualization:

```bash
# Install XQuartz
brew install --cask xquartz

# Restart your computer after installation
# Then start XQuartz and set display
open -a XQuartz
export DISPLAY=:0

# Test XQuartz functionality
xeyes  # Should display animated eyes
```

### **5. Verification**

Confirm your setup is complete by running verification commands:

```bash
# Test Python environment
python --version  # Should show 3.8+

# Test SUMO integration
python -c "import sumolib; print('SUMO integration successful')"

# Test required packages
python -c "import osmnx, numpy, xml.etree.ElementTree; print('All packages available')"
```

---

## 🔄 Format Specifications

Understanding the three main road network formats is crucial for effective conversion and validation. Each format serves different purposes in the AV simulation pipeline.

### **Format Overview**

| Format | Extension | Purpose | Industry Use |
|--------|-----------|---------|--------------|
| **OpenStreetMap** | .osm | Real-world map data | Community mapping, navigation |
| **SUMO Network** | .net.xml | Traffic simulation | Academic research, urban planning |
| **OpenDRIVE** | .xodr | AV simulation | Automotive industry, AV development |

### **OpenStreetMap (OSM) Format**

OSM represents real-world geographic data using a node-way-relation model optimized for collaborative mapping:

- **Nodes**: Geographic points with latitude/longitude coordinates
- **Ways**: Ordered sequences of nodes representing linear features like roads
- **Relations**: Complex geographic relationships between nodes and ways
- **Tags**: Key-value pairs providing semantic information about geographic features

**Example OSM Road Element:**
```xml
<way id="123456789">
  <nd ref="1001"/>
  <nd ref="1002"/>
  <tag k="highway" v="primary"/>
  <tag k="name" v="Bağdat Caddesi"/>
  <tag k="lanes" v="4"/>
  <tag k="maxspeed" v="50"/>
  <tag k="oneway" v="no"/>
</way>
```

### **SUMO Network Format**

SUMO represents traffic networks using a graph-based model optimized for microscopic traffic simulation:

- **Edges**: Road segments with explicit lane definitions and traffic characteristics
- **Junctions**: Intersection points with detailed connection logic and traffic light phases
- **Lanes**: Individual driving lanes with specific attributes like speed limits and width
- **Traffic Lights**: Detailed signal logic with phase definitions and timing

**Example SUMO Edge Element:**
```xml
<edge id="edge123" from="junction1" to="junction2" priority="2" type="highway.primary">
  <lane id="edge123_0" index="0" speed="13.89" width="3.5" length="150.0"/>
  <lane id="edge123_1" index="1" speed="13.89" width="3.5" length="150.0"/>
</edge>
```

### **OpenDRIVE Format**

OpenDRIVE provides a standardized description of road networks designed specifically for automotive simulation applications:

- **Roads**: Detailed geometric descriptions with parametric representation of centerlines
- **Lane Sections**: Precise lane definitions with width functions and lateral positioning
- **Junctions**: Complex intersection descriptions with connection paths and priority rules
- **Signals**: Traffic control devices with precise positioning and logical relationships

**Example OpenDRIVE Road Element:**
```xml
<road name="Bağdat Caddesi" length="150.0" id="1" junction="-1">
  <planView>
    <geometry s="0.0" x="456789.0" y="4567890.0" hdg="0.0" length="150.0">
      <line/>
    </geometry>
  </planView>
  <lanes>
    <laneSection s="0.0">
      <right>
        <lane id="-1" type="driving" level="false">
          <width sOffset="0.0" a="3.5" b="0.0" c="0.0" d="0.0"/>
        </lane>
        <lane id="-2" type="driving" level="false">
          <width sOffset="0.0" a="3.5" b="0.0" c="0.0" d="0.0"/>
        </lane>
      </right>
    </laneSection>
  </lanes>
</road>
```

### **Conversion Rules and Mapping**

The conversion process follows specific rules to maintain data integrity across formats while optimizing for each format's strengths.

**OSM to SUMO Conversion:**
- Highway tags map to SUMO edge types with priority values
- Lane count information becomes explicit lane definitions
- Traffic signal nodes become SUMO traffic light logic
- Coordinate transformation from WGS84 to local projection

**SUMO to OpenDRIVE Conversion:**
- SUMO edges become OpenDRIVE roads with parametric geometry
- Lane definitions transform to OpenDRIVE lane sections with width functions
- Junction logic converts to OpenDRIVE connection paths
- Coordinate system alignment for automotive simulation tools

---

## 🎯 Version 1: Basic Method

Version 1 provides the foundational data creation and basic conversion capabilities. This primitive method establishes the core infrastructure required for advanced processing.

### **Objectives and Scope**

Version 1 focuses on creating reliable, foundational data from real-world sources. The primary objectives include establishing OSM data acquisition workflows, implementing basic format conversion, and creating validation mechanisms for data quality assurance.

### **Component Overview**

The basic method implements core functionality through modular components designed for simplicity and reliability:

- **OSM Fetcher**: Automated download and processing of OpenStreetMap data for specified geographic regions
- **Basic Converter**: Fundamental conversion algorithms supporting OSM to SUMO transformation
- **Data Validator**: Essential validation routines ensuring data integrity and format compliance
- **Utility Functions**: Supporting infrastructure for coordinate transformation and data processing

### **Execution Instructions**

```bash
# Navigate to Version 1 directory
cd v1_basic_method

# Execute the main pipeline
python fetch_and_convert.py

# Expected execution time: 2-5 minutes for Üsküdar district
# Output: OSM data (7.4 MB) and basic SUMO network (12+ MB)
```

### **Generated Outputs**

Version 1 produces foundational data files essential for advanced processing:

- **OSM Data File**: Raw geographic data for Üsküdar district (approximately 7.4 MB)
- **Basic SUMO Network**: Converted network suitable for traffic simulation (12+ MB)
- **Validation Reports**: Data quality assessments and conversion statistics
- **Processing Logs**: Detailed execution information for debugging and optimization

---

## 🚀 Version 2: Advanced Method

Version 2 implements professional-grade algorithms for autonomous vehicle simulation, building upon the foundation established in Version 1. This advanced method provides industry-standard export capabilities and sophisticated traffic modeling.

### **Advanced Capabilities**

Version 2 extends the basic foundation with cutting-edge algorithms designed for professional AV development workflows:

- **OpenDRIVE Export Engine**: Industry-standard road network format generation with precise geometric representation
- **OpenSCENARIO Generator**: Scenario-based testing framework for autonomous vehicle validation
- **Intelligent Traffic System**: Real-time traffic generation using authentic network topology
- **Professional Integration**: Compatibility with leading AV simulation platforms

### **Algorithm Innovations**

The advanced method incorporates several algorithmic innovations specifically developed for this project:

**Real Edge ID Extraction**: Advanced parsing algorithms that extract authentic road segment identifiers from converted networks, ensuring realistic traffic flow patterns.

**Geometric Precision Enhancement**: Sophisticated coordinate transformation and geometric refinement algorithms that maintain sub-meter accuracy required for AV simulation.

**Traffic Behavior Modeling**: Intelligent traffic generation algorithms that create realistic vehicle distributions and behavior patterns based on real-world traffic data.

### **Execution Instructions**

```bash
# Navigate to Version 2 directory
cd v2_advanced_method

# Execute the advanced pipeline
python advanced_uskudar_pipeline.py

# Alternative: Run individual components
python export_uskudar_simple.py      # OpenDRIVE/OpenSCENARIO export
python add_traffic_uskudar.py         # Advanced traffic generation
python test_export_simple.py          # Algorithm testing
```

### **Professional Outputs**

Version 2 generates production-ready files suitable for professional AV development:

- **OpenDRIVE Network**: Precision road network (16.3 MB) compatible with automotive simulation tools
- **OpenSCENARIO Files**: AV testing scenarios (6.8 KB) for scenario-based validation
- **Advanced SUMO Integration**: Enhanced traffic simulation with realistic vehicle behavior
- **Interactive Visualization**: Complete simulation environment with moving traffic

---

## 🧪 Testing & Validation

Comprehensive testing ensures data quality and system reliability throughout the conversion pipeline. The validation framework implements multiple verification layers designed to catch errors early and ensure professional-grade output quality.

### **Validation Methodology**

The testing framework employs a multi-layered approach addressing different aspects of data quality and system functionality:

**Structural Validation**: Verifies network topology, ensuring all roads are properly connected, junctions have valid configurations, and the overall network maintains logical consistency.

**Geometric Validation**: Confirms coordinate accuracy, road segment lengths, lane widths, and elevation data meet specified tolerances for automotive simulation requirements.

**Format Compliance**: Ensures output files conform to official specifications for OpenDRIVE, OpenSCENARIO, and SUMO formats, maintaining compatibility with industry-standard tools.

**Functional Testing**: Validates algorithm behavior under various input conditions, edge cases, and error scenarios to ensure robust operation.

### **Testing Commands**

```bash
# Run comprehensive test suite
python -m pytest tests/ -v

# Run specific validation tests
python -m pytest tests/test_network_validation.py

# Run format compliance tests
python -m pytest tests/test_format_compliance.py

# Run performance benchmarks
python -m pytest tests/test_performance.py --benchmark
```

### **Validation Reports**

The validation system generates detailed reports providing insights into data quality and conversion accuracy:

- **Network Statistics**: Comprehensive metrics including node counts, edge counts, traffic light distributions, and geometric characteristics
- **Quality Metrics**: Precision measurements, error rates, and compliance scores for professional assessment
- **Error Analysis**: Detailed identification and classification of validation failures with recommended corrections
- **Performance Metrics**: Execution time analysis, memory usage patterns, and optimization recommendations

---

## 📊 Visualization Methods

The project provides multiple visualization approaches designed for different use cases, from interactive exploration to professional presentation. Each method serves specific needs in the AV simulation development workflow.

### **SUMO GUI Integration**

SUMO's graphical interface provides the most comprehensive visualization capabilities for traffic simulation analysis:

```bash
# Basic network visualization
sumo-gui -n path/to/network.net.xml

# Interactive simulation with traffic
sumo-gui -c path/to/simulation.sumocfg

# Advanced visualization with custom settings
sumo-gui -n network.net.xml --gui-settings-file custom.settings.xml
```

**SUMO GUI Features**: Real-time traffic simulation, interactive network exploration, detailed vehicle tracking, traffic light phase visualization, and comprehensive data export capabilities.

### **Web-Based Interactive Maps**

Interactive HTML maps provide accessible visualization for stakeholders and documentation:

```bash
# Generate interactive map
python src/visualization/create_interactive_map.py input_network.osm output_map.html

# Advanced map with traffic data overlay
python src/visualization/create_traffic_map.py network.net.xml traffic_data.xml output.html
```

**Interactive Features**: Zoom and pan navigation, clickable network elements with detailed information, layer toggles for different data types, and export capabilities for presentations.

### **Professional Documentation Graphics**

Static visualizations suitable for reports, presentations, and technical documentation:

```bash
# Generate network overview plots
python src/visualization/create_network_plots.py network.net.xml output_directory/

# Create comparative visualizations
python src/visualization/compare_networks.py original.osm converted.net.xml comparison_report.html
```

---

## 🔧 Development Guidelines

Professional development practices ensure code quality, maintainability, and collaborative efficiency. These guidelines establish standards for contributing to the project and extending its capabilities.

### **Code Quality Standards**

All contributions must adhere to established coding standards designed to maintain professional-grade code quality:

**Python Style Compliance**: Follow PEP 8 guidelines with automated formatting using black and isort. Type hints are required for all function signatures and class definitions.

**Documentation Requirements**: Comprehensive docstrings using Google or NumPy style, inline comments for complex algorithms, and updated README files for new components.

**Testing Standards**: Unit tests with minimum 80% coverage, integration tests for component interactions, and performance benchmarks for optimization validation.

### **Development Workflow**

```bash
# Create development branch
git checkout -b feature/new-algorithm

# Install development dependencies
pip install -r requirements-dev.txt

# Run pre-commit hooks
pre-commit install
pre-commit run --all-files

# Execute test suite
python -m pytest tests/ --cov=src --cov-report=html

# Submit for review
git push origin feature/new-algorithm
```

### **Architecture Extension**

When adding new functionality, follow the established architectural patterns:

**Component Design**: New components should implement clear interfaces, maintain separation of concerns, and follow dependency injection patterns for testability.

**Error Handling**: Implement comprehensive error handling with appropriate logging levels, graceful degradation for non-critical failures, and detailed error messages for debugging.

**Configuration Management**: Use centralized configuration files, environment-specific settings, and validation for configuration parameters.

---

## 🔍 API Reference

The project provides comprehensive APIs for programmatic access to conversion and validation functionality. These APIs enable integration with external tools and custom workflow development.

### **Core Conversion APIs**

**NetworkConverter Class**: Primary interface for format conversion operations supporting OSM, SUMO, and OpenDRIVE formats with extensive configuration options.

```python
from v2_advanced_method.exporters.opendrive_exporter.exporter import OpenDRIVEExporter

# Initialize exporter with configuration
exporter = OpenDRIVEExporter()
exporter.set_network_offset(-668686.91, -4539963.74)  # UTM Zone 35N for Istanbul

# Add network elements
exporter.add_node(node_id="123", x=29.0448, y=41.0370)
exporter.add_edge(edge_id="456", from_node="123", to_node="124")

# Export to file
exporter.export("output/network.xodr")
```

**OpenSCENARIO APIs**: Scenario generation and vehicle behavior definition for autonomous vehicle testing:

```python
from v2_advanced_method.exporters.openscenario_exporter.exporter import OpenSCENARIOExporter

# Create scenario exporter
scenario = OpenSCENARIOExporter()

# Define autonomous vehicle
scenario.add_vehicle(
    vehicle_id="ego_vehicle",
    vehicle_type="av_sedan",
    initial_position=(29.0448, 41.0370),
    initial_speed=30.0
)

# Export scenario
scenario.export("output/av_scenario.xosc")
```

### **Validation APIs**

**Network Validation**: Comprehensive validation framework for ensuring data quality and format compliance:

```python
from v2_advanced_method.validation.network_validator import NetworkValidator

# Initialize validator
validator = NetworkValidator(network_file="path/to/network.net.xml")

# Run validation suite
structure_errors = validator.validate_structure()
geometry_errors = validator.validate_geometry()
connection_errors = validator.validate_connections()

# Generate validation report
report = validator.generate_report()
```

### **Utility Functions**

**Coordinate Transformation**: Precise coordinate system conversion supporting multiple projections and datum transformations:

```python
from v1_basic_method.utils.coordinate_converter import CoordinateConverter

# Initialize converter for Istanbul region
converter = CoordinateConverter(source_crs="EPSG:4326", target_crs="EPSG:32635")

# Transform coordinates
utm_x, utm_y = converter.transform(longitude=29.0448, latitude=41.0370)
```

---

## 🛠️ Troubleshooting

Common issues and their solutions are documented here to assist with rapid problem resolution and maintain development productivity.

### **Installation Issues**

**SUMO Installation Problems**: Verify SUMO installation with `sumo --version`. On macOS, ensure Homebrew is updated. On Ubuntu, verify the PPA repository is correctly added. Windows users should check PATH environment variables.

**Python Dependencies**: Use `pip list` to verify installed packages. Create a fresh virtual environment if conflicts occur. For macOS users with M1/M2 chips, ensure compatibility versions are installed.

**XQuartz Configuration (macOS)**: Restart computer after XQuartz installation. Verify display setting with `echo $DISPLAY`. If GUI applications fail, try `export DISPLAY=:0` and restart the application.

### **Conversion Errors**

**Network Topology Issues**: Large networks may have disconnected components. Use the network validation tools to identify and resolve topology problems before conversion.

**Coordinate System Problems**: Ensure proper coordinate reference system (CRS) configuration. Istanbul data requires UTM Zone 35N (EPSG:32635) for optimal precision.

**Memory Limitations**: Large networks may exceed available memory. Consider processing smaller geographic regions or using the provided network partitioning utilities.

### **Performance Optimization**

**Slow Conversion Times**: Monitor system resources during conversion. Consider adjusting chunk sizes for large datasets or using parallel processing options where available.

**Large File Sizes**: OpenDRIVE files can become very large for complex networks. Use the geometric simplification options to reduce file size while maintaining accuracy.

### **Visualization Problems**

**SUMO GUI Issues**: Ensure XQuartz is running on macOS. Verify network file integrity before attempting visualization. Check SUMO GUI settings for performance optimization with large networks.

**Interactive Map Loading**: Large HTML maps may load slowly in browsers. Consider using the network simplification options or viewing smaller geographic regions.

### **Getting Help**

**Error Log Analysis**: Enable debug logging for detailed error information. Most errors include suggestions for resolution in the log output.

**Community Support**: Check the project issues tracker for similar problems and solutions. Provide detailed error logs when reporting new issues.

**Documentation Updates**: If you discover missing information or errors in this documentation, please contribute improvements through the standard development workflow.

---

## 📞 Support and Resources

For additional assistance and extended learning resources:

- **Project Repository**: [GitHub Issues Tracker]
- **SUMO Documentation**: [https://sumo.dlr.de/docs/]
- **OpenDRIVE Specification**: [https://www.asam.net/standards/detail/opendrive/]
- **OpenSCENARIO Standard**: [https://www.asam.net/standards/detail/openscenario/]

---

**🏛️ Built for SWE599 - Advanced Software Development Project**  
**📍 Geographic Focus: Üsküdar, Istanbul, Turkey**  
**🚀 Status: Production-ready AV simulation environment** 