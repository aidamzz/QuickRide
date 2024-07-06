# user/serializers.py

from rest_framework import serializers
from .models import User, Trip

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'name', 'phone_number', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User(
            phone_number=validated_data['phone_number'],
            name=validated_data['name']
        )
        user.set_password(validated_data['password'])
        user.save()
        return user

class LoginSerializer(serializers.Serializer):
    phone_number = serializers.CharField()
    password = serializers.CharField()

class TripSerializer(serializers.ModelSerializer):
    class Meta:
        model = Trip
        fields = ['id', 'user', 'driver', 'origin', 'destination', 'price', 'status', 'payment_status', 'created_at', 'updated_at']
        read_only_fields = ['id', 'user', 'status', 'payment_status', 'created_at', 'updated_at']

    def create(self, validated_data):
        # Convert price to a string to ensure proper handling
        if 'price' in validated_data:
            validated_data['price'] = str(validated_data['price'])
        
        return Trip.objects.create(**validated_data)
