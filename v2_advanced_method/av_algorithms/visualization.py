"""Visualization module for AV simulation using HTML and PNG outputs."""

import os
import math
import json
from typing import List, Tuple, Dict
import folium
from folium import plugins
import branca.colormap as cm
from datetime import datetime
import numpy as np

from .av_controller import AVController, AVState
from .path_planner import Node, Edge
from .traffic_light_handler import TrafficLight, TrafficLightState

class AVVisualizer:
    """Visualizes AV simulation using HTML and PNG outputs."""
    
    def __init__(self, output_dir: str = "visualization/av_simulation"):
        """Initialize the visualizer.
        
        Args:
            output_dir: Directory to save visualization outputs
        """
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        
        # Create color maps
        self.speed_colormap = cm.LinearColormap(
            ['red', 'yellow', 'green'],
            vmin=0,
            vmax=50.0  # Maximum speed in m/s
        )
        
        self.accel_colormap = cm.LinearColormap(
            ['red', 'white', 'green'],
            vmin=-5.0,  # Maximum deceleration
            vmax=5.0    # Maximum acceleration
        )
        
        self.comfort_colormap = cm.LinearColormap(
            ['red', 'yellow', 'green'],
            vmin=0,     # Worst comfort
            vmax=1.0    # Best comfort
        )
        
        self.energy_colormap = cm.LinearColormap(
            ['green', 'yellow', 'red'],
            vmin=0,     # Most efficient
            vmax=100.0  # Least efficient (kWh/100km)
        )
        
        self.state_colors = {
            AVState.INITIALIZING: 'gray',
            AVState.PLANNING: 'blue',
            AVState.FOLLOWING_LANE: 'green',
            AVState.STOPPING: 'red',
            AVState.COMPLETED: 'purple',
            AVState.ERROR: 'black'
        }
        
        # Vehicle parameters for energy and comfort calculations
        self.vehicle_mass = 1500.0  # kg
        self.air_density = 1.225    # kg/m³
        self.drag_coefficient = 0.3
        self.frontal_area = 2.2     # m²
        self.rolling_resistance = 0.01
        self.gravity = 9.81         # m/s²
        
        # Create traffic light state timeline
        self.traffic_light_timeline = {}
        
    def create_network_map(self, nodes: List[Node], edges: List[Edge],
                          traffic_lights: List[TrafficLight]) -> folium.Map:
        """Create a map visualization of the road network.
        
        Args:
            nodes: List of road network nodes
            edges: List of road network edges
            traffic_lights: List of traffic lights
            
        Returns:
            Folium map object
        """
        # Determine if we have transformed coordinates
        has_latlon = hasattr(nodes[0], 'lat') and hasattr(nodes[0], 'lon') if nodes else False
        
        if has_latlon:
            # Use transformed coordinates
            center_lat = sum(n.lat for n in nodes) / len(nodes)
            center_lon = sum(n.lon for n in nodes) / len(nodes)
        else:
            # Fallback to original coordinates (might not work well for visualization)
            center_lon = sum(n.x for n in nodes) / len(nodes)
            center_lat = sum(n.y for n in nodes) / len(nodes)
        
        # Create map with no default tiles first
        m = folium.Map(location=[center_lat, center_lon], zoom_start=15, tiles=None)
        
        # Add multiple tile layers for reliability
        # 1. Carto Light (reliable and clean)
        carto_light = folium.TileLayer(
            tiles='https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png',
            attr='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>',
            name='Carto Light',
            overlay=False,
            control=True,
            max_zoom=20
        )
        carto_light.add_to(m)
        
        # 2. OpenStreetMap (fallback)
        osm = folium.TileLayer(
            tiles='https://tile.openstreetmap.org/{z}/{x}/{y}.png',
            attr='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
            name='OpenStreetMap',
            overlay=False,
            control=True,
            max_zoom=19
        )
        osm.add_to(m)
        
        # 3. Carto Dark (for night mode)
        carto_dark = folium.TileLayer(
            tiles='https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png',
            attr='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>',
            name='Carto Dark',
            overlay=False,
            control=True,
            max_zoom=20
        )
        carto_dark.add_to(m)
        
        # 4. Satellite view
        esri_satellite = folium.TileLayer(
            tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
            attr='Tiles &copy; Esri &mdash; Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community',
            name='Satellite',
            overlay=False,
            control=True,
            max_zoom=18
        )
        esri_satellite.add_to(m)
        
        # Add layer control
        folium.LayerControl().add_to(m)
        
        # Add road network
        for edge in edges:
            from_node = next(n for n in nodes if n.id == edge.from_node)
            to_node = next(n for n in nodes if n.id == edge.to_node)
            
            if has_latlon:
                # Use transformed coordinates for proper geographic display
                if hasattr(edge, 'shape_latlon') and edge.shape_latlon:
                    # Use transformed shape if available
                    locations = [[lat, lon] for lon, lat in edge.shape_latlon]
                else:
                    # Use transformed node coordinates
                    locations = [[from_node.lat, from_node.lon], [to_node.lat, to_node.lon]]
            else:
                # Fallback to original coordinates
                locations = [[from_node.y, from_node.x], [to_node.y, to_node.x]]
            
            # Create road line
            folium.PolyLine(
                locations=locations,
                color='black',
                weight=3,
                opacity=0.7,
                popup=f"Edge: {edge.id}<br>Speed Limit: {edge.speed_limit} m/s"
            ).add_to(m)
            
            # Add lane boundaries and markings if we have geographic coordinates
            if has_latlon and len(locations) >= 2:
                self._add_lane_markings(m, locations, edge)
                
        # Add traffic lights
        for light in traffic_lights:
            # Handle both enum objects and string values for state
            state_display = light.state.value if hasattr(light.state, 'value') else str(light.state)
            
            # Use appropriate coordinates for traffic lights
            if hasattr(light, 'position') and len(light.position) >= 2:
                # Traffic lights should already be in lat/lon format
                light_lat, light_lon = light.position[1], light.position[0]
            else:
                # Fallback position
                light_lat, light_lon = center_lat, center_lon
            
            folium.CircleMarker(
                location=[light_lat, light_lon],
                radius=5,
                color=self._get_light_color(light.state),
                fill=True,
                popup=f"Traffic Light: {light.id}<br>State: {state_display}"
            ).add_to(m)
                
        return m
        
    def _add_lane_markings(self, m: folium.Map, locations: list, edge: Edge) -> None:
        """Add lane markings to the map.
        
        Args:
            m: Folium map object
            locations: List of [lat, lon] coordinates
            edge: Edge object
        """
        if len(locations) < 2:
            return
            
        # Calculate perpendicular offset for lane boundaries
        start_lat, start_lon = locations[0]
        end_lat, end_lon = locations[-1]
        
        # Approximate distance and bearing
        import math
        dlat = end_lat - start_lat
        dlon = end_lon - start_lon
        bearing = math.atan2(dlon, dlat)
        
        # Lane width in degrees (approximate)
        lane_width_degrees = 0.00003  # Roughly 3.5 meters
        perp_bearing = bearing + math.pi / 2
        
        offset_lat = lane_width_degrees * math.cos(perp_bearing)
        offset_lon = lane_width_degrees * math.sin(perp_bearing)
        
        # Draw lane boundaries
        left_locations = [[lat + offset_lat, lon + offset_lon] for lat, lon in locations]
        right_locations = [[lat - offset_lat, lon - offset_lon] for lat, lon in locations]
        
        folium.PolyLine(
            locations=left_locations,
            color='gray',
            weight=1,
            opacity=0.3,
            dash_array='5, 5'
        ).add_to(m)
        
        folium.PolyLine(
            locations=right_locations,
            color='gray',
            weight=1,
            opacity=0.3,
            dash_array='5, 5'
        ).add_to(m)
        
        # Add lane IDs
        if edge.lanes:
            for i, lane_id in enumerate(edge.lanes):
                mid_idx = len(locations) // 2
                lane_lat = locations[mid_idx][0]
                lane_lon = locations[mid_idx][1]
                
                if i == 0:  # First lane
                    lane_lat += offset_lat * 0.5
                    lane_lon += offset_lon * 0.5
                else:  # Second lane
                    lane_lat -= offset_lat * 0.5
                    lane_lon -= offset_lon * 0.5
                
                folium.Popup(
                    f"Lane: {lane_id}",
                    max_width=100
                ).add_to(folium.CircleMarker(
                    location=[lane_lat, lane_lon],
                    radius=2,
                    color='blue',
                    fill=True
                ).add_to(m))
        
    def _get_light_color(self, state) -> str:
        """Get the color for a traffic light state.
        
        Args:
            state: Traffic light state (enum or string)
            
        Returns:
            Color string
        """
        # Handle both enum objects and string values
        state_str = state.value if hasattr(state, 'value') else str(state).upper()
        
        if state_str == 'RED':
            return 'red'
        elif state_str == 'YELLOW':
            return 'yellow'
        elif state_str == 'GREEN':
            return 'green'
        else:
            return 'gray'
            
    def _calculate_acceleration(self, positions: List[Tuple[float, float, float]], 
                              time_step: float) -> List[float]:
        """Calculate acceleration at each point in the trajectory.
        
        Args:
            positions: List of (x, y, heading) positions
            time_step: Time step between positions
            
        Returns:
            List of acceleration values
        """
        accelerations = []
        prev_speed = None
        
        for i in range(len(positions)-1):
            # Calculate speed between current and next position
            dx = positions[i+1][0] - positions[i][0]
            dy = positions[i+1][1] - positions[i][1]
            current_speed = math.sqrt(dx*dx + dy*dy) / time_step
            
            if prev_speed is not None:
                # Calculate acceleration
                accel = (current_speed - prev_speed) / time_step
                accelerations.append(accel)
            else:
                accelerations.append(0.0)
                
            prev_speed = current_speed
            
        # Add final acceleration (same as last calculated)
        if accelerations:
            accelerations.append(accelerations[-1])
        else:
            accelerations.append(0.0)
            
        return accelerations
        
    def _calculate_energy_consumption(self, positions: List[Tuple[float, float, float]], 
                                    time_step: float) -> Tuple[List[float], List[float]]:
        """Calculate energy consumption and efficiency.
        
        Args:
            positions: List of (x, y, heading) positions
            time_step: Time step between positions
            
        Returns:
            Tuple of (energy_consumption, efficiency) lists
        """
        energy_consumption = []
        efficiency = []
        prev_speed = 0
        
        for i in range(len(positions)-1):
            # Calculate speed and acceleration
            dx = positions[i+1][0] - positions[i][0]
            dy = positions[i+1][1] - positions[i][1]
            distance = math.sqrt(dx*dx + dy*dy)
            speed = distance / time_step
            accel = (speed - prev_speed) / time_step
            
            # Calculate forces
            drag_force = 0.5 * self.air_density * self.drag_coefficient * self.frontal_area * speed**2
            rolling_force = self.rolling_resistance * self.vehicle_mass * self.gravity
            acceleration_force = self.vehicle_mass * accel
            
            # Total force and power
            total_force = drag_force + rolling_force + acceleration_force
            power = total_force * speed
            
            # Energy consumption (kWh)
            energy = (power * time_step) / 3600000  # Convert to kWh
            energy_consumption.append(energy)
            
            # Energy efficiency (kWh/100km)
            if distance > 0:
                eff = (energy / distance) * 100000  # Convert to kWh/100km
            else:
                eff = 0
            efficiency.append(eff)
            
            prev_speed = speed
            
        # Add final values
        if energy_consumption:
            energy_consumption.append(energy_consumption[-1])
            efficiency.append(efficiency[-1])
        else:
            energy_consumption.append(0)
            efficiency.append(0)
            
        return energy_consumption, efficiency
        
    def _calculate_comfort_metrics(self, positions: List[Tuple[float, float, float]], 
                                 time_step: float) -> Tuple[List[float], List[float]]:
        """Calculate comfort metrics (jerk and lateral acceleration).
        
        Args:
            positions: List of (x, y, heading) positions
            time_step: Time step between positions
            
        Returns:
            Tuple of (comfort_scores, jerk_values) lists
        """
        # Calculate accelerations
        accelerations = self._calculate_acceleration(positions, time_step)
        
        # Calculate jerk (derivative of acceleration)
        jerk = []
        for i in range(len(accelerations)-1):
            j = (accelerations[i+1] - accelerations[i]) / time_step
            jerk.append(j)
        jerk.append(jerk[-1] if jerk else 0)
        
        # Calculate lateral acceleration
        lateral_accel = []
        for i in range(len(positions)-1):
            # Calculate heading change
            heading1 = positions[i][2]
            heading2 = positions[i+1][2]
            heading_change = (heading2 - heading1) / time_step
            
            # Calculate speed
            dx = positions[i+1][0] - positions[i][0]
            dy = positions[i+1][1] - positions[i][1]
            speed = math.sqrt(dx*dx + dy*dy) / time_step
            
            # Lateral acceleration = speed * heading_change
            lat_acc = speed * heading_change
            lateral_accel.append(lat_acc)
        lateral_accel.append(lateral_accel[-1] if lateral_accel else 0)
        
        # Calculate comfort score (0-1, higher is better)
        comfort_scores = []
        for i in range(len(positions)):
            # Normalize jerk and lateral acceleration
            norm_jerk = min(abs(jerk[i]) / 2.0, 1.0)  # 2.0 m/s³ is max comfortable jerk
            norm_lat_acc = min(abs(lateral_accel[i]) / 2.0, 1.0)  # 2.0 m/s² is max comfortable lateral acc
            
            # Combined comfort score
            comfort = 1.0 - (0.5 * norm_jerk + 0.5 * norm_lat_acc)
            comfort_scores.append(comfort)
            
        return comfort_scores, jerk
        
    def _create_speed_profile(self, positions: List[Tuple[float, float, float]], 
                            time_step: float) -> str:
        """Create HTML for speed profile visualization.
        
        Args:
            positions: List of (x, y, heading) positions
            time_step: Time step between positions
            
        Returns:
            HTML string for speed profile
        """
        # Calculate speeds
        speeds = []
        times = []
        for i in range(len(positions)-1):
            dx = positions[i+1][0] - positions[i][0]
            dy = positions[i+1][1] - positions[i][1]
            speed = math.sqrt(dx*dx + dy*dy) / time_step
            speeds.append(speed)
            times.append(i * time_step)
            
        # Create speed profile HTML
        html = """
        <div style="width: 300px; height: 200px;">
            <h4>Speed Profile</h4>
            <div id="speed_profile"></div>
        </div>
        <script>
            var speeds = """ + json.dumps(speeds) + """;
            var times = """ + json.dumps(times) + """;
            
            var trace = {
                x: times,
                y: speeds,
                type: 'scatter',
                mode: 'lines',
                name: 'Speed',
                line: {color: 'blue'}
            };
            
            var layout = {
                title: 'Vehicle Speed Over Time',
                xaxis: {title: 'Time (s)'},
                yaxis: {title: 'Speed (m/s)'}
            };
            
            Plotly.newPlot('speed_profile', [trace], layout);
        </script>
        """
        return html
        
    def _create_metrics_visualization(self, positions: List[Tuple[float, float, float]], 
                                    time_step: float) -> str:
        """Create HTML for energy and comfort metrics visualization.
        
        Args:
            positions: List of (x, y, heading) positions
            time_step: Time step between positions
            
        Returns:
            HTML string for metrics visualization
        """
        # Calculate metrics
        energy_consumption, efficiency = self._calculate_energy_consumption(positions, time_step)
        comfort_scores, jerk = self._calculate_comfort_metrics(positions, time_step)
        times = [i * time_step for i in range(len(positions))]
        
        # Create metrics visualization HTML
        html = """
        <div style="width: 600px; height: 400px;">
            <h4>Vehicle Performance Metrics</h4>
            <div id="metrics_plot"></div>
        </div>
        <script>
            var times = """ + json.dumps(times) + """;
            var efficiency = """ + json.dumps(efficiency) + """;
            var comfort = """ + json.dumps(comfort_scores) + """;
            
            var efficiency_trace = {
                x: times,
                y: efficiency,
                type: 'scatter',
                mode: 'lines',
                name: 'Energy Efficiency',
                line: {color: 'green'},
                yaxis: 'y1'
            };
            
            var comfort_trace = {
                x: times,
                y: comfort,
                type: 'scatter',
                mode: 'lines',
                name: 'Comfort Score',
                line: {color: 'blue'},
                yaxis: 'y2'
            };
            
            var layout = {
                title: 'Vehicle Performance Metrics',
                xaxis: {title: 'Time (s)'},
                yaxis: {
                    title: 'Energy Efficiency (kWh/100km)',
                    titlefont: {color: 'green'},
                    tickfont: {color: 'green'}
                },
                yaxis2: {
                    title: 'Comfort Score',
                    titlefont: {color: 'blue'},
                    tickfont: {color: 'blue'},
                    overlaying: 'y',
                    side: 'right'
                }
            };
            
            Plotly.newPlot('metrics_plot', [efficiency_trace, comfort_trace], layout);
        </script>
        """
        return html
        
    def _create_playback_controls(self, positions: List[Tuple[float, float, float]], 
                                time_step: float) -> str:
        """Create HTML for simulation playback controls.
        
        Args:
            positions: List of (x, y, heading) positions
            time_step: Time step between positions
            
        Returns:
            HTML string for playback controls
        """
        # Create a much smaller sample of position data to avoid HTML corruption
        # Sample every 50th position to keep the data manageable
        sample_interval = max(1, len(positions) // 100)  # At most 100 sample points
        sampled_positions = positions[::sample_interval]
        
        position_data = [
            {
                'x': x,
                'y': y,
                'heading': heading,
                'time': i * time_step * sample_interval
            }
            for i, (x, y, heading) in enumerate(sampled_positions)
        ]
        
        html = """
        <div style="position: fixed; bottom: 20px; left: 20px; z-index: 1000; background: white; padding: 10px; border-radius: 5px; box-shadow: 0 0 10px rgba(0,0,0,0.2);">
            <h4 style="margin: 0 0 10px 0;">Simulation Controls</h4>
            <div style="display: flex; align-items: center; gap: 10px;">
                <button onclick="playPause()" id="playPauseBtn">Play</button>
                <input type="range" id="timeSlider" min="0" max="100" value="0" style="width: 200px;">
                <span id="timeDisplay">0.0s</span>
                <select id="playbackSpeed" onchange="updatePlaybackSpeed()">
                    <option value="0.25">0.25x</option>
                    <option value="0.5">0.5x</option>
                    <option value="1" selected>1x</option>
                    <option value="2">2x</option>
                    <option value="4">4x</option>
                </select>
            </div>
            <div style="margin-top: 5px; font-size: 12px; color: #666;">
                <span>Keyboard Shortcuts:</span>
                <span style="margin-left: 10px;">Space: Play/Pause</span>
                <span style="margin-left: 10px;">←/→: Step Back/Forward</span>
                <span style="margin-left: 10px;">+/-: Speed Up/Down</span>
                <span style="margin-left: 10px;">R: Reset</span>
            </div>
        </div>
        
        <script>
            // Initialize variables with sampled position data
            var positions = """ + json.dumps(position_data) + """;
            var currentIndex = 0;
            var isPlaying = false;
            var playbackSpeed = 1.0;
            var vehicleMarker = null;
            var headingLine = null;
            var trajectoryLine = null;
            var trajectoryCoords = [];
            
            // Initialize map elements when document is ready
            document.addEventListener('DOMContentLoaded', function() {
                if (typeof map !== 'undefined') {
                    initializeMapElements();
                }
            });
            
            // Initialize map elements
            function initializeMapElements() {
                if (positions.length === 0) return;
                
                // Create vehicle marker
                vehicleMarker = L.circleMarker([positions[0].y, positions[0].x], {
                    radius: 8,
                    color: 'red',
                    fillColor: 'yellow',
                    fill: true,
                    weight: 2
                }).addTo(map);
                
                // Create heading line
                headingLine = L.polyline([], {
                    color: 'red',
                    weight: 3
                }).addTo(map);
                
                // Create trajectory line
                trajectoryLine = L.polyline([], {
                    color: 'blue',
                    weight: 2,
                    opacity: 0.6
                }).addTo(map);
                
                // Add keyboard event listeners
                document.addEventListener('keydown', handleKeyPress);
                
                // Initialize position
                updateVehiclePosition(0);
            }
            
            // Handle keyboard events
            function handleKeyPress(e) {
                // Ignore if typing in an input field
                if (e.target.tagName === 'INPUT' || e.target.tagName === 'SELECT') {
                    return;
                }
                
                switch(e.key) {
                    case ' ':  // Space
                        e.preventDefault();
                        playPause();
                        break;
                    case 'ArrowLeft':  // Left arrow
                        e.preventDefault();
                        stepBackward();
                        break;
                    case 'ArrowRight':  // Right arrow
                        e.preventDefault();
                        stepForward();
                        break;
                    case '+':
                    case '=':
                        e.preventDefault();
                        increaseSpeed();
                        break;
                    case '-':
                        e.preventDefault();
                        decreaseSpeed();
                        break;
                    case 'r':
                    case 'R':
                        e.preventDefault();
                        resetSimulation();
                        break;
                }
            }
            
            // Step backward
            function stepBackward() {
                if (isPlaying) {
                    playPause();
                }
                currentIndex = Math.max(0, currentIndex - 1);
                updateVehiclePosition(currentIndex);
            }
            
            // Step forward
            function stepForward() {
                if (isPlaying) {
                    playPause();
                }
                currentIndex = Math.min(positions.length - 1, currentIndex + 1);
                updateVehiclePosition(currentIndex);
            }
            
            // Increase playback speed
            function increaseSpeed() {
                var speedSelect = document.getElementById('playbackSpeed');
                var currentSpeed = parseFloat(speedSelect.value);
                var speeds = [0.25, 0.5, 1, 2, 4];
                var speedIndex = speeds.indexOf(currentSpeed);
                if (speedIndex < speeds.length - 1) {
                    speedSelect.value = speeds[speedIndex + 1];
                    updatePlaybackSpeed();
                }
            }
            
            // Decrease playback speed
            function decreaseSpeed() {
                var speedSelect = document.getElementById('playbackSpeed');
                var currentSpeed = parseFloat(speedSelect.value);
                var speeds = [0.25, 0.5, 1, 2, 4];
                var speedIndex = speeds.indexOf(currentSpeed);
                if (speedIndex > 0) {
                    speedSelect.value = speeds[speedIndex - 1];
                    updatePlaybackSpeed();
                }
            }
            
            // Reset simulation
            function resetSimulation() {
                if (isPlaying) {
                    playPause();
                }
                currentIndex = 0;
                trajectoryCoords = [];
                updateVehiclePosition(currentIndex);
            }
            
            // Update vehicle position and heading
            function updateVehiclePosition(index) {
                if (!positions || index >= positions.length || !vehicleMarker) return;
                
                var pos = positions[index];
                
                // Update vehicle marker position
                vehicleMarker.setLatLng([pos.y, pos.x]);
                
                // Update heading line
                var headingLength = 0.001;  // Adjusted for geographic coordinates
                var headingX = pos.x + headingLength * Math.cos(pos.heading);
                var headingY = pos.y + headingLength * Math.sin(pos.heading);
                headingLine.setLatLngs([[pos.y, pos.x], [headingY, headingX]]);
                
                // Update trajectory
                trajectoryCoords.push([pos.y, pos.x]);
                if (trajectoryCoords.length > 50) {  // Keep trajectory manageable
                    trajectoryCoords = trajectoryCoords.slice(-50);
                }
                trajectoryLine.setLatLngs(trajectoryCoords);
                
                // Update time display
                document.getElementById('timeDisplay').textContent = pos.time.toFixed(1) + 's';
                document.getElementById('timeSlider').value = (index / (positions.length - 1)) * 100;
            }
            
            // Play/pause function
            function playPause() {
                isPlaying = !isPlaying;
                document.getElementById('playPauseBtn').textContent = isPlaying ? 'Pause' : 'Play';
                
                if (isPlaying) {
                    playStep();
                }
            }
            
            // Play one step
            function playStep() {
                if (!isPlaying || !positions) return;
                
                currentIndex = (currentIndex + 1) % positions.length;
                updateVehiclePosition(currentIndex);
                
                setTimeout(playStep, 200 / playbackSpeed);  // Slower for better visualization
            }
            
            // Update playback speed
            function updatePlaybackSpeed() {
                playbackSpeed = parseFloat(document.getElementById('playbackSpeed').value);
            }
            
            // Handle slider change
            document.addEventListener('DOMContentLoaded', function() {
                var slider = document.getElementById('timeSlider');
                if (slider) {
                    slider.addEventListener('input', function(e) {
                        var index = Math.floor((e.target.value / 100) * (positions.length - 1));
                        currentIndex = Math.max(0, Math.min(index, positions.length - 1));
                        updateVehiclePosition(currentIndex);
                    });
                }
            });
        </script>
        """
        return html
        
    def create_simulation_visualization(self, controller: AVController,
                                     positions: List[Tuple[float, float, float]],
                                     nodes: List[Node], edges: List[Edge],
                                     traffic_lights: List[TrafficLight]) -> None:
        """Create visualization of the simulation.
        
        Args:
            controller: AV controller instance
            positions: List of (x, y, heading) positions during simulation
            nodes: List of road network nodes
            edges: List of road network edges
            traffic_lights: List of traffic lights
        """
        # Create base map
        m = self.create_network_map(nodes, edges, traffic_lights)
        
        # Calculate metrics
        accelerations = self._calculate_acceleration(positions, 0.1)
        energy_consumption, efficiency = self._calculate_energy_consumption(positions, 0.1)
        comfort_scores, jerk = self._calculate_comfort_metrics(positions, 0.1)
        
        # Add vehicle trajectory with comfort coloring
        trajectory_coords = [[y, x] for x, y, _ in positions]
        folium.PolyLine(
            locations=trajectory_coords,
            color='blue',
            weight=2,
            opacity=0.7,
            popup="Vehicle Trajectory"
        ).add_to(m)
        
        # Add comfort zones
        for i in range(len(positions)-1):
            if comfort_scores[i] < 0.8:  # Only show low comfort zones
                x1, y1, _ = positions[i]
                x2, y2, _ = positions[i+1]
                
                # Create gradient line for comfort
                folium.PolyLine(
                    locations=[[y1, x1], [y2, x2]],
                    color=self.comfort_colormap(comfort_scores[i]),
                    weight=4,
                    opacity=0.6,
                    popup=f"Comfort Score: {comfort_scores[i]:.2f}<br>Jerk: {jerk[i]:.2f} m/s³"
                ).add_to(m)
        
        # Add energy efficiency zones
        for i in range(len(positions)-1):
            if efficiency[i] > 20.0:  # Only show high energy consumption zones
                x1, y1, _ = positions[i]
                x2, y2, _ = positions[i+1]
                
                # Create gradient line for energy efficiency
                folium.PolyLine(
                    locations=[[y1, x1], [y2, x2]],
                    color=self.energy_colormap(efficiency[i]),
                    weight=4,
                    opacity=0.6,
                    popup=f"Energy Efficiency: {efficiency[i]:.1f} kWh/100km"
                ).add_to(m)
        
        # Track lane changes and traffic light states
        current_lane = controller.vehicle_state.current_lane
        lane_changes = []
        traffic_light_states = {light.id: [] for light in traffic_lights}
        
        # Add vehicle positions with metrics information
        for i, (x, y, heading) in enumerate(positions):
            if i % 10 == 0:  # Add marker every second
                speed = controller.vehicle_state.speed if controller.vehicle_state else 0
                state = controller.vehicle_state.state if controller.vehicle_state else AVState.INITIALIZING
                accel = accelerations[i] if i < len(accelerations) else 0
                comfort = comfort_scores[i] if i < len(comfort_scores) else 0
                eff = efficiency[i] if i < len(efficiency) else 0
                
                # Track lane changes
                if controller.vehicle_state.current_lane != current_lane:
                    lane_changes.append({
                        'time': i * 0.1,
                        'from_lane': current_lane,
                        'to_lane': controller.vehicle_state.current_lane,
                        'position': (x, y),
                        'comfort': comfort,
                        'efficiency': eff
                    })
                    current_lane = controller.vehicle_state.current_lane
                
                # Track traffic light states
                for light in traffic_lights:
                    # Handle both enum objects and string values for state
                    light_state = light.state.value if hasattr(light.state, 'value') else str(light.state)
                    traffic_light_states[light.id].append({
                        'time': i * 0.1,
                        'state': light_state,
                        'position': light.position
                    })
                
                # Create popup content
                popup_content = f"""
                Time: {i * 0.1:.1f}s<br>
                Speed: {speed:.1f} m/s<br>
                Acceleration: {accel:.2f} m/s²<br>
                Comfort Score: {comfort:.2f}<br>
                Energy Efficiency: {eff:.1f} kWh/100km<br>
                State: {state.value}<br>
                Heading: {math.degrees(heading):.1f}°<br>
                Current Lane: {controller.vehicle_state.current_lane}
                """
                
                # Add vehicle position marker
                folium.CircleMarker(
                    location=[y, x],
                    radius=3,
                    color=self.state_colors[state],
                    fill=True,
                    popup=popup_content
                ).add_to(m)
                
                # Add heading indicator
                heading_length = 3.0
                heading_x = x + heading_length * math.cos(heading)
                heading_y = y + heading_length * math.sin(heading)
                folium.PolyLine(
                    locations=[[y, x], [heading_y, heading_x]],
                    color=self.state_colors[state],
                    weight=2,
                    opacity=0.7
                ).add_to(m)
        
        # Add metrics visualization
        metrics_html = self._create_metrics_visualization(positions, 0.1)
        folium.Popup(
            metrics_html,
            max_width=650
        ).add_to(folium.CircleMarker(
            location=[positions[0][1], positions[0][0]],
            radius=6,
            color='purple',
            fill=True
        ).add_to(m))
        
        # Add playback controls
        controls_html = self._create_playback_controls(positions, 0.1)
        # Use a more compatible way to add HTML to avoid corruption with large datasets
        from folium.plugins import DivIcon
        
        # Calculate center coordinates for the controls location
        has_latlon = hasattr(nodes[0], 'lat') and hasattr(nodes[0], 'lon') if nodes else False
        if has_latlon:
            center_lat = sum(n.lat for n in nodes) / len(nodes)
            center_lon = sum(n.lon for n in nodes) / len(nodes)
        else:
            center_lat = sum(n.y for n in nodes) / len(nodes)
            center_lon = sum(n.x for n in nodes) / len(nodes)
        
        # Create a marker with custom HTML for controls (positioned off-screen)
        folium.Marker(
            location=[center_lat, center_lon],  # Use map center
            icon=DivIcon(html=controls_html, icon_size=(0, 0), icon_anchor=(0, 0)),
            opacity=0
        ).add_to(m)
        
        # Add legends
        self.speed_colormap.add_to(m)
        self.accel_colormap.add_to(m)
        self.comfort_colormap.add_to(m)
        self.energy_colormap.add_to(m)
        
        # Save visualization
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        html_path = os.path.join(self.output_dir, f"simulation_{timestamp}.html")
        m.save(html_path)
        
        print(f"Visualization saved to: {html_path}")
        
    def create_simulation_summary(self, controller: AVController,
                                positions: List[Tuple[float, float, float]]) -> None:
        """Create a summary of the simulation.
        
        Args:
            controller: AV controller instance
            positions: List of (x, y, heading) positions during simulation
        """
        # Calculate statistics
        total_time = len(positions) * 0.1
        total_distance = sum(
            math.sqrt(
                (positions[i+1][0] - positions[i][0])**2 +
                (positions[i+1][1] - positions[i][1])**2
            )
            for i in range(len(positions)-1)
        )
        avg_speed = total_distance / total_time if total_time > 0 else 0
        
        # Calculate metrics
        accelerations = self._calculate_acceleration(positions, 0.1)
        energy_consumption, efficiency = self._calculate_energy_consumption(positions, 0.1)
        comfort_scores, jerk = self._calculate_comfort_metrics(positions, 0.1)
        
        # Calculate energy and comfort statistics
        total_energy = sum(energy_consumption)
        avg_efficiency = sum(efficiency) / len(efficiency) if efficiency else 0
        avg_comfort = sum(comfort_scores) / len(comfort_scores) if comfort_scores else 0
        max_jerk = max(abs(j) for j in jerk) if jerk else 0
        
        # Track lane changes
        current_lane = controller.vehicle_state.current_lane
        lane_changes = []
        for i, (x, y, _) in enumerate(positions):
            if controller.vehicle_state.current_lane != current_lane:
                lane_changes.append({
                    'time': i * 0.1,
                    'from_lane': current_lane,
                    'to_lane': controller.vehicle_state.current_lane,
                    'position': {'x': x, 'y': y},
                    'comfort': comfort_scores[i] if i < len(comfort_scores) else 0,
                    'efficiency': efficiency[i] if i < len(efficiency) else 0
                })
                current_lane = controller.vehicle_state.current_lane
        
        # Create summary data
        summary = {
            "total_time": total_time,
            "total_distance": total_distance,
            "average_speed": avg_speed,
            "energy_stats": {
                "total_energy": total_energy,
                "average_efficiency": avg_efficiency,
                "max_efficiency": max(efficiency) if efficiency else 0,
                "min_efficiency": min(efficiency) if efficiency else 0
            },
            "comfort_stats": {
                "average_comfort": avg_comfort,
                "min_comfort": min(comfort_scores) if comfort_scores else 0,
                "max_jerk": max_jerk
            },
            "acceleration_stats": {
                "max_acceleration": max(accelerations),
                "max_deceleration": min(accelerations),
                "average_acceleration": sum(accelerations) / len(accelerations)
            },
            "final_position": {
                "x": positions[-1][0],
                "y": positions[-1][1],
                "heading": math.degrees(positions[-1][2])
            },
            "lane_changes": lane_changes,
            "vehicle_states": [
                {
                    "time": i * 0.1,
                    "position": {"x": x, "y": y},
                    "heading": math.degrees(heading),
                    "speed": controller.vehicle_state.speed if controller.vehicle_state else 0,
                    "acceleration": accelerations[i] if i < len(accelerations) else 0,
                    "comfort": comfort_scores[i] if i < len(comfort_scores) else 0,
                    "efficiency": efficiency[i] if i < len(efficiency) else 0,
                    "state": controller.vehicle_state.state.value if controller.vehicle_state and hasattr(controller.vehicle_state.state, 'value') else str(controller.vehicle_state.state) if controller.vehicle_state else "unknown",
                    "current_lane": controller.vehicle_state.current_lane if controller.vehicle_state else "unknown"
                }
                for i, (x, y, heading) in enumerate(positions)
                if i % 10 == 0  # Record every second
            ]
        }
        
        # Save summary
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        json_path = os.path.join(self.output_dir, f"simulation_summary_{timestamp}.json")
        with open(json_path, 'w') as f:
            json.dump(summary, f, indent=2)
            
        print(f"Simulation summary saved to: {json_path}") 