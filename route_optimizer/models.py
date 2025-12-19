from django.db import models
from django.contrib.auth.models import User

class Location(models.Model):
    name = models.CharField(max_length=200)
    latitude = models.FloatField()
    longitude = models.FloatField()
    aqi_pm25 = models.FloatField(null=True, blank=True)
    aqi_pm10 = models.FloatField(null=True, blank=True)
    aqi_no2 = models.FloatField(null=True, blank=True)
    aqi_co = models.FloatField(null=True, blank=True)
    aqi_o3 = models.FloatField(null=True, blank=True)
    overall_aqi = models.FloatField(null=True, blank=True)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']


class RouteHistory(models.Model):
    PRIORITY_CHOICES = [
        ('shortest', 'Shortest Distance'),
        ('cleanest', 'Cleanest Air'),
        ('balanced', 'Balanced'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    source_name = models.CharField(max_length=200)
    source_lat = models.FloatField()
    source_lng = models.FloatField()
    destination_name = models.CharField(max_length=200)
    destination_lat = models.FloatField()
    destination_lng = models.FloatField()
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='balanced')
    total_distance = models.FloatField()
    estimated_time = models.FloatField()
    average_aqi = models.FloatField()
    route_geometry = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.source_name} to {self.destination_name} ({self.created_at})"

    class Meta:
        ordering = ['-created_at']
