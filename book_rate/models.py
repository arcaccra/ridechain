from django.db import models
from accounts.models import User
from rides.models import Ride
import uuid
from utilities.options import IMPRESSION_OPTIONS


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


class Rating(BaseModel):
    """
    Model to represent a rating given by a passenger to a ride.
    """
    passenger = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ratings')
    ride = models.ForeignKey(Ride, on_delete=models.CASCADE, related_name='ratings')
    score = models.PositiveSmallIntegerField()
    impression_option = models.CharField(max_length=20, blank=True, null=True, choices=IMPRESSION_OPTIONS)
    comment = models.TextField(blank=True, null=True)
    date_rated = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Rating'
        verbose_name_plural = 'Ratings'
        ordering = ['-date_rated']
        unique_together = ('passenger', 'ride')

    def __str__(self):
        return f"Rating {self.score} by {self.passenger.full_name} for Ride {self.ride.uuid}"