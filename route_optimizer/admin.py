from django.contrib import admin
from .models import Location, RouteHistory

@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ['name', 'latitude', 'longitude', 'overall_aqi', 'last_updated']
    search_fields = ['name']
    list_filter = ['last_updated']
    ordering = ['-last_updated']

@admin.register(RouteHistory)
class RouteHistoryAdmin(admin.ModelAdmin):
    list_display = ['source_name', 'destination_name', 'priority', 'total_distance', 'average_aqi', 'created_at']
    list_filter = ['priority', 'created_at']
    search_fields = ['source_name', 'destination_name']
    ordering = ['-created_at']
    readonly_fields = ['created_at']
