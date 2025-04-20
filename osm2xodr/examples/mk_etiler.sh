#!/usr/bin/env bash -e

osmium getid --overwrite -r -t turkey-latest.osm.pbf r9340882 r9340899 r9343698 r9343740 -o etiler.relation.osm
osmium extract --overwrite -p etiler.relation.osm turkey-latest.osm.pbf -o etiler.osm.pbf --clean timestamp
osmium tags-filter --overwrite etiler.osm.pbf w/highway=primary -o etiler-roads.osm.pbf
osmium cat --overwrite etiler-roads.osm.pbf -o etiler.osm

# Convert to the OpenDrive format
netconvert --osm.elevation 1 --osm-files etiler.osm --opendrive-output etiler.xodr
