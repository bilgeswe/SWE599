#!/usr/bin/env bash -e

osmium getid --overwrite -r -t turkey-latest.osm.pbf r9340882 -o levent.relation.osm 
osmium extract --overwrite --strategy smart --polygon levent.relation.osm turkey-latest.osm.pbf -o levent.osm.pbf --clean timestamp


# Extract the roads from the OpenStreetMap data
# See: https://docs.osmcode.org/osmium/latest/osmium-tags-filter.html#filter-expressions
#
osmium tags-filter --overwrite levent.osm.pbf w/highway=primary -o levent-roads.osm.pbf

# Convert to the textual OSM format
osmium cat --overwrite levent-roads.osm.pbf -o levent.osm

# Convert to the OpenDrive format
netconvert --osm.elevation true --osm-files levent.osm --opendrive-output levent.xodr
