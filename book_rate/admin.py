from django.contrib import admin
from .models import RideBooking, Rating

# Register your models here.

@admin.register(RideBooking)
class RideBookingAdmin(admin.ModelAdmin):
    list_display = ('id', 'passenger', 'ride', 'date_booked', 'qrcode_uuid')
    search_fields = ('passenger__full_name', 'ride__uuid')
    list_filter = ('date_booked',)
    readonly_fields = ('qrcode_uuid', 'qr_code')


@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    list_display = ('id', 'passenger', 'ride', 'score', 'impression_option', 'date_rated')
    search_fields = ('passenger__full_name', 'ride__uuid', 'comment')
    list_filter = ('score', 'impression_option', 'date_rated')
    readonly_fields = ('date_rated',)
