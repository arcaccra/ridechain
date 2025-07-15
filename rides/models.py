from django.db import models
from accounts.models import Driver, User
import uuid

class Ride(models.Model):
    """
    Represents a ride offered by a driver.
    """
    STATUS_CHOICES = (
        ('UPCOMING', 'Upcoming'),
        ('IN_PROGRESS', 'In Progress'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
    )
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)  # Set default
    driver = models.ForeignKey(Driver, on_delete=models.CASCADE, related_name='rides', verbose_name='driver')
    passengers = models.ManyToManyField(User, related_name='rides', blank=True, verbose_name='passengers')
    pick_up = models.DecimalField(max_digits=10, decimal_places=6, verbose_name='pick-up location', blank=True, null=True)
    drop_off = models.DecimalField(max_digits=10, decimal_places=6, verbose_name='drop-off location', blank=True, null=True)
    departure_time = models.DateTimeField(null=True, blank=True, verbose_name='departure time')
    arrival_time = models.DateTimeField(blank=True, null=True , verbose_name='arrival time')
    seats_available = models.PositiveIntegerField(default=1)
    price_per_seat = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='UPCOMING')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Ride'
        verbose_name_plural = 'Rides'
        ordering = ['-created_at']

    def __str__(self):
        return f"Ride {self.uuid} by {self.driver.user.full_name} from {self.pick_up} to {self.drop_off}"