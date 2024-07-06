# driver/serializers.py
from rest_framework import serializers
from user.models import User
from .models import Driver, Vehicle

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['name', 'phone_number', 'password']
        extra_kwargs = {'password': {'write_only': True}}

class DriverSerializer(serializers.ModelSerializer):
    class Meta:
        model = Driver
        fields = ['phone_number']

class VehicleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vehicle
        fields = ['model', 'number']

class DriverRegistrationSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=100)
    phone_number = serializers.CharField(max_length=20)
    password = serializers.CharField(write_only=True)
    vehicle_model = serializers.CharField(max_length=255)
    vehicle_number = serializers.CharField(max_length=20)

    def create(self, validated_data):
        user = User.objects.create(
            name=validated_data['name'],
            phone_number=validated_data['phone_number']
        )
        user.set_password(validated_data['password'])
        user.save()

        driver = Driver.objects.create(
            user=user,
            phone_number=validated_data['phone_number']
        )

        vehicle = Vehicle.objects.create(
            driver=driver,
            model=validated_data['vehicle_model'],
            number=validated_data['vehicle_number']
        )

        return driver
