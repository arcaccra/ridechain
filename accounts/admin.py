from django.contrib import admin
from .models import Driver, User


class DriverAdmin(admin.ModelAdmin):
    list_display = ('user', 'vehicle_plate_number', 'approved')
    search_fields = ('vehicle_plate_number', 'user__email', 'user__full_name')
    ordering = ('-date_created',)



admin.site.register(User)
admin.site.register(Driver, DriverAdmin)