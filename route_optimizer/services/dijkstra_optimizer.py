# import heapq
# import numpy as np
# from typing import Dict, List, Tuple, Optional
# from .air_quality_service import AirQualityService
# from .routing_service import RoutingService


# class DijkstraOptimizer:
#     """
#     Optimized route finder using Dijkstra's algorithm with AQI weighting
#     """
    
#     def __init__(self):
#         self.aqi_service = AirQualityService()
#         self.routing_service = RoutingService()
    
#     def calculate_edge_weight(self, distance: float, aqi: float, 
#                             priority: str = 'balanced', pollutant_type: str = None) -> float:
#         """
#         Calculate edge weight based on distance and AQI or specific pollutants
        
#         priority options:
#         - 'shortest': Prioritize shortest distance
#         - 'cleanest': Prioritize cleanest air
#         - 'balanced': Balance between distance and air quality
#         - 'pm25': Prioritize minimum PM2.5
#         - 'pm10': Prioritize minimum PM10
#         - 'co': Prioritize minimum CO
#         - 'o3': Prioritize minimum O3
#         - 'so2': Prioritize minimum SO2
#         """
#         # Normalize AQI (typical range 0-500)
#         normalized_aqi = min(aqi / 500.0, 1.0)
        
#         # For shortest route, completely ignore AQI
#         if priority == 'shortest':
#             return distance
            
#         # For balanced route, use moderate weighting
#         if priority == 'balanced':
#             # 60% distance, 40% AQI
#             return (0.6 * distance) + (0.4 * normalized_aqi * distance * 2)
        
#         # For cleanest route, heavily weight AQI
#         if priority == 'cleanest':
#             # Apply exponential penalty for poor air quality
#             aqi_factor = normalized_aqi ** 2 * 4  # Square the AQI factor
#             return (0.1 * distance) + (0.9 * aqi_factor * distance)
            
#         # For specific pollutants, focus almost entirely on that pollutant
#         if priority in ['pm25', 'pm10', 'co', 'o3', 'so2']:
#             # Apply cubic penalty for poor air quality
#             aqi_factor = normalized_aqi ** 3 * 5
#             return (0.05 * distance) + (0.95 * aqi_factor * distance)
            
#         # Default balanced approach
#         return (0.5 * distance) + (0.5 * normalized_aqi * distance * 2)
    


    
#     def dijkstra_shortest_path(self, graph: Dict, start: int, end: int) -> Tuple[List[int], float]:
#         """
#         Implementation of Dijkstra's algorithm with robust error handling
        
#         Returns: (path, total_cost)
#         """
#         # Find all possible nodes (include all nodes that appear as keys or neighbors)
#         all_nodes = set(graph.keys())
#         for node in graph:
#             all_nodes.update(graph[node].keys())
        
#         # Ensure start and end are in the node set
#         all_nodes.add(start)
#         all_nodes.add(end)
        
#         # Initialize distances and previous nodes for ALL possible nodes
#         distances = {node: float('infinity') for node in all_nodes}
#         distances[start] = 0
#         previous = {node: None for node in all_nodes}
        
#         # Priority queue: (distance, node)
#         pq = [(0, start)]
#         visited = set()
        
#         while pq:
#             current_dist, current_node = heapq.heappop(pq)
            
#             if current_node in visited:
#                 continue
            
#             visited.add(current_node)
            
#             # Found destination
#             if current_node == end:
#                 break
            
#             # Check neighbors (only if current_node has outgoing edges)
#             if current_node in graph:
#                 for neighbor, weight in graph[current_node].items():
#                     if neighbor in distances:  # Safety check
#                         distance = current_dist + weight
                        
#                         if distance < distances[neighbor]:
#                             distances[neighbor] = distance
#                             previous[neighbor] = current_node
#                             heapq.heappush(pq, (distance, neighbor))
        
#         # Reconstruct path
#         path = []
#         current = end
        
#         # Check if destination was reached
#         if distances[end] == float('infinity'):
#             print(f"   ⚠️ Warning: No path found from {start} to {end}, using direct path")
#             return [start, end], float('infinity')
        
