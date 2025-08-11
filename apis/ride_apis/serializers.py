from django.db.models import Model

from rides.models import Ride, Location
from rest_framework import serializers
from apis.account_apis.serializers import UserSerializer, DriverSerializer


class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = ['id', 'name', 'latitude', 'longitude']
        read_only_fields = ['latitude', 'longitude']

class RideListSerializer(serializers.ModelSerializer):
    driver = DriverSerializer(read_only=True)
    pick_up = serializers.PrimaryKeyRelatedField(queryset=Location.objects.all())
    drop_off = serializers.PrimaryKeyRelatedField(queryset=Location.objects.all())

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
    pick_up = LocationSerializer(read_only=True)
    drop_off = LocationSerializer(read_only=True)

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


class RideUpdateSerializer(serializers.ModelSerializer):
    pick_up = serializers.PrimaryKeyRelatedField(queryset=Location.objects.all(), required=False)
    drop_off = serializers.PrimaryKeyRelatedField(queryset=Location.objects.all(), required=False)
    driver = DriverSerializer(read_only=True)
    passengers = UserSerializer(many=True)

    class Meta:
        model = Ride
        fields = [
            'uuid',
            'driver',
            'passengers',
            'pick_up',
            'drop_off',
            'seats_available',
            'price_per_seat',
            'departure_time',
            'arrival_time',
            'status',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['uuid', 'created_at', 'updated_at']
