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
from django.http import JsonResponse
from rest_framework import generics, permissions
from user.models import Trip
from .models import Driver, Vehicle
from .serializers import DriverSerializer, VehicleSerializer, DriverRegistrationSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from user.serializers import TripSerializer

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

# driver/views.py

from django.http import JsonResponse
from django.views import View
from user.models import Trip
from django.shortcuts import render
from django.http import JsonResponse
from django.views import View
from user.models import Trip


class RequestedTripsView(View):
    def get(self, request):
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            requested_trips = Trip.objects.filter(status='REQUESTED').values(
                'id',
                'origin',
                'destination',
                'user__name',
                'driver__user__name',
                'status',
                'payment_status',
                'price',
                'created_at'
            )
            trips_list = list(requested_trips)
            return JsonResponse({'trips': trips_list})
        else:
            return render(request, 'driver/requested_trips.html')

class DriverProfileView(generics.RetrieveUpdateAPIView):
    queryset = Driver.objects.all()
    serializer_class = DriverSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user.driver

class VehicleProfileView(generics.RetrieveUpdateAPIView):
    queryset = Vehicle.objects.all()
    serializer_class = VehicleSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user.driver.vehicle_set.first()

class DriverAcceptedTripsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        trips = Trip.objects.filter(driver=request.user.driver, status='ACCEPTED')
        serializer = TripSerializer(trips, many=True)
        return Response(serializer.data)


def driver_profile(request):
    return render(request, 'driver/profile.html')



