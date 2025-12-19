import streamlit as st
import requests
import openrouteservice
import numpy as np
import folium
from streamlit_folium import st_folium
import time
from typing import List, Dict, Optional, Tuple

# ==========================================
# 1. SERVICES (Converted from Django Services)
# ==========================================

class AirQualityService:
    """Service to fetch air quality data from WAQI API"""
    BASE_URL = "https://api.waqi.info"
    
    def __init__(self, api_key):
        self.api_key = api_key
    
    def get_aqi_by_coordinates(self, lat: float, lng: float) -> Optional[Dict]:
        url = f"{self.BASE_URL}/feed/geo:{lat};{lng}/"
        params = {'token': self.api_key}
        try:
            response = requests.get(url, params=params, timeout=5)
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'ok':
                    return data['data']
            return None
        except Exception:
            return None
    
    def get_multiple_aqi_for_route(self, coordinates: List[tuple]) -> List[Dict]:
        """Fetch AQI for points along the route with a progress bar"""
        aqi_data = []
        # Create a placeholder for progress to avoid UI clutter
        progress_text = "Fetching Air Quality data..."
        my_bar = st.progress(0, text=progress_text)
        
        total = len(coordinates)
        for i, (lat, lng) in enumerate(coordinates):
            data = self.get_aqi_by_coordinates(lat, lng)
            if data:
                aqi_data.append(data)
            # Update progress
            my_bar.progress((i + 1) / total, text=f"{progress_text} ({i+1}/{total})")
            time.sleep(0.1)  # Rate limiting
            
        my_bar.empty()
        return aqi_data

class RoutingService:
    """Service to handle routing using OpenRouteService"""
    def __init__(self, api_key):
        self.client = openrouteservice.Client(key=api_key)
    
    def geocode_address(self, address: str) -> Optional[Tuple[float, float]]:
        try:
            # Focus on Kolkata as per original code
            result = self.client.pelias_search(text=address, focus_point=[88.3639, 22.5726])
            if result and 'features' in result and len(result['features']) > 0:
                coords = result['features'][0]['geometry']['coordinates']
                return tuple(coords)  # Returns (lng, lat)
            return None
        except Exception as e:
            st.error(f"Geocoding error: {e}")
            return None

    def get_route(self, start_coords: Tuple[float, float], end_coords: Tuple[float, float]) -> Optional[Dict]:
        """Get standard route"""
        try:
            # ORS expects [lng, lat]
            coords = [start_coords, end_coords]
            route = self.client.directions(
                coordinates=coords,
                profile='driving-car',
                format='geojson',
                instructions=True,
                elevation=False
            )
            return self._parse_route_data(route)
        except Exception as e:
            st.error(f"Routing error: {e}")
            return None

    def get_route_via_waypoint(self, start_coords, waypoint_coords, end_coords):
        """Get route passing through a specific waypoint"""
        try:
            coords = [start_coords, waypoint_coords, end_coords]
            route = self.client.directions(
                coordinates=coords,
                profile='driving-car',
                format='geojson',
                instructions=True,
                elevation=False,
                radiuses=[350, 350, 350]
            )
            return self._parse_route_data(route)
        except Exception:
            return None

    def _parse_route_data(self, route_geojson):
        if not route_geojson or 'features' not in route_geojson:
            return None
        feature = route_geojson['features'][0]
        props = feature['properties']
        return {
            'distance': props.get('summary', {}).get('distance', 0) / 1000,
            'duration': props.get('summary', {}).get('duration', 0) / 60,
            'coordinates': feature['geometry']['coordinates'],
            'geometry': feature['geometry']
        }

    def sample_route_points(self, coordinates, num_samples=10):
        """Sample points along the route for AQI checking"""
        if len(coordinates) <= num_samples:
            return [(coord[1], coord[0]) for coord in coordinates] # Swap to (lat, lng)
        
        indices = np.linspace(0, len(coordinates) - 1, num_samples, dtype=int)
        sampled = [coordinates[i] for i in indices]
        return [(coord[1], coord[0]) for coord in sampled] # Swap to (lat, lng)

class DijkstraOptimizer:
    """Optimized route finder (Adapted from Django logic)"""
    def __init__(self, aqi_key, ors_key):
        self.aqi_service = AirQualityService(aqi_key)
        self.routing_service = RoutingService(ors_key)

    def _calculate_bearing(self, lat1, lon1, lat2, lon2):
        lat1_rad, lat2_rad = np.radians(lat1), np.radians(lat2)
        dlon = np.radians(lon2 - lon1)
        x = np.sin(dlon) * np.cos(lat2_rad)
        y = np.cos(lat1_rad) * np.sin(lat2_rad) - np.sin(lat1_rad) * np.cos(lat2_rad) * np.cos(dlon)
        return (np.degrees(np.arctan2(x, y)) + 360) % 360

    def _calculate_destination_point(self, lat, lon, distance_km, bearing):
        R = 6371
        lat_rad, lon_rad, bearing_rad = np.radians(lat), np.radians(lon), np.radians(bearing)
        new_lat_rad = np.arcsin(np.sin(lat_rad) * np.cos(distance_km / R) +
                                np.cos(lat_rad) * np.sin(distance_km / R) * np.cos(bearing_rad))
        new_lon_rad = lon_rad + np.arctan2(np.sin(bearing_rad) * np.sin(distance_km / R) * np.cos(lat_rad),
                                           np.cos(distance_km / R) - np.sin(lat_rad) * np.sin(new_lat_rad))
        return np.degrees(new_lat_rad), np.degrees(new_lon_rad)

    def find_optimal_route(self, start_lat, start_lng, end_lat, end_lng, priority='balanced'):
        # 1. Get Base Route
        base_route = self.routing_service.get_route((start_lng, start_lat), (end_lng, end_lat))
        
        if not base_route:
            return None
        
        final_route = base_route

        # 2. Apply Optimization (Detours) if not "shortest"
        if priority != 'shortest':
            mid_lat = (start_lat + end_lat) / 2
            mid_lng = (start_lng + end_lng) / 2
            bearing = self._calculate_bearing(start_lat, start_lng, end_lat, end_lng)
            
            # Logic from your dijkstra_optimizer.py
            detour_configs = {
                'balanced': {'dist_factor': 0.15, 'angle': 50, 'side': 1}, # Right
                'cleanest': {'dist_factor': 0.35, 'angle': 80, 'side': -1}, # Left
            }
            config = detour_configs.get(priority, detour_configs['balanced'])
            
            dist = min(3.0, base_route['distance'] * config['dist_factor'])
            detour_bearing = (bearing + (config['angle'] * config['side'])) % 360
            
            wp_lat, wp_lng = self._calculate_destination_point(mid_lat, mid_lng, dist, detour_bearing)
            
            # Try getting route via waypoint
            alt_route = self.routing_service.get_route_via_waypoint(
                (start_lng, start_lat), (wp_lng, wp_lat), (end_lng, end_lat)
            )
            
            if alt_route:
                final_route = alt_route

        # 3. Fetch AQI Data for the final route
        sampled_points = self.routing_service.sample_route_points(final_route['coordinates'], num_samples=8)
        aqi_data = self.aqi_service.get_multiple_aqi_for_route(sampled_points)
        
        # Calculate Average AQI
        valid_aqi = [d['aqi'] for d in aqi_data if d.get('aqi') is not None]
        avg_aqi = np.mean(valid_aqi) if valid_aqi else 0
        
        final_route['average_aqi'] = avg_aqi
        final_route['aqi_data'] = aqi_data
        return final_route

# ==========================================
# 2. STREAMLIT UI (Converted from Views/Templates)
# ==========================================

st.set_page_config(page_title="AQI Route Optimizer", page_icon="🌍", layout="wide")

st.title("🌿 Eco-Friendly Route Optimizer")
st.markdown("Find the healthiest path between two locations based on real-time Air Quality.")

# --- Sidebar Inputs ---
with st.sidebar:
    st.header("Configuration")
    
    # API Key Management
    ors_key = st.text_input("OpenRouteService API Key", type="password", value=st.secrets.get("ORS_API_KEY", ""))
    waqi_key = st.text_input("WAQI API Key", type="password", value=st.secrets.get("WAQI_API_KEY", ""))
    
    st.divider()
    
    st.header("Route Settings")
    source_addr = st.text_input("Source Address", "Kolkata Airport")
    dest_addr = st.text_input("Destination Address", "Victoria Memorial, Kolkata")
    priority = st.selectbox("Optimization Priority", ["balanced", "cleanest", "shortest"])
    
    find_btn = st.button("Find Optimal Route", type="primary")

# --- Main App Logic ---
if find_btn:
    if not ors_key or not waqi_key:
        st.error("Please provide both API Keys in the sidebar or secrets.toml")
    else:
        with st.spinner("Calculating optimal route..."):
            # Initialize Logic
            optimizer = DijkstraOptimizer(waqi_key, ors_key)
            router = optimizer.routing_service
            
            # 1. Geocoding
            source_coords = router.geocode_address(source_addr)
            dest_coords = router.geocode_address(dest_addr)
            
            if source_coords and dest_coords:
                source_lng, source_lat = source_coords
                dest_lng, dest_lat = dest_coords
                
                # 2. Optimization
                result = optimizer.find_optimal_route(
                    source_lat, source_lng, dest_lat, dest_lng, priority=priority
                )
                
                if result:
                    # 3. Display Results
                    c1, c2, c3 = st.columns(3)
                    c1.metric("Distance", f"{result['distance']:.2f} km")
                    c2.metric("Duration", f"{result['duration']:.0f} mins")
                    
                    aqi_color = "normal"
                    if result['average_aqi'] > 150: aqi_color = "inverse"
                    c3.metric("Avg AQI", f"{result['average_aqi']:.0f}", delta_color=aqi_color)
                    
                    # 4. Map Visualization
                    m = folium.Map(location=[source_lat, source_lng], zoom_start=12)
                    
                    # Route Line (OpenRouteService returns [lng, lat], Folium needs [lat, lng])
                    route_line = [(c[1], c[0]) for c in result['coordinates']]
                    
                    color_map = {'shortest': 'blue', 'balanced': 'orange', 'cleanest': 'green'}
                    folium.PolyLine(
                        route_line, 
                        color=color_map.get(priority, 'blue'), 
                        weight=5, 
                        opacity=0.8,
                        tooltip=f"Route: {priority}"
                    ).add_to(m)
                    
                    # Start/End Markers
                    folium.Marker([source_lat, source_lng], popup=f"Start: {source_addr}", icon=folium.Icon(color='green', icon='play')).add_to(m)
                    folium.Marker([dest_lat, dest_lng], popup=f"End: {dest_addr}", icon=folium.Icon(color='red', icon='stop')).add_to(m)
                    
                    # AQI Points along route
                    for data in result.get('aqi_data', []):
                        lat = data['location']['lat']
                        lng = data['location']['lng']
                        aqi = data['aqi']
                        
                        # Color coding for AQI
                        color = "green"
                        if aqi > 50: color = "yellow"
                        if aqi > 100: color = "orange"
                        if aqi > 150: color = "red"
                        if aqi > 200: color = "purple"
                        
                        folium.CircleMarker(
                            location=[lat, lng],
                            radius=8,
                            popup=f"AQI: {aqi}",
                            color=color,
                            fill=True,
                            fill_opacity=0.7
                        ).add_to(m)

                    st_folium(m, width=800, height=500)
                else:
                    st.error("Could not find a route. The locations might be too far apart or invalid.")
            else:
                st.error("Could not geocode one of the addresses. Please try being more specific.")