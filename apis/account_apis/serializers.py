from django.contrib.auth import authenticate
from rest_framework import serializers
from accounts.models import User, Driver


class UserSerializer(serializers.ModelSerializer):
    password1 = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = (
            'id', 'avatar', 'full_name', 'email', 'country', 'phone_number', 'password1', 'password2')

    def validate(self, data):
        if data['password1'] != data['password2']:
            raise serializers.ValidationError("Passwords do not match.")
        return data

    def create(self, validated_data):
        user = User(
            avatar=validated_data['avatar'],
            full_name=validated_data['full_name'],
            email=validated_data['email'],
            country=validated_data['country'],
            phone_number=validated_data['phone_number']
        )
        user.set_password(validated_data['password1'])
        user.save()
        return user

    def get_avatar(self, obj):
        request = self.context.get('request')
        if obj.avatar:
            return request.build_absolute_uri(obj.avatar.url)
        return None

    def validate_email(self, value):
        if self.instance is None and User.objects.filter(email=value).exists():
            raise serializers.ValidationError('Email address already exists.')
        return value

class UserListSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'id', 'avatar', 'full_name', 'email', 'country', 'phone_number', 'password', 'is_active', 'is_staff',
            'is_superuser', 'is_driver',)


class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('avatar', 'full_name', 'email', 'country', 'phone_number')


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        user = authenticate(username=data['email'], password=data['password'])
        if user is None:
            raise serializers.ValidationError("Invalid credentials")
        return data


class LogoutSerializer(serializers.Serializer):
    pass


class DriverSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Driver
        fields = ('id', 'user', 'id_type', 'id_number', 'vehicle_plate_number', 'vehicle_type', 'vehicle_color', 'date_created', 'date_updated')