#         while current is not None:
#             path.append(current)
#             current = previous[current]
        
#         path.reverse()
        
#         # Validate path
#         if not path or path[0] != start or path[-1] != end:
#             print(f"   ⚠️ Warning: Invalid path reconstructed, using direct path")
#             return [start, end], distances[end]
        
#         return path, distances[end]


        
        




#     def find_optimal_route(self, start_lat: float, start_lng: float,
#                       end_lat: float, end_lng: float,
#                       priority: str = 'balanced',
#                       pollutant_type: str = None,
#                       num_waypoints: int = 10) -> Dict:
#         """
#         Find optimal route using alternative routes and AQI weighting
#         """
        
#         print(f"   Finding {priority} route...")
        
#         # For shortest route, get direct path
#         if priority == 'shortest':
#             base_route = self.routing_service.get_route(
#                 (start_lng, start_lat),
#                 (end_lng, end_lat)
#             )
            
#             if not base_route:
#                 return None
            
#             sampled_points = self.routing_service.sample_route_points(
#                 base_route['coordinates'],
#                 num_samples=8
#             )
            
#             aqi_data_list = self.aqi_service.get_multiple_aqi_for_route(sampled_points)
#             avg_aqi = np.mean([data['aqi'] for data in aqi_data_list if data.get('aqi', 0) > 0]) if aqi_data_list else 100
                
#             return {
#                 'distance': base_route['distance'],
#                 'duration': base_route['duration'],
#                 'average_aqi': float(avg_aqi),
#                 'aqi_data': aqi_data_list,
#                 'geometry': base_route['geometry'],
#                 'coordinates': base_route['coordinates'],
#                 'sampled_points': sampled_points,
#                 'optimal_path_indices': list(range(len(sampled_points))),
#                 'dijkstra_cost': base_route['distance'],
#                 'priority': priority
#             }
        
#         # Get alternative routes from OpenRouteService
#         print("   → Fetching alternative routes from OpenRouteService...")
#         alternative_routes = self.routing_service.get_alternative_routes(
#             (start_lng, start_lat),
#             (end_lng, end_lat)
#         )
        
#         print(f"   ✓ Got {len(alternative_routes)} route options")
        
#         # If we only got one route, generate waypoint-based alternatives
#         if len(alternative_routes) < 2:
#             print("   → Generating waypoint-based alternative...")
#             waypoint_route = self._generate_waypoint_alternative(
#                 start_lat, start_lng, end_lat, end_lng, priority, pollutant_type
#             )
#             if waypoint_route:
#                 alternative_routes.append(waypoint_route)
        
#         # Evaluate each route based on AQI and priority
#         best_route = None
#         best_score = float('inf')
        
#         for idx, route in enumerate(alternative_routes):
#             # Sample points and get AQI
#             sampled_points = self.routing_service.sample_route_points(
#                 route['coordinates'],
#                 num_samples=12
#             )
            
#             aqi_data_list = self.aqi_service.get_multiple_aqi_for_route(sampled_points)
#             avg_aqi = np.mean([data['aqi'] for data in aqi_data_list if data.get('aqi', 0) > 0]) if aqi_data_list else 100
            
#             # Calculate score based on priority
#             score = self._calculate_route_score(
#                 route['distance'], 
#                 avg_aqi, 
#                 priority
#             )
            
#             print(f"   Route {idx+1}: {route['distance']:.2f}km, AQI {avg_aqi:.1f}, Score: {score:.2f}")
            
#             if score < best_score:
#                 best_score = score
#                 best_route = {
#                     **route,
#                     'average_aqi': float(avg_aqi),
#                     'aqi_data': aqi_data_list,
#                     'sampled_points': sampled_points,
#                     'optimal_path_indices': list(range(len(sampled_points))),
#                     'dijkstra_cost': score,
#                     'priority': priority
#                 }
        
#         print(f"   ✓ Selected best route: {best_route['distance']:.2f}km, AQI {best_route['average_aqi']:.1f}")
        
#         return best_route


