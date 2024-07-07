# user/views.py
from django.shortcuts import render
from django.views import View
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.views import APIView
from django.contrib.auth import authenticate
from django.conf import settings
import requests
import logging

from .models import User, Trip
from .serializers import UserSerializer, LoginSerializer, TripSerializer, UserProfileSerializer, TripDetailSerializer


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]


class JWTLoginView(generics.GenericAPIView):
    serializer_class = LoginSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = authenticate(
            phone_number=serializer.validated_data['phone_number'],
            password=serializer.validated_data['password']
        )
        if user is not None:
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Invalid Credentials'}, status=status.HTTP_401_UNAUTHORIZED)


class UserRegisterView(View):
    def get(self, request):
        return render(request, 'user/register.html')


class UserLoginFormView(View):
    def get(self, request):
        return render(request, 'user/login.html')

from django.shortcuts import render
from django.views import View
from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.conf import settings
from rest_framework.views import APIView
import requests
import logging

from .models import User, Trip
from .serializers import UserSerializer, LoginSerializer, TripSerializer
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

def send_trip_update(trip_data):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        'trips',
        {
            'type': 'send_trip_update',
            'text': trip_data
        }
    )

class TripCreateView(generics.CreateAPIView):
    queryset = Trip.objects.all()
    serializer_class = TripSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        trip = serializer.save(user=self.request.user, status='REQUESTED', payment_status='PENDING')
        trip_data = {
            'id': trip.id,
            'origin': trip.origin,
            'destination': trip.destination,
            'user_name': trip.user.name,
            'driver_name': trip.driver.name if trip.driver else 'N/A',
            'status': trip.get_status_display(),
            'payment_status': trip.get_payment_status_display(),
            'price': trip.price,
            'created_at': trip.created_at.strftime('%Y-%m-%d %H:%M:%S'),
        }
        send_trip_update(trip_data)

class TripDetailView(generics.RetrieveUpdateAPIView):
    queryset = Trip.objects.all()
    serializer_class = TripSerializer
    permission_classes = [IsAuthenticated]

    def put(self, request, *args, **kwargs):
        trip = self.get_object()
        if 'status' in request.data and request.data['status'] == 'ACCEPTED' and trip.driver is None:
            trip.driver = request.user.driver  # assuming request.user is the driver
        serializer = self.get_serializer(trip, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class UserTripListView(generics.ListAPIView):
    serializer_class = TripSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Trip.objects.filter(user=self.request.user)


class DriverTripListView(generics.ListAPIView):
    serializer_class = TripSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Trip.objects.filter(driver=self.request.user.driver)


class TripRequestView(View):
    def get(self, request):
        return render(request, 'user/request_trip.html')


import logging
import requests
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.conf import settings

class RouteInfoView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        print(request, '1111111111111111111111111')
        origin = request.query_params.get('origin')
        destination = request.query_params.get('destination')
        
        OPENROUTESERVICE_API_KEY = '5b3ce3597851110001cf6248c991167e200a4dd5a694a7d747707b1a'
        if not origin or not destination:
            return Response({'error': 'Origin and destination are required.'}, status=status.HTTP_400_BAD_REQUEST)
        
        api_key = OPENROUTESERVICE_API_KEY
        url = 'https://api.openrouteservice.org/v2/directions/driving-car'
        params = {
            'api_key': api_key,
            'start': origin,
            'end': destination
        }

        response = requests.get(url, params=params)
        data = response.json()
        
        if response.status_code == 403:
            logging.error(f'Forbidden error: {data}')
            return Response({'error': 'Access to the OpenRouteService API has been disallowed. Please check your API key permissions.'}, status=status.HTTP_403_FORBIDDEN)
        
        if response.status_code != 200:
            logging.error(f'Error fetching route information: {data}')
            return Response({'error': 'Error fetching route information.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        if 'features' not in data or not data['features']:
            logging.error(f'Unexpected API response structure: {data}')
            return Response({'error': 'Error fetching route information. Invalid response structure.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        try:
            route = data['features'][0]['properties']['segments'][0]
            distance = route['distance'] / 1000  # Convert to km
            duration = route['duration'] / 60    # Convert to minutes
            
            # Pricing model
            base_fare = 2.50
            distance_charge = 1.00 * distance
            time_charge = 0.25 * duration
            total_fare = base_fare + distance_charge + time_charge
            
            return Response({
                'distance': distance,
                'duration': duration,
                'fare': total_fare,
            })
        except (IndexError, KeyError) as e:
            logging.error(f'Error processing route information: {e}, response data: {data}')
            return Response({'error': 'Error processing route information.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class UserProfileView(generics.RetrieveUpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user

class UserTripsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        trips = Trip.objects.filter(user=request.user)
        serializer = TripDetailSerializer(trips, many=True)
        return Response(serializer.data)

class UserProfileTemplateView(View):
    def get(self, request):
        return render(request, 'user/profile.html')

