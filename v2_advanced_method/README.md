# 🚀 Version 2: Advanced Üsküdar AV Simulation Pipeline

This is the **advanced method** that builds upon Version 1, featuring professional AV simulation algorithms and tools.

## 🎯 What This Version Adds

### **🔥 Major Improvements Over Version 1:**

1. **🛣️ OpenDRIVE Export Algorithm**
   - Professional road network format for AV simulation
   - Compatible with industry-standard tools (esmini, Unreal Engine, etc.)
   - Creates: `uskudar_network.xodr` (16.3 MB)

2. **🎬 OpenSCENARIO Export Algorithm**
   - Scenario-based AV testing format
   - Defines vehicle behaviors and test scenarios
   - Creates: `uskudar_av_scenario.xosc` (6.8 KB)

3. **🚦 Intelligent Traffic Generation**
   - Real edge ID extraction from network
   - Multiple vehicle types and realistic behavior
   - Creates: `uskudar_routes.rou.xml`, `uskudar_simulation.sumocfg`

4. **🎮 Complete SUMO Integration**
   - Professional-grade traffic simulation
   - Interactive visualization with moving vehicles
   - Ready for AV algorithm testing

## 🗂️ Folder Structure

```
v2_advanced_method/
├── README.md                           # This file
├── advanced_uskudar_pipeline.py        # Main pipeline script
├── add_traffic_uskudar.py              # Advanced traffic generation
├── export_uskudar_simple.py            # Üsküdar-specific export
├── test_export_simple.py               # Testing framework
├── exporters/                          # Advanced export algorithms
│   ├── opendrive_exporter/             # OpenDRIVE export module
│   │   ├── exporter.py
│   │   ├── road_geometry.py
│   │   └── junction_builder.py
│   └── openscenario_exporter/          # OpenSCENARIO export module
│       ├── exporter.py
│       ├── vehicle_catalog.py
│       └── scenario_builder.py
├── av_algorithms/                      # AV-specific algorithms
├── examples/                           # Advanced examples
├── validation/                         # Validation tools
├── visualization/                      # Advanced visualization
├── cli/                               # Command-line interface
└── output/                            # Generated files
    └── uskudar/
        ├── opendrive_scenario/         # From our successful run
        │   ├── uskudar_network.xodr    # 16.3 MB OpenDRIVE
        │   ├── uskudar_av_scenario.xosc # 6.8 KB OpenSCENARIO  
        │   ├── uskudar_network.net.xml  # 15.9 MB SUMO network
        │   ├── uskudar_routes.rou.xml   # Traffic routes
        │   ├── uskudar_simulation.sumocfg # Simulation config
        │   └── export_summary.json     # Processing statistics
        └── advanced_simulation/        # New advanced output
```

## 🚀 How to Run

### **Option 1: Full Advanced Pipeline**
```bash
cd v2_advanced_method
python advanced_uskudar_pipeline.py
```

### **Option 2: Individual Components**
```bash
# Export Üsküdar to OpenDRIVE/OpenSCENARIO
python export_uskudar_simple.py

# Generate advanced traffic
python add_traffic_uskudar.py

# Test with mock data
python test_export_simple.py
```

### **Option 3: Launch Existing Simulation**
```bash
cd output/uskudar/opendrive_scenario
sumo-gui uskudar_simulation.sumocfg
```

## 📊 Expected Output

```
🚀 VERSION 2: ADVANCED ÜSKÜDAR AV SIMULATION PIPELINE
====================================================================

📊 Loading Üsküdar network data from Version 1...
✅ Found OSM data: ../v1_basic_method/data/osm/üsküdar__istanbul__turkey.osm
📈 Network stats: 9421 nodes, 24157 edges, 42 traffic lights

🛣️ Step 1: Exporting to OpenDRIVE format...
✅ OpenDRIVE exported: output/uskudar/advanced_simulation/uskudar_network.xodr (16.3 MB)

🎬 Step 2: Creating OpenSCENARIO for AV testing...
✅ OpenSCENARIO exported: output/uskudar/advanced_simulation/uskudar_av_scenario.xosc (6.8 KB)

🚗 Step 3: Converting to advanced SUMO format...
✅ Advanced SUMO network: output/uskudar/advanced_simulation/uskudar_network.net.xml (15.9 MB)

🚦 Step 4: Generating advanced traffic with real edge IDs...
✅ Traffic routes: output/uskudar/advanced_simulation/uskudar_routes.rou.xml
✅ Simulation config: output/uskudar/advanced_simulation/uskudar_simulation.sumocfg

🎉 VERSION 2 ADVANCED PIPELINE COMPLETE!
🚀 Professional AV simulation environment ready!
💡 Launch with: sumo-gui output/uskudar/advanced_simulation/uskudar_simulation.sumocfg
```

## 🔧 Key Algorithms Developed

### **1. OpenDRIVE Exporter** (`exporters/opendrive_exporter/`)
- Converts OSM/SUMO data to OpenDRIVE XML format
- Handles road geometry, junctions, traffic lights
- Uses UTM coordinate system for precision

### **2. OpenSCENARIO Exporter** (`exporters/openscenario_exporter/`)
- Creates AV test scenarios
- Defines vehicle catalogs and behaviors
- Generates realistic traffic interactions

### **3. Advanced Traffic Generator** (`add_traffic_uskudar.py`)
- Extracts real edge IDs from SUMO network
- Generates realistic vehicle routes
- Creates complete simulation configuration

## 💡 Real-World Applications

- **🚗 Autonomous Vehicle Testing**: Use OpenSCENARIO for scenario-based testing
- **🏙️ Urban Planning**: Visualize traffic flow in Üsküdar district
- **🚦 Traffic Optimization**: Test traffic light algorithms
- **📊 Research**: Study traffic patterns in real Istanbul geography

## 🔗 Integration with Professional Tools

- **esmini**: Load `.xodr` and `.xosc` files for 3D simulation
- **Unreal Engine**: Import OpenDRIVE for photorealistic AV simulation  
- **CARLA**: Use as custom map for AV research
- **IPG CarMaker**: Professional AV simulation platform

## 📦 Dependencies

- All Version 1 dependencies, plus:
- `numpy` - Numerical computations
- `scipy` - Scientific computing
- Custom export algorithms (included) 