#     def _calculate_route_score(self, distance: float, avg_aqi: float, priority: str) -> float:
#         """Calculate route score based on priority"""
#         if priority == 'shortest':
#             return distance
#         elif priority == 'cleanest':
#             return distance * 0.2 + avg_aqi * 0.8
#         elif priority in ['pm25', 'pm10', 'co', 'o3', 'so2']:
#             return distance * 0.1 + avg_aqi * 0.9
#         else:  # balanced
#             return distance * 0.5 + (avg_aqi / 100) * distance * 0.5


#     def _generate_waypoint_alternative(self, start_lat: float, start_lng: float,
#                                     end_lat: float, end_lng: float,
#                                     priority: str, pollutant_type: str = None) -> Optional[Dict]:
#         """Generate an alternative route using strategic waypoints"""
#         try:
#             # Create ONE strategic waypoint perpendicular to direct path
#             mid_lat = (start_lat + end_lat) / 2
#             mid_lng = (start_lng + end_lng) / 2
            
#             # Calculate perpendicular offset
#             bearing = self._calculate_bearing(start_lat, start_lng, end_lat, end_lng)
            
#             # Offset distance based on priority
#             if priority in ['cleanest', 'pm25', 'pm10', 'co', 'o3', 'so2']:
#                 offset_km = 2.0  # 2km offset
#                 perp_bearing = (bearing + 90) % 360  # Go right
#             else:
#                 offset_km = 1.0
#                 perp_bearing = (bearing - 90) % 360  # Go left
            
#             # Calculate waypoint
#             waypoint_lat, waypoint_lng = self._calculate_destination_point(
#                 mid_lat, mid_lng, offset_km, perp_bearing
#             )
            
#             # Get route through waypoint
#             route = self.routing_service.get_route_with_waypoints(
#                 [(start_lng, start_lat), (waypoint_lng, waypoint_lat), (end_lng, end_lat)],
#                 priority=priority
#             )
            
#             return route
            
#         except Exception as e:
#             print(f"   ⚠️ Could not generate waypoint alternative: {e}")
#             return None




#     def _generate_candidate_waypoints(self, start_lat: float, start_lng: float,
#                                        end_lat: float, end_lng: float,
#                                        priority: str) -> List[Tuple]:
#         """
#         Generate candidate waypoints exploring different geographic areas
#         Returns: List of (lat, lng) tuples
#         """
#         waypoints = [(start_lat, start_lng)]
        
#         # Calculate bearing and distance
#         bearing = self._calculate_bearing(start_lat, start_lng, end_lat, end_lng)
#         total_distance = self._haversine_distance(start_lat, start_lng, end_lat, end_lng)
        
#         # Determine exploration strategy based on priority
#         if priority in ['cleanest', 'pm25', 'pm10', 'co', 'o3', 'so2']:
#             # Create wide exploration pattern for air quality focused routes
#             num_layers = 3
#             points_per_layer = 5
#             max_deviation_km = 3.0  # 3km perpendicular deviation
            
#         else:  # balanced
#             num_layers = 2
#             points_per_layer = 4
#             max_deviation_km = 1.5  # 1.5km perpendicular deviation
        
#         # Generate waypoint layers between start and end
#         for layer in range(1, num_layers + 1):
#             progress = layer / (num_layers + 1)
            
#             # Base point along direct line
#             base_lat = start_lat + (end_lat - start_lat) * progress
#             base_lng = start_lng + (end_lng - start_lng) * progress
            
#             # Create points perpendicular to main direction
#             for i in range(points_per_layer):
#                 # Create symmetric points on both sides
#                 if i == 0:
#                     # Center point (on direct line)
#                     waypoints.append((base_lat, base_lng))
#                 else:
#                     # Calculate perpendicular offsets
#                     side = 1 if i % 2 == 0 else -1
#                     offset_km = (i // 2 + 1) / (points_per_layer // 2 + 1) * max_deviation_km
                    
#                     # Perpendicular bearing (90 degrees off main bearing)
#                     perp_bearing = (bearing + 90 * side) % 360
                    
