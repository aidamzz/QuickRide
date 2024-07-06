# driver/views.py
from django.shortcuts import render
from django.views import View
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import DriverRegistrationSerializer, UserSerializer, DriverSerializer, VehicleSerializer
from user.models import User, Trip
from .models import Driver, Vehicle
from django.contrib.auth import authenticate, login

class DriverRegistrationView(generics.GenericAPIView):
    serializer_class = DriverRegistrationSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        driver = serializer.save()
        user = driver.user
        refresh = RefreshToken.for_user(user)
        return Response({
            'user': UserSerializer(user).data,
            'driver': DriverSerializer(driver).data,
            'vehicle': VehicleSerializer(driver.vehicle_set.first()).data,
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }, status=status.HTTP_201_CREATED)

class DriverLoginView(generics.GenericAPIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        phone_number = request.data.get('phone_number')
        password = request.data.get('password')
        user = authenticate(phone_number=phone_number, password=password)
        if user is not None:
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }, status=status.HTTP_200_OK)
        return Response({'error': 'Invalid Credentials'}, status=status.HTTP_401_UNAUTHORIZED)

class DriverRegistrationTemplateView(View):
    def get(self, request):
        return render(request, 'driver/register_driver.html')

class DriverLoginTemplateView(View):
    def get(self, request):
        return render(request, 'driver/login_driver.html')

class RequestedTripsView(View):
    def get(self, request):
        requested_trips = Trip.objects.filter(status='REQUESTED')
        return render(request, 'driver/requested_trips.html', {'trips': requested_trips})
