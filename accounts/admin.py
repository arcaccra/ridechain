from django.contrib import admin
from .models import Driver, User

class UserAdmin(admin.ModelAdmin):
    list_display = ('email', 'full_name', 'is_driver', 'is_active', 'date_joined')
    search_fields = ('email', 'full_name')
    ordering = ('-date_joined',)

class DriverAdmin(admin.ModelAdmin):
    list_display = ('user', 'vehicle_plate_number', 'approved')
    search_fields = ('vehicle_plate_number', 'user__email', 'user__full_name')
    ordering = ('-date_created',)



admin.site.register(User, UserAdmin)
admin.site.register(Driver, DriverAdmin)