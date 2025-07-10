from django.contrib import admin
from .models import Ride

@admin.register(Ride)
class RideAdmin(admin.ModelAdmin):
    list_display = ('uuid', 'driver', 'passenger', 'departure_location', 'destination', 'departure_time', 'status', 'seats_available')
    list_filter = ('status', 'driver', 'departure_time')
    search_fields = ('uuid', 'driver__user__full_name', 'passenger__user__full_name', 'departure_location', 'destination')
    readonly_fields = ('uuid', 'created_at', 'updated_at')
