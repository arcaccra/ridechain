from django.db import models
from accounts.models import Driver, User
import uuid
import secrets

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
    passenger = models.ForeignKey(User, on_delete=models.CASCADE, related_name='rides', verbose_name='passenger', null=True, blank=True)
    departure_location = models.CharField(max_length=255)
    destination = models.CharField(max_length=255)
    departure_time = models.DateTimeField()
    arrival_time = models.DateTimeField(null=True, blank=True)
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
        return f"Ride {self.id} by {self.driver.user.full_name} from {self.departure_location} to {self.destination}"