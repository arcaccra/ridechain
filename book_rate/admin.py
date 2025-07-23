from django.contrib import admin
from .models import RideBooking

# Register your models here.

@admin.register(RideBooking)
class RideBookingAdmin(admin.ModelAdmin):
    list_display = ('id', 'passenger', 'ride', 'date_booked', 'qrcode_uuid')
    search_fields = ('passenger__full_name', 'ride__uuid')
    list_filter = ('date_booked',)
    readonly_fields = ('qrcode_uuid', 'qr_code')
