from rest_framework import serializers
from book_rate.models import RideBooking
from apis.account_apis.serializers import UserSerializer
from apis.ride_apis.serializers import RideDetailSerializer
from rides.models import Ride

class RideBookingSerializer(serializers.ModelSerializer):
    passenger = UserSerializer(read_only=True)
    ride = serializers.PrimaryKeyRelatedField(queryset=Ride.objects.all())  # Accept ride ID in input

    class Meta:
        model = RideBooking
        fields = [
            'id',
            'passenger',
            'ride',
            'qrcode_uuid',
            'qr_code',
            'date_booked',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'qrcode_uuid', 'date_booked', 'created_at', 'updated_at']


class RideBookingDetailSerializer(serializers.ModelSerializer):
    passenger = UserSerializer(read_only=True)
    ride = RideDetailSerializer(read_only=True)

    class Meta:
        model = RideBooking
        fields = [
            'id',
            'passenger',
            'ride',
            'qrcode_uuid',
            'qr_code',
            'date_booked',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'qrcode_uuid', 'date_booked', 'created_at', 'updated_at']