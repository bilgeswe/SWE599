#!/usr/bin/env bash -e

osmium getid --overwrite -r -t turkey-latest.osm.pbf r223474 -o istanbul.relation.osm
osmium extract --overwrite -p istanbul.relation.osm turkey-latest.osm.pbf -o istanbul.osm.pbf --clean timestamp
osmium tags-filter --overwrite istanbul.osm.pbf w/highway=motorway -o istanbul-roads.osm.pbf
osmium cat --overwrite istanbul-roads.osm.pbf -o istanbul.osm

# Convert to the OpenDrive format
netconvert --osm.elevation 1 --osm-files istanbul.osm --opendrive-output istanbul.xodr
