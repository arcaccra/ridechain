from django.contrib import admin
from .models import Ride, Location

@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ('name', 'latitude', 'longitude')
    search_fields = ('name',)
    readonly_fields = ('created_at', 'updated_at')
    list_filter = ('created_at',)

@admin.register(Ride)
class RideAdmin(admin.ModelAdmin):
    list_display = ('uuid', 'driver' , 'pick_up', 'drop_off', 'departure_time', 'status', 'seats_available')
    list_filter = ('status', 'driver', 'departure_time')
    search_fields = ('uuid', 'driver__user__full_name', 'driver__vehicle_plate_number', 'pick_up', 'drop_off')
    readonly_fields = ('uuid', 'created_at', 'updated_at')