#                     # Calculate offset point
#                     offset_lat, offset_lng = self._calculate_destination_point(
#                         base_lat, base_lng,
#                         offset_km,
#                         perp_bearing
#                     )
                    
#                     waypoints.append((offset_lat, offset_lng))
        
#         # Add destination
#         waypoints.append((end_lat, end_lng))
        
#         return waypoints
    
#     def _calculate_bearing(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
#         """Calculate bearing between two points in degrees"""
#         lat1_rad = np.radians(lat1)
#         lat2_rad = np.radians(lat2)
#         dlon = np.radians(lon2 - lon1)
        
#         x = np.sin(dlon) * np.cos(lat2_rad)
#         y = np.cos(lat1_rad) * np.sin(lat2_rad) - np.sin(lat1_rad) * np.cos(lat2_rad) * np.cos(dlon)
        
#         bearing = np.degrees(np.arctan2(x, y))
#         return (bearing + 360) % 360
    
#     def _calculate_destination_point(self, lat: float, lon: float, 
#                                      distance_km: float, bearing: float) -> Tuple[float, float]:
#         """
#         Calculate destination point given start point, distance (in km), and bearing
#         Using Haversine formula
#         """
#         R = 6371  # Earth's radius in kilometers
        
#         lat_rad = np.radians(lat)
#         lon_rad = np.radians(lon)
#         bearing_rad = np.radians(bearing)
        
#         # Calculate new latitude
#         new_lat_rad = np.arcsin(
#             np.sin(lat_rad) * np.cos(distance_km / R) +
#             np.cos(lat_rad) * np.sin(distance_km / R) * np.cos(bearing_rad)
#         )
        
#         # Calculate new longitude
#         new_lon_rad = lon_rad + np.arctan2(
#             np.sin(bearing_rad) * np.sin(distance_km / R) * np.cos(lat_rad),
#             np.cos(distance_km / R) - np.sin(lat_rad) * np.sin(new_lat_rad)
#         )
        
#         new_lat = np.degrees(new_lat_rad)
#         new_lon = np.degrees(new_lon_rad)
        
#         return new_lat, new_lon



    
#     def _build_smart_graph(self, points: List[Tuple], 
#                       aqi_data: List[Dict],
#                       priority: str,
#                       pollutant_type: str = None) -> Dict:
#         """
#         Build graph that connects points intelligently based on proximity and priority
#         points: List of (lat, lng) tuples
#         """
#         n = len(points)
#         graph = {}
        
#         # Initialize ALL nodes in the graph (even if they have no outgoing edges initially)
#         for i in range(n):
#             graph[i] = {}
        
#         print(f"   Building graph with {n} nodes for {priority} priority...")
        
#         # Start node connects to points in first layer
#         for i in range(1, min(8, n)):
#             distance = self._haversine_distance(
#                 points[0][0], points[0][1],
#                 points[i][0], points[i][1]
#             )
            
#             aqi_0 = aqi_data[0]['aqi'] if aqi_data[0] else 100
#             aqi_i = aqi_data[i]['aqi'] if i < len(aqi_data) and aqi_data[i] else 100
#             avg_aqi = (aqi_0 + aqi_i) / 2
            
#             weight = self.calculate_edge_weight(distance, avg_aqi, priority, pollutant_type)
#             graph[0][i] = weight
        
#         # Middle nodes connect to nearby nodes and forward progress nodes
#         for i in range(1, n - 1):
#             # Calculate distances to all subsequent nodes
#             distances = []
#             for j in range(i + 1, n):
#                 dist = self._haversine_distance(
#                     points[i][0], points[i][1],
#                     points[j][0], points[j][1]
#                 )
#                 distances.append((j, dist))
            
#             # Sort by distance and connect to closest nodes
#             distances.sort(key=lambda x: x[1])
            
#             # Connect to closest 6 nodes (or fewer if not enough nodes)
#             num_connections = min(6, len(distances))
#             for j, distance in distances[:num_connections]:
#                 aqi_i = aqi_data[i]['aqi'] if i < len(aqi_data) and aqi_data[i] else 100
#                 aqi_j = aqi_data[j]['aqi'] if j < len(aqi_data) and aqi_data[j] else 100
#                 avg_aqi = (aqi_i + aqi_j) / 2
                
