from django.contrib import admin
from .models import Driver, User, Subscriber


class DriverAdmin(admin.ModelAdmin):
    list_display = ('user', 'vehicle_plate_number', 'approved')
    search_fields = ('vehicle_plate_number', 'user__email', 'user__full_name')
    ordering = ('-date_created',)


class SubscriberAdmin(admin.ModelAdmin):
    list_display = ('email', 'name', 'accepted_mailing', 'create_date')
    search_fields = ('email', 'name')
    ordering = ('-create_date',)



admin.site.register(User)
admin.site.register(Subscriber, SubscriberAdmin)
admin.site.register(Driver, DriverAdmin)