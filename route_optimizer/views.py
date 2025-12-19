from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
import traceback
import logging
from .services.dijkstra_optimizer import DijkstraOptimizer
from .services.routing_service import RoutingService
from .services.air_quality_service import AirQualityService
from .models import RouteHistory, Location

# Set up logging
logger = logging.getLogger(__name__)


def index(request):
    """Main page"""
    return render(request, 'route_optimizer/index.html')


@csrf_exempt
@require_http_methods(["POST"])
def find_route(request):
    """
    API endpoint to find optimal route
    """
    try:
        # Parse request data
        data = json.loads(request.body)
        
        # Extract parameters
        source_address = data.get('source_address')
        dest_address = data.get('destination_address')
        source_lat = data.get('source_lat')
        source_lng = data.get('source_lng')
        dest_lat = data.get('dest_lat')
        dest_lng = data.get('dest_lng')
        priority = data.get('priority', 'balanced')
        pollutant_type = data.get('pollutant_type')
        
        print(f"\n{'='*60}")
        print(f"🔍 ROUTE REQUEST")
        print(f"{'='*60}")
        print(f"Source Address: {source_address}")
        print(f"Destination Address: {dest_address}")
        print(f"Priority: {priority}")
        print(f"Pollutant Type: {pollutant_type}")
        
        # Initialize services
        routing_service = RoutingService()
        optimizer = DijkstraOptimizer()
        
        # Geocode addresses if coordinates not provided
        if not (source_lat and source_lng) and source_address:
            print(f"\n📍 Geocoding source: {source_address}")
            source_coords = routing_service.geocode_address(f"{source_address}, Kolkata")
            if source_coords:
                source_lng, source_lat = source_coords  # Returns (lng, lat)
                print(f"   ✓ Source coords: ({source_lat}, {source_lng})")
            else:
                print(f"   ✗ Failed to geocode source")
                return JsonResponse({
                    'success': False,
                    'error': f'Could not geocode source address: {source_address}'
                }, status=400)
        
        if not (dest_lat and dest_lng) and dest_address:
            print(f"\n📍 Geocoding destination: {dest_address}")
            dest_coords = routing_service.geocode_address(f"{dest_address}, Kolkata")
            if dest_coords:
                dest_lng, dest_lat = dest_coords  # Returns (lng, lat)
                print(f"   ✓ Destination coords: ({dest_lat}, {dest_lng})")
            else:
                print(f"   ✗ Failed to geocode destination")
                return JsonResponse({
                    'success': False,
                    'error': f'Could not geocode destination address: {dest_address}'
                }, status=400)
        
        # Validate coordinates
        if not all([source_lat, source_lng, dest_lat, dest_lng]):
            print(f"\n✗ Invalid coordinates:")
            print(f"   Source: ({source_lat}, {source_lng})")
            print(f"   Destination: ({dest_lat}, {dest_lng})")
            return JsonResponse({
                'success': False,
                'error': 'Invalid coordinates or addresses. Please provide valid locations.'
            }, status=400)
        
        # Convert to float
        source_lat = float(source_lat)
        source_lng = float(source_lng)
        dest_lat = float(dest_lat)
        dest_lng = float(dest_lng)
        
        print(f"\n🚗 Finding optimal route...")
        print(f"   From: ({source_lat}, {source_lng})")
        print(f"   To: ({dest_lat}, {dest_lng})")
        print(f"   Priority: {priority}")
        
        # Find optimal route
        route_result = optimizer.find_optimal_route(
            source_lat, source_lng,
            dest_lat, dest_lng,
            priority=priority,
            pollutant_type=pollutant_type
        )
        
        if not route_result:
            print(f"\n✗ Could not find route")
            return JsonResponse({
                'success': False,
                'error': 'Could not find route. Please try different locations.'
            }, status=400)
        
        print(f"\n✓ Route found!")
        print(f"   Distance: {route_result['distance']} km")
        print(f"   Duration: {route_result['duration']} min")
        print(f"   Average AQI: {route_result['average_aqi']}")
        
        # Reverse geocode for names (with fallback)
        try:
            source_name = routing_service.reverse_geocode(source_lng, source_lat) or source_address or "Source"
            dest_name = routing_service.reverse_geocode(dest_lng, dest_lat) or dest_address or "Destination"
            print(f"\n📝 Location names:")
            print(f"   Source: {source_name}")
            print(f"   Destination: {dest_name}")
        except Exception as e:
            print(f"\n⚠️ Warning: Could not reverse geocode: {e}")
            source_name = source_address or "Source"
            dest_name = dest_address or "Destination"
        
        # Save to history
        try:
            RouteHistory.objects.create(
                source_name=source_name,
                source_lat=source_lat,
                source_lng=source_lng,
                destination_name=dest_name,
                destination_lat=dest_lat,
                destination_lng=dest_lng,
                priority=priority,
                total_distance=route_result['distance'],
                estimated_time=route_result['duration'],
                average_aqi=route_result['average_aqi'],
                route_geometry=route_result['geometry']
            )
            print(f"✓ Saved to history")
        except Exception as e:
            print(f"⚠️ Warning: Could not save to history: {e}")
            # Don't fail the request if history save fails
        
        print(f"{'='*60}\n")
        
        # Return response
        return JsonResponse({
            'success': True,
            'route': {
                'source': {
                    'lat': source_lat, 
                    'lng': source_lng, 
                    'name': source_name
                },
                'destination': {
                    'lat': dest_lat, 
                    'lng': dest_lng, 
                    'name': dest_name
                },
                'distance': round(route_result['distance'], 2),
                'duration': round(route_result['duration'], 2),
                'average_aqi': round(route_result['average_aqi'], 2),
                'geometry': route_result['geometry'],
                'coordinates': route_result['coordinates'],
                'aqi_data': route_result['aqi_data'],
                'priority': priority
            }
        })
        
    except json.JSONDecodeError as e:
        print(f"\n✗ JSON Parse Error: {e}")
        logger.error(f"JSON decode error: {e}")
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON in request body'
        }, status=400)
        
    except ValueError as e:
        print(f"\n✗ Value Error: {e}")
        logger.error(f"Value error: {e}")
        logger.error(traceback.format_exc())
        return JsonResponse({
            'success': False,
            'error': f'Invalid data format: {str(e)}'
        }, status=400)
        
    except Exception as e:
        print(f"\n{'='*60}")
        print(f"💥 UNEXPECTED ERROR")
        print(f"{'='*60}")
        print(f"Error: {str(e)}")
        print(f"\nFull Traceback:")
        print(traceback.format_exc())
        print(f"{'='*60}\n")
        
        logger.error(f"Unexpected error in find_route: {str(e)}")
        logger.error(traceback.format_exc())
        
        return JsonResponse({
            'success': False,
            'error': str(e),
            'type': type(e).__name__,
            'traceback': traceback.format_exc().split('\n')  # Include traceback in development
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def compare_routes(request):
    """
    API endpoint to compare routes with different priorities
    """
    try:
        data = json.loads(request.body)
        
        source_lat = float(data.get('source_lat'))
        source_lng = float(data.get('source_lng'))
        dest_lat = float(data.get('dest_lat'))
        dest_lng = float(data.get('dest_lng'))
        
        print(f"\n{'='*60}")
        print(f"🔄 COMPARING ROUTES")
        print(f"{'='*60}")
        print(f"From: ({source_lat}, {source_lng})")
        print(f"To: ({dest_lat}, {dest_lng})")
        
        optimizer = DijkstraOptimizer()
        comparison = optimizer.compare_routes(
            source_lat, source_lng, dest_lat, dest_lng
        )
        
        print(f"✓ Comparison complete")
        print(f"{'='*60}\n")
        
        return JsonResponse({
            'success': True,
            'comparison': comparison
        })
        
    except Exception as e:
        print(f"\n💥 Error comparing routes: {e}")
        print(traceback.format_exc())
        
        logger.error(f"Error comparing routes: {str(e)}")
        logger.error(traceback.format_exc())
        
        return JsonResponse({
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc().split('\n')
        }, status=500)


@require_http_methods(["GET"])
def get_history(request):
    """
    Get route history
    """
    try:
        history = RouteHistory.objects.all().order_by('-created_at')[:20]
        
        data = [{
            'id': h.id,
            'source': h.source_name,
            'destination': h.destination_name,
            'distance': h.total_distance,
            'duration': h.estimated_time,
            'average_aqi': h.average_aqi,
            'priority': h.priority,
            'created_at': h.created_at.isoformat()
        } for h in history]
        
        return JsonResponse({'success': True, 'history': data})
        
    except Exception as e:
        logger.error(f"Error fetching history: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def get_aqi(request):
    """
    Get AQI for specific location
    """
    try:
        data = json.loads(request.body)
        lat = float(data.get('lat'))
        lng = float(data.get('lng'))
        
        print(f"\n🌍 Fetching AQI for ({lat}, {lng})")
        
        aqi_service = AirQualityService()
        aqi_data = aqi_service.get_aqi_by_coordinates(lat, lng)
        
        if aqi_data:
            print(f"✓ AQI: {aqi_data.get('aqi', 'N/A')}")
            return JsonResponse({
                'success': True,
                'aqi_data': aqi_data
            })
        else:
            print(f"✗ Could not fetch AQI data")
            return JsonResponse({
                'success': False,
                'error': 'Could not fetch AQI data for this location'
            }, status=400)
            
    except Exception as e:
        print(f"💥 Error fetching AQI: {e}")
        logger.error(f"Error fetching AQI: {str(e)}")
        logger.error(traceback.format_exc())
        
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)
