
<img width="1203" alt="uskudar_network_net_xml" src="https://github.com/user-attachments/assets/f57eabb1-2d5e-446e-a808-8da666d8285b" />

# 🏙️ AV Simulation Project

> **Professional OpenDRIVE/OpenSCENARIO export system for Istanbul's Üsküdar district, evolved from basic OSM data to advanced AV simulation pipeline.**

## 🎯 Project Overview

This project demonstrates the evolution from **basic OSM data processing** to **professional autonomous vehicle simulation** using real-world data from Üsküdar, Istanbul.

### 📊 **Final Achievement:**
- **🗺️ 9,421 nodes** and **24,157 road edges** covering Üsküdar district
- **🚦 42 traffic lights** with realistic behavior
- **📍 Geographic coverage:** 29.006°-29.092°E, 40.992°-41.078°N
- **🔧 Professional formats:** OpenDRIVE (16.3 MB) + OpenSCENARIO (6.8 KB)
- **🎮 Interactive simulation:** Ready for SUMO-GUI with moving traffic

## 🏗️ Two-Version Architecture

### **Version 1: Basic Method** (`v1_basic_method/`)
The foundation - basic OSM data fetching and simple SUMO conversion.

   ```bash
🏗️ PRIMITIVE METHOD
├── Fetch OSM data for Üsküdar → 7.4 MB .osm file
├── Convert to basic SUMO → 12.3 MB .net.xml
└── Foundation for advanced processing
```

**Run:** `cd v1_basic_method && python fetch_and_convert.py`

### **Version 2: Advanced Method** (`v2_advanced_method/`)
Professional AV simulation with advanced algorithms and export systems.

```bash
🚀 ADVANCED METHOD
├── OpenDRIVE Export Algorithm → 16.3 MB .xodr
├── OpenSCENARIO Export → 6.8 KB .xosc  
├── Intelligent Traffic Generation → Real edge IDs
├── Professional SUMO Integration → Interactive simulation
└── Ready for AV development tools
```

**Run:** `cd v2_advanced_method && python advanced_uskudar_pipeline.py`

## 🚀 Quick Start

### **Option 1: Full Pipeline (Recommended)**
```bash
# Step 1: Create foundation data
cd v1_basic_method
python fetch_and_convert.py

# Step 2: Build advanced simulation
cd ../v2_advanced_method  
python advanced_uskudar_pipeline.py

# Step 3: Launch interactive simulation
cd output/uskudar/advanced_simulation
sumo-gui uskudar_simulation.sumocfg
```

### **Option 2: Use Existing Results**
```bash
# Launch our pre-built Üsküdar simulation
cd v2_advanced_method/output/uskudar/opendrive_scenario
sumo-gui uskudar_simulation.sumocfg
```

## 📁 Repository Structure

```
SWE599/
├── README.md                     # This file
├── requirements.txt              # Python dependencies
├── v1_basic_method/              # 🏗️ VERSION 1: Foundation
│   ├── README.md
│   ├── fetch_and_convert.py      # Main script
│   ├── data/                     # OSM data (7.4 MB)
│   ├── osm_fetcher/              # Basic OSM tools
│   ├── converter/                # Basic conversion
│   └── utils/                    # Utility functions
└── v2_advanced_method/           # 🚀 VERSION 2: Advanced
    ├── README.md
    ├── advanced_uskudar_pipeline.py  # Main advanced script
    ├── add_traffic_uskudar.py     # Traffic generation algorithm
    ├── export_uskudar_simple.py   # Üsküdar-specific export
    ├── test_export_simple.py      # Testing framework
    ├── exporters/                 # Advanced export algorithms
    │   ├── opendrive_exporter/    # OpenDRIVE export system
    │   └── openscenario_exporter/ # OpenSCENARIO export system
    ├── av_algorithms/             # AV-specific algorithms
    ├── examples/                  # Advanced examples
    ├── validation/                # Validation tools
    ├── visualization/             # Advanced visualization
    ├── cli/                      # Command-line interface
    └── output/                   # 🎯 GENERATED FILES
        └── uskudar/
            └── opendrive_scenario/    # Working simulation
                ├── uskudar_network.xodr       # 16.3 MB OpenDRIVE
                ├── uskudar_av_scenario.xosc   # 6.8 KB OpenSCENARIO
                ├── uskudar_network.net.xml    # 15.9 MB SUMO network
                ├── uskudar_routes.rou.xml     # Traffic routes
                ├── uskudar_simulation.sumocfg # Complete simulation
                └── export_summary.json       # Statistics
```

## 🔧 Key Technologies & Algorithms

### **Version 1 Technologies:**
- **OSMnx** - OpenStreetMap data fetching
- **SUMO netconvert** - Basic network conversion
- **XML processing** - Data parsing

### **Version 2 Advanced Algorithms:**
- **🛣️ OpenDRIVE Exporter** - Professional road network format
- **🎬 OpenSCENARIO Exporter** - AV scenario testing format  
- **🚦 Intelligent Traffic Generator** - Real edge ID extraction
- **🎮 SUMO Integration** - Complete simulation pipeline

## 💡 Real-World Applications

### **🚗 Autonomous Vehicle Development**
- Test AV algorithms in realistic Istanbul traffic
- Use OpenSCENARIO for scenario-based validation
- Professional-grade simulation environment

### **🏙️ Urban Planning & Traffic Research**
- Analyze traffic patterns in Üsküdar district
- Test traffic light optimization algorithms
- Study real-world urban mobility

### **🔬 Academic Research**
- Ready-to-use Istanbul traffic simulation
- Professional export formats for research tools
- Complete pipeline for similar cities

## 🌍 Geographic Coverage

- **🏛️ District:** Üsküdar, Istanbul, Turkey
- **📍 Coordinates:** 29.006°-29.092°E, 40.992°-41.078°N  
- **🗺️ Area:** Real urban district with complex road network
- **🚦 Infrastructure:** 42 traffic lights, major intersections

## 🔗 Integration with Professional Tools

The generated files are compatible with:

- **🎮 esmini** - Load `.xodr` and `.xosc` for 3D simulation
- **🎯 Unreal Engine** - Import OpenDRIVE for photorealistic AV simulation
- **🚗 CARLA** - Use as custom map for AV research  
- **🏭 IPG CarMaker** - Professional AV simulation platform
- **📊 SUMO** - Traffic flow analysis and optimization

## 📦 Installation & Dependencies

```bash
# Clone repository
git clone [repository-url]
cd SWE599

# Install Python dependencies
pip install -r requirements.txt

# Install SUMO (macOS)
brew install sumo

# Verify installation
sumo-gui --version
```

## 🎉 Project Success Metrics

✅ **Data Processing:** 7.4 MB OSM → 16.3 MB OpenDRIVE  
✅ **Network Scale:** 9,421 nodes, 24,157 edges  
✅ **Professional Formats:** OpenDRIVE + OpenSCENARIO export  
✅ **Interactive Simulation:** Working SUMO-GUI with traffic  
✅ **Real-World Data:** Actual Istanbul geography  
✅ **Algorithm Development:** Custom export and traffic generation  
✅ **Professional Integration:** Ready for AV development tools  

---

**📧 Contact:** Built for SWE599 - Advanced software development project  
**🏛️ Location:** Üsküdar, Istanbul, Turkey  
**🚀 Status:** Production-ready AV simulation environment