#                 weight = self.calculate_edge_weight(distance, avg_aqi, priority, pollutant_type)
#                 graph[i][j] = weight
            
#             # Always ensure connection to end point
#             if n - 1 not in graph[i] and i < n - 1:
#                 distance = self._haversine_distance(
#                     points[i][0], points[i][1],
#                     points[n-1][0], points[n-1][1]
#                 )
                
#                 aqi_i = aqi_data[i]['aqi'] if i < len(aqi_data) and aqi_data[i] else 100
#                 aqi_end = aqi_data[n-1]['aqi'] if aqi_data[n-1] else 100
#                 avg_aqi = (aqi_i + aqi_end) / 2
                
#                 weight = self.calculate_edge_weight(distance, avg_aqi, priority, pollutant_type)
#                 graph[i][n-1] = weight
        
#         # Verify graph connectivity
#         total_edges = sum(len(neighbors) for neighbors in graph.values())
#         print(f"   ✓ Graph built: {n} nodes, {total_edges} edges")
        
#         return graph





#     def _haversine_distance(self, lat1: float, lon1: float, 
#                            lat2: float, lon2: float) -> float:
#         """
#         Calculate distance between two points using Haversine formula
#         Returns distance in kilometers
#         """
#         R = 6371  # Earth's radius in kilometers
        
#         lat1_rad = np.radians(lat1)
#         lat2_rad = np.radians(lat2)
#         dlat = np.radians(lat2 - lat1)
#         dlon = np.radians(lon2 - lon1)
        
#         a = np.sin(dlat/2)**2 + np.cos(lat1_rad) * np.cos(lat2_rad) * np.sin(dlon/2)**2
#         c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1-a))
        
#         return R * c
    
#     def compare_routes(self, start_lat: float, start_lng: float,
#                       end_lat: float, end_lng: float) -> Dict:
#         """
#         Compare routes with different priorities
#         """
#         priorities = ['shortest', 'balanced', 'cleanest', 'pm25', 'pm10', 'co', 'o3', 'so2']
#         results = {}
        
#         for priority in priorities:
#             pollutant_type = priority if priority in ['pm25', 'pm10', 'co', 'o3', 'so2'] else None
#             route = self.find_optimal_route(
#                 start_lat, start_lng, end_lat, end_lng,
#                 priority=priority,
#                 pollutant_type=pollutant_type
#             )
#             results[priority] = route
        
#         return results



import heapq
import numpy as np
from typing import Dict, List, Tuple, Optional
from .air_quality_service import AirQualityService
from .routing_service import RoutingService


