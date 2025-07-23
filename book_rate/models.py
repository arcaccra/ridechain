from django.db import models
from accounts.models import User
from rides.models import Ride
import uuid


# Create your models here.

class BaseModel(models.Model):
    """
    Abstract base model to add common fields to all models.
    """
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class RideBooking(BaseModel):
    """
    Model to represent a ride booking.
    """
    passenger = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings')
    ride = models.ForeignKey(Ride, on_delete=models.CASCADE, related_name='bookings')
    qrcode_uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    qr_code = models.ImageField(upload_to='qr_codes/', blank=True, null=True)
    date_booked = models.DateTimeField(auto_now_add=True)



    class Meta:
        verbose_name = 'Ride Booking'
        verbose_name_plural = 'Ride Bookings'
        ordering = ['-date_booked']
        unique_together = ('passenger', 'ride')

    def __str__(self):
        return f"Booking {self.id} by {self.passenger.full_name} for Ride {self.ride.uuid}"