#!/usr/bin/env bash -e

osmium getid --overwrite -r -t turkey-latest.osm.pbf r365987 -o 559c.relation.osm
osmium extract --overwrite --strategy smart --polygon 559c.osm turkey-latest.osm.pbf -o 559c.osm --clean timestamp

# Convert to the OpenDrive format
netconvert --osm.elevation true --osm-files 559c.osm --opendrive-output 559c.xodr