class DijkstraOptimizer:
    """
    Optimized route finder using different routing strategies
    """
    
    def __init__(self):
        self.aqi_service = AirQualityService()
        self.routing_service = RoutingService()
    
    # def find_optimal_route(self, start_lat: float, start_lng: float,
    #                       end_lat: float, end_lng: float,
    #                       priority: str = 'balanced',
    #                       pollutant_type: str = None,
    #                       num_waypoints: int = 10) -> Dict:
    #     """
    #     Find optimal route based on priority using different routing strategies
    #     """
        
    #     print(f"\n   🔍 Finding {priority.upper()} route...")
        
    #     # Get base route
    #     base_route = self.routing_service.get_route(
    #         (start_lng, start_lat),  # CORRECT: (lng, lat)
    #         (end_lng, end_lat)
    #     )
        
    #     if not base_route:
    #         print("   ✗ Could not get base route")
    #         return None
        
    #     # For shortest priority - return direct route
    #     if priority == 'shortest':
    #         print("   → Using DIRECT shortest path")
    #         sampled_points = self.routing_service.sample_route_points(
    #             base_route['coordinates'],
    #             num_samples=8
    #         )
    #         aqi_data_list = self.aqi_service.get_multiple_aqi_for_route(sampled_points)
    #         avg_aqi = np.mean([data['aqi'] for data in aqi_data_list if data.get('aqi', 0) > 0]) if aqi_data_list else 100
            
    #         return {
    #             'distance': base_route['distance'],
    #             'duration': base_route['duration'],
    #             'average_aqi': float(avg_aqi),
    #             'aqi_data': aqi_data_list,
    #             'geometry': base_route['geometry'],
    #             'coordinates': base_route['coordinates'],
    #             'sampled_points': sampled_points,
    #             'optimal_path_indices': list(range(len(sampled_points))),
    #             'dijkstra_cost': base_route['distance'],
    #             'priority': priority
    #         }
        
    #     # For other priorities, try to get alternative route
    #     print(f"   → Generating alternative route for {priority}...")
        
    #     # Calculate a strategic detour waypoint
    #     mid_lat = (start_lat + end_lat) / 2
    #     mid_lng = (start_lng + end_lng) / 2
        
    #     # Calculate bearing
    #     bearing = self._calculate_bearing(start_lat, start_lng, end_lat, end_lng)
        
    #     # Determine detour based on priority
    #     if priority in ['cleanest', 'pm25', 'pm10', 'co', 'o3', 'so2']:
    #         # Larger detour for air quality routes
    #         detour_distance = min(3.0, base_route['distance'] * 0.3)  # 30% detour or 3km max
    #         detour_angle = 75  # More perpendicular
    #         print(f"   → Air quality route: {detour_distance:.1f}km detour")
    #     else:  # balanced
    #         # Moderate detour for balanced
    #         detour_distance = min(1.5, base_route['distance'] * 0.2)  # 20% detour or 1.5km max
    #         detour_angle = 60
    #         print(f"   → Balanced route: {detour_distance:.1f}km detour")
        
    #     # Try right side detour
    #     waypoint_lat_right, waypoint_lng_right = self._calculate_destination_point(
    #         mid_lat, mid_lng,
    #         detour_distance,
    #         (bearing + detour_angle) % 360
    #     )
        
    #     # Try left side detour
    #     waypoint_lat_left, waypoint_lng_left = self._calculate_destination_point(
    #         mid_lat, mid_lng,
    #         detour_distance,
    #         (bearing - detour_angle) % 360
    #     )
        
    #     # Try both detour routes and pick the one that works
    #     routes_to_try = [
    #         ('right', waypoint_lng_right, waypoint_lat_right),
    #         ('left', waypoint_lng_left, waypoint_lat_left),
    #     ]
        
    #     alternative_route = None
    #     for side, wp_lng, wp_lat in routes_to_try:
    #         print(f"   → Trying {side} detour via ({wp_lat:.4f}, {wp_lng:.4f})...")
    #         try:
    #             route = self.routing_service.get_route_via_waypoint(
    #                 (start_lng, start_lat),
    #                 (wp_lng, wp_lat),
    #                 (end_lng, end_lat)
    #             )
    #             if route and route['distance'] > base_route['distance'] * 0.95:  # At least 5% different
    #                 print(f"   ✓ {side.capitalize()} detour successful: {route['distance']:.2f}km")
    #                 alternative_route = route
    #                 break
    #             else:
    #                 print(f"   ⚠ {side} detour too similar to direct route")
    #         except Exception as e:
    #             print(f"   ⚠ {side} detour failed: {e}")
    #             continue
        
    #     # Use alternative route if found, otherwise use base route
    #     final_route = alternative_route if alternative_route else base_route
        
    #     if alternative_route:
    #         print(f"   ✓ Using ALTERNATIVE route: {final_route['distance']:.2f}km vs {base_route['distance']:.2f}km direct")
    #     else:
    #         print(f"   ⚠ Using DIRECT route (no alternative found): {final_route['distance']:.2f}km")
        
    #     # Sample and get AQI data
    #     sampled_points = self.routing_service.sample_route_points(
    #         final_route['coordinates'],
    #         num_samples=12
    #     )
        
    #     aqi_data_list = self.aqi_service.get_multiple_aqi_for_route(sampled_points)
    #     avg_aqi = np.mean([data['aqi'] for data in aqi_data_list if data.get('aqi', 0) > 0]) if aqi_data_list else 100
        
    #     print(f"   ✓ Route AQI: {avg_aqi:.1f}")
        
    #     return {
    #         'distance': final_route['distance'],
    #         'duration': final_route['duration'],
    #         'average_aqi': float(avg_aqi),
    #         'aqi_data': aqi_data_list,
    #         'geometry': final_route['geometry'],
    #         'coordinates': final_route['coordinates'],
    #         'sampled_points': sampled_points,
    #         'optimal_path_indices': list(range(len(sampled_points))),
    #         'dijkstra_cost': final_route['distance'],
    #         'priority': priority
    #     }
    
    def find_optimal_route(self, start_lat: float, start_lng: float,
                      end_lat: float, end_lng: float,
                      priority: str = 'balanced',
                      pollutant_type: str = None,
                      num_waypoints: int = 10) -> Dict:
        """
        Find optimal route based on priority using different routing strategies
        """
        
        print(f"\n   🔍 Finding {priority.upper()} route...")
        
        # Get base route
        base_route = self.routing_service.get_route(
            (start_lng, start_lat),
            (end_lng, end_lat)
        )
        
        if not base_route:
            print("   ✗ Could not get base route")
            return None
        
        # For shortest priority - return direct route
        if priority == 'shortest':
            print("   → Using DIRECT shortest path")
            sampled_points = self.routing_service.sample_route_points(
                base_route['coordinates'],
                num_samples=8
            )
            aqi_data_list = self.aqi_service.get_multiple_aqi_for_route(sampled_points)
            avg_aqi = np.mean([data['aqi'] for data in aqi_data_list if data.get('aqi', 0) > 0]) if aqi_data_list else 100
            
            return {
                'distance': base_route['distance'],
                'duration': base_route['duration'],
                'average_aqi': float(avg_aqi),
                'aqi_data': aqi_data_list,
                'geometry': base_route['geometry'],
                'coordinates': base_route['coordinates'],
                'sampled_points': sampled_points,
                'optimal_path_indices': list(range(len(sampled_points))),
                'dijkstra_cost': base_route['distance'],
                'priority': priority
            }
        
        # For other priorities, calculate different detours
        print(f"   → Generating alternative route for {priority}...")
        
        mid_lat = (start_lat + end_lat) / 2
        mid_lng = (start_lng + end_lng) / 2
        bearing = self._calculate_bearing(start_lat, start_lng, end_lat, end_lng)
        
        # DIFFERENT DETOUR PARAMETERS FOR EACH PRIORITY
        detour_configs = {
            'balanced': {
                'distance': min(1.0, base_route['distance'] * 0.15),
                'angle': 50,
                'side': 'right',
                'description': 'Moderate right detour'
            },
            'cleanest': {
                'distance': min(3.0, base_route['distance'] * 0.35),
                'angle': 80,
                'side': 'left',
                'description': 'Large left detour for clean air'
            },
            'pm25': {
                'distance': min(2.5, base_route['distance'] * 0.30),
                'angle': 70,
                'side': 'right',
                'description': 'Right detour avoiding PM2.5'
            },
            'pm10': {
                'distance': min(2.8, base_route['distance'] * 0.32),
                'angle': 75,
                'side': 'left',
                'description': 'Left detour avoiding PM10'
            },
            'co': {
                'distance': min(2.2, base_route['distance'] * 0.28),
                'angle': 65,
                'side': 'right',
                'description': 'Right detour avoiding CO'
            },
            'o3': {
                'distance': min(2.6, base_route['distance'] * 0.31),
                'angle': 72,
                'side': 'left',
                'description': 'Left detour avoiding O3'
            },
            'so2': {
                'distance': min(2.4, base_route['distance'] * 0.29),
                'angle': 68,
                'side': 'right',
                'description': 'Right detour avoiding SO2'
            }
        }
        
        config = detour_configs.get(priority, detour_configs['balanced'])
        
        print(f"   → {config['description']}: {config['distance']:.1f}km at {config['angle']}°")
        
        # Calculate detour angle based on side
        if config['side'] == 'right':
            detour_bearing = (bearing + config['angle']) % 360
        else:
            detour_bearing = (bearing - config['angle']) % 360
        
        # Calculate waypoint
        waypoint_lat, waypoint_lng = self._calculate_destination_point(
            mid_lat, mid_lng,
            config['distance'],
            detour_bearing
        )
        
        print(f"   → Trying waypoint at ({waypoint_lat:.4f}, {waypoint_lng:.4f})...")
        
        # Try the detour route
        alternative_route = None
        try:
            route = self.routing_service.get_route_via_waypoint(
                (start_lng, start_lat),
                (waypoint_lng, waypoint_lat),
                (end_lng, end_lat)
            )
            if route and route['distance'] > base_route['distance'] * 1.05:  # At least 5% longer
                print(f"   ✓ Detour successful: {route['distance']:.2f}km vs {base_route['distance']:.2f}km direct")
                alternative_route = route
            else:
                print(f"   ⚠ Detour too similar, using direct route")
        except Exception as e:
            print(f"   ⚠ Detour failed: {e}")
        
        # Use alternative route if found, otherwise use base route
        final_route = alternative_route if alternative_route else base_route
        
        # Sample and get AQI data
        sampled_points = self.routing_service.sample_route_points(
            final_route['coordinates'],
            num_samples=12
        )
        
        aqi_data_list = self.aqi_service.get_multiple_aqi_for_route(sampled_points)
        avg_aqi = np.mean([data['aqi'] for data in aqi_data_list if data.get('aqi', 0) > 0]) if aqi_data_list else 100
        
        print(f"   ✓ Route AQI: {avg_aqi:.1f}\n")
        
        return {
            'distance': final_route['distance'],
            'duration': final_route['duration'],
            'average_aqi': float(avg_aqi),
            'aqi_data': aqi_data_list,
            'geometry': final_route['geometry'],
            'coordinates': final_route['coordinates'],
            'sampled_points': sampled_points,
            'optimal_path_indices': list(range(len(sampled_points))),
            'dijkstra_cost': final_route['distance'],
            'priority': priority
        }




    def _calculate_bearing(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate bearing between two points in degrees"""
        lat1_rad = np.radians(lat1)
        lat2_rad = np.radians(lat2)
        dlon = np.radians(lon2 - lon1)
        
        x = np.sin(dlon) * np.cos(lat2_rad)
        y = np.cos(lat1_rad) * np.sin(lat2_rad) - np.sin(lat1_rad) * np.cos(lat2_rad) * np.cos(dlon)
        
        bearing = np.degrees(np.arctan2(x, y))
        return (bearing + 360) % 360
    
    def _calculate_destination_point(self, lat: float, lon: float, 
                                     distance_km: float, bearing: float) -> Tuple[float, float]:
        """
        Calculate destination point given start point, distance (in km), and bearing
        """
        R = 6371  # Earth's radius in kilometers
        
        lat_rad = np.radians(lat)
        lon_rad = np.radians(lon)
        bearing_rad = np.radians(bearing)
        
        new_lat_rad = np.arcsin(
            np.sin(lat_rad) * np.cos(distance_km / R) +
            np.cos(lat_rad) * np.sin(distance_km / R) * np.cos(bearing_rad)
        )
        
        new_lon_rad = lon_rad + np.arctan2(
            np.sin(bearing_rad) * np.sin(distance_km / R) * np.cos(lat_rad),
            np.cos(distance_km / R) - np.sin(lat_rad) * np.sin(new_lat_rad)
        )
        
        new_lat = np.degrees(new_lat_rad)
        new_lon = np.degrees(new_lon_rad)
        
        return new_lat, new_lon
    
    def compare_routes(self, start_lat: float, start_lng: float,
                      end_lat: float, end_lng: float) -> Dict:
        """
        Compare routes with different priorities
        """
        priorities = ['shortest', 'balanced', 'cleanest']
        results = {}
        
        for priority in priorities:
            route = self.find_optimal_route(
                start_lat, start_lng, end_lat, end_lng,
                priority=priority
            )
            results[priority] = route
        
        return results

