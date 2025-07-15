from rides.models import Ride
from rest_framework import serializers
from apis.account_apis.serializers import UserSerializer, DriverSerializer
from accounts.models import Driver, User

class RideListSerializer(serializers.ModelSerializer):
    driver = DriverSerializer(read_only=True)

    class Meta:
        model = Ride
        fields = [
            'uuid',
            'driver',
            'pick_up',
            'drop_off',
            'seats_available',
            'price_per_seat',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['uuid', 'created_at', 'updated_at']


class RideDetailSerializer(serializers.ModelSerializer):
    driver = DriverSerializer(read_only=True)
    passengers = UserSerializer(many=True, read_only=True)

    class Meta:
        model = Ride
        fields = [
            'uuid',
            'driver',
            'passengers',
            'pick_up',
            'drop_off',
            'departure_time',
            'arrival_time',
            'seats_available',
            'price_per_seat',
            'status',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['uuid', 'created_at', 'updated_at']

