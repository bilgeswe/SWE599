# 🏗️ Version 1: Basic OSM Data Fetching & Conversion

This is the **primitive/basic method** for creating the foundation of our Üsküdar AV simulation project.

## 📋 What This Version Does

### **Step 1: OSM Data Fetching**
- Downloads OpenStreetMap data for **Üsküdar, Istanbul**
- Creates: `data/osm/üsküdar__istanbul__turkey.osm` (7.4 MB)
- Contains raw road network data

### **Step 2: Basic SUMO Conversion** 
- Converts OSM to basic SUMO network format
- Creates: `data/sumo_basic/uskudar_basic.net.xml`
- Simple, unoptimized conversion

## 🗂️ Folder Structure

```
v1_basic_method/
├── README.md                    # This file
├── fetch_and_convert.py         # Main script
├── data/                        # Data directory
│   ├── osm/                     # Raw OSM data
│   │   └── üsküdar__istanbul__turkey.osm
│   └── sumo_basic/              # Basic SUMO files
│       └── uskudar_basic.net.xml
├── osm_fetcher/                 # OSM fetching module
├── converter/                   # Basic conversion tools
└── utils/                       # Utility functions
```

## 🚀 How to Run

```bash
cd v1_basic_method
python fetch_and_convert.py
```

## 📊 Expected Output

```
🏗️ VERSION 1: BASIC OSM DATA FETCHING & CONVERSION
================================================================

📍 Step 1: Fetching Üsküdar OSM Data...
✅ OSM data saved: data/osm/üsküdar__istanbul__turkey.osm
📊 File size: 7.4 MB

🔄 Step 2: Converting OSM to SUMO...
✅ SUMO network created: data/sumo_basic/uskudar_basic.net.xml
📊 SUMO file size: 12.3 MB

🎉 VERSION 1 COMPLETE!
```

## 🔗 Next Steps

After completing Version 1, proceed to **Version 2** for:
- Advanced OpenDRIVE/OpenSCENARIO export
- Intelligent traffic generation
- Professional AV simulation capabilities

## 📦 Dependencies

- `osmnx` - OpenStreetMap data fetching
- `SUMO` - Traffic simulation (netconvert tool)
- `xml.etree.ElementTree` - XML processing 