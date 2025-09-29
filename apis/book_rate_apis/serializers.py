from rest_framework import serializers
from book_rate.models import RideBooking, Rating
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
    ride_id = serializers.PrimaryKeyRelatedField(source='ride', read_only=True)

    class Meta:
        model = RideBooking
        fields = [
            'id',
            'passenger',
            'ride',
            'ride_id',
            'qrcode_uuid',
            'qr_code',
            'date_booked',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'qrcode_uuid', 'date_booked', 'created_at', 'updated_at']

    def create(self, validated_data):
        passenger = self.context['request'].user
        ride = validated_data['ride']

        # Prevent duplicate bookings
        if RideBooking.objects.filter(passenger=passenger, ride=ride).exists():
            raise serializers.ValidationError("You have already booked this ride.")

        # Create the booking instance
        booking = RideBooking.objects.create(passenger=passenger, ride=ride)
        return booking


class RatingSerializer(serializers.ModelSerializer):
    passenger = UserSerializer(read_only=True)
    ride = serializers.PrimaryKeyRelatedField(queryset=Ride.objects.all())  # Accept ride ID in input

    class Meta:
        model = Rating
        fields = [
            'id',
            'passenger',
            'ride',
            'score',
            'impression_option',
            'comment',
            'date_rated',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'date_rated', 'created_at', 'updated_at']


