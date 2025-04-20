#!/usr/bin/env bash -e

osmium getid --overwrite -o besiktas.relation.osm turkey-latest.osm.pbf r1765893 
osmium tags-filter --overwrite -o besiktas.boundary.osm besiktas.relation.osm r/type=multipolygon,boundary
osmium cat --overwrite -o 43r.enclosed.osm besiktas.boundary.osm 43r.relation.osm

osmium getid --overwrite -r -t turkey-latest.osm.pbf r365969 -o 43r.relation.osm
osmium extract --overwrite -s smart -p 43r.enclosed.osm turkey-latest.osm.pbf -o 43r.osm --clean timestamp

# Convert to the OpenDrive format
netconvert --osm.elevation 1 --osm-files 43r.osm --opendrive-output 43r.xodr
