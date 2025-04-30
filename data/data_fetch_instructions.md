# Data Fetching Instructions

This document provides instructions for fetching and processing road network data.

## Fetching Road Network Data

The project provides two methods for downloading road network data:

### 1. Using Place Name (Recommended)

The simplest way to download road network data is by using a place name:

```bash
python src/examples/download_network.py "Place Name, Country"
```

For example, to download the road network for Odunpazarı, Eskişehir:
```bash
python src/examples/download_network.py "Odunpazarı, Eskişehir, Turkey"
```

### 2. Using Bounding Box Coordinates

Alternatively, you can specify a bounding box to download data for a specific area:

```bash
python src/examples/download_by_coordinates.py min_lat max_lat min_lon max_lon
```

For example:
```bash
python src/examples/download_by_coordinates.py 39.7 39.8 30.4 30.6
```

## Data Processing

The downloaded data will be saved in the following formats:
- OSM XML format (`.osm`)
- SUMO network format (`.net.xml`)
- OpenDRIVE format (`.xodr`)

The data processing pipeline includes:
1. Downloading OSM data
2. Converting to SUMO network format
3. Converting to OpenDRIVE format
4. Validating the generated files

## Requirements

- Python 3.8 or higher
- Required packages:
  - osmnx
  - networkx
  - lxml
  - numpy
  - matplotlib

## Notes

- The download process may take several minutes depending on the area size
- Progress feedback is provided during the download
- The generated files are saved in the `data` directory
- Validation tools are available to check the generated files 