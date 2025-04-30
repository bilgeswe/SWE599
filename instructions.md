# Instructions for Cleaning and Recreating Visualizations

## 1. Cleaning Up Old Files

First, we need to clean up the existing files. Run these commands in your terminal:

```bash
# Remove old network files
rm -rf data/networks/*.osm

# Remove old visualization files
rm -rf data/visualizations/*.html
rm -rf data/visualizations/*.png

# Remove old plot files
rm -rf data/plots/*.html
rm -rf data/plots/*.png
```

## 2. Downloading Fresh Network Data

Download the road network data for each area:

```bash
# Download Kadıköy network
python src/osm_fetcher/download_network.py "Kadıköy, Istanbul, Turkey"

# Download Levent network
python src/osm_fetcher/download_network.py "Levent, Istanbul, Turkey"

# Download Odunpazarı network
python src/osm_fetcher/download_network.py "Odunpazarı, Eskişehir, Turkey"
```

## 3. Creating Interactive Visualizations

Generate interactive visualizations for each network:

```bash
# Create interactive visualization for Kadıköy
python src/visualization/visualize_with_folium.py data/networks/kadıköy.osm

# Create interactive visualization for Levent
python src/visualization/visualize_with_folium.py data/networks/levent.osm

# Create interactive visualization for Odunpazarı
python src/visualization/visualize_with_folium.py data/networks/odunpazarı.osm
```

## 4. Creating Static Visualizations

Generate static visualizations for each network:

```bash
# Create static visualization for Kadıköy
python src/visualization/visualize_network.py data/networks/kadıköy.osm

# Create static visualization for Levent
python src/visualization/visualize_network.py data/networks/levent.osm

# Create static visualization for Odunpazarı
python src/visualization/visualize_network.py data/networks/odunpazarı.osm
```

## 5. Verifying Results

After running all commands, you should have:

1. Network files in `data/networks/`:
   - `kadıköy.osm`
   - `levent.osm`
   - `odunpazarı.osm`

2. Interactive visualizations in `data/visualizations/`:
   - `kadıköy_interactive.html`
   - `levent_interactive.html`
   - `odunpazarı_interactive.html`

3. Static visualizations in `data/plots/`:
   - `kadıköy_network.png`
   - `levent_network.png`
   - `odunpazarı_network.png`

## Notes

- Make sure you're in your project's root directory before running these commands
- Ensure your Python virtual environment is activated
- All paths are relative to the project root directory
- The process might take a few minutes, especially the network downloads
- Interactive visualizations can be opened in any modern web browser 