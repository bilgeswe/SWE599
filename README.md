# OSM to OpenDRIVE Converter for AV Testing

This project focuses on converting real-world OpenStreetMap (OSM) data into OpenDRIVE map format using Python, SUMO, and custom tooling — with the goal of enabling autonomous vehicle (AV) testing without a simulation environment.

## 📌 Project Goals

- Use OpenStreetMap (OSM) API to gather real-world road data
- Convert OSM data to SUMO Net using netconvert
- Write a Python script to convert SUMO Net to OpenDRIVE format
- Develop basic AV algorithms to test on the OpenDRIVE map
- Focus on map-based simulation structure and testing
- Account for missing elevation data in OSM

## 📅 Timeline & Phases

### ✅ Phase 1: Environment Setup & Exploration
**Objectives:**
- Set up development environment
- Explore OSM, SUMO, and OpenDRIVE formats

**Tasks:**
- [ ] Install Python & required libraries: osmnx, requests, xml, etc.
- [ ] Install SUMO and verify netconvert tool
- [ ] Review .osm (XML), SUMO .net.xml, and OpenDRIVE .xodr formats

### 🌐 Phase 2: OSM Data Collection via API
**Objectives:**
- Use Overpass API or osmnx to scrape road network data

**Tasks:**
- [ ] Select region of interest (city or custom bounding box)
- [ ] Retrieve and save .osm road data
- [ ] Handle missing elevation (optional: consider SRTM/DEM sources)

### 🔁 Phase 3: Convert OSM → SUMO Net → OpenDRIVE
**Objectives:**
- Build conversion pipeline from real-world data to OpenDRIVE format

**Tasks:**
- [ ] Use SUMO's netconvert to convert .osm → .net.xml
- [ ] Explore existing tools to convert SUMO Net → OpenDRIVE
- [ ] Write custom Python script to parse SUMO XML and build .xodr
- [ ] Validate resulting OpenDRIVE file

### 🤖 Phase 4: AV Algorithm Development
**Objectives:**
- Simulate AV logic on OpenDRIVE map structure

**Tasks:**
- [ ] Design algorithms (lane following, routing, stoplight behavior)
- [ ] Apply logic on OpenDRIVE map data
- [ ] Output simulated behavior (paths, decisions, logs)

### 📘 Phase 5: Documentation & Final Report
**Objectives:**
- Prepare full documentation and final report

**Tasks:**
- [ ] Complete technical documentation
- [ ] Write final report
- [ ] Create visualizations and demos
- [ ] Present findings

## ⚙️ Tools and Libraries

- OpenStreetMap API / Overpass API
- osmnx – OSM data extraction with Python
- SUMO + netconvert – Create traffic networks
- Python – Scripting and conversion logic
- OpenDRIVE – Standardized road format
- (Optional) DEM / SRTM tools – Elevation data

## 📂 Repository Structure

```
.
├── data/
│   ├── osm/          # Raw OpenStreetMap data
│   ├── sumo/         # SUMO network files
│   └── opendrive/    # Converted OpenDRIVE files
├── src/
│   ├── osm_fetcher/  # OSM data collection scripts
│   ├── converter/    # Conversion pipeline
│   └── av_logic/     # AV testing algorithms
├── tests/            # Unit tests
├── docs/             # Documentation
├── requirements.txt  # Python dependencies
└── README.md        # Project documentation
```

## 🚀 Getting Started

Instructions for setting up the development environment will be added soon.

## 🚌 43R Bus Route Details

The project focuses on Istanbul's 43R bus route as a test case. This route was chosen because:
- It represents a real-world public transport route
- Contains various road types and intersections
- Includes both urban and suburban sections
- Has well-documented stops and schedule data

The bounding box coordinates for the 43R route area are:
- North: 41.0697
- South: 41.0297
- East: 29.0324
- West: 28.9724


