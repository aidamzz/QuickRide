# user/views.py
import logging
from django.shortcuts import render
from django.views import View
from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.views import APIView
from django.contrib.auth import authenticate
import requests
from .models import User, Trip
from django.conf import settings
from .serializers import (
    UserSerializer, 
    LoginSerializer, 
    TripSerializer, 
    UserProfileSerializer, 
    TripDetailSerializer
)
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync


# Configure logging
logger = logging.getLogger(__name__)
class RegisterView(generics.CreateAPIView):
    """
    View for user registration. Uses UserSerializer for validation and creation.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        # Validate and save the user data
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        access = refresh.access_token

        # Return user data along with the JWT tokens
        return Response({
            'user': UserSerializer(user).data,
            'refresh': str(refresh),
            'access': str(access),
        }, status=status.HTTP_201_CREATED)

class JWTLoginView(generics.GenericAPIView):
    """
    View for user login using JWT tokens. Uses LoginSerializer for validation.
    """
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
            logger.warning("Invalid login attempt for phone number: %s", serializer.validated_data['phone_number'])
            return Response({'error': 'Invalid Credentials'}, status=status.HTTP_401_UNAUTHORIZED)

class UserRegisterView(View):
    """
    View for rendering user registration template.
    """
    def get(self, request):
        return render(request, 'user/register.html')

class UserLoginFormView(View):
    """
    View for rendering user login template.
    """
    def get(self, request):
        return render(request, 'user/login.html')

class TripCreateView(generics.CreateAPIView):
    """
    View for creating a new trip. Uses TripSerializer for validation and creation.
    """
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
            'price': float(trip.price),  # Convert Decimal to float
            'created_at': trip.created_at.strftime('%Y-%m-%d %H:%M:%S'),
        }
        send_trip_update(trip_data)

class TripDetailView(generics.RetrieveUpdateAPIView):
    """
    View for retrieving and updating trip details. Uses TripSerializer for validation.
    """
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
    """
    View for listing all trips associated with the authenticated user.
    """
    serializer_class = TripSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Trip.objects.filter(user=self.request.user)

class DriverTripListView(generics.ListAPIView):
    """
    View for listing all trips associated with the authenticated driver.
    """
    serializer_class = TripSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Trip.objects.filter(driver=self.request.user.driver)

class TripRequestView(View):
    """
    View for rendering trip request template.
    """
    def get(self, request):
        return render(request, 'user/request_trip.html')

from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
import requests
import logging

logger = logging.getLogger(__name__)

class RouteInfoView(APIView):
    """
    View for fetching route information using the OpenRouteService API.
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        origin = request.query_params.get('origin')
        destination = request.query_params.get('destination')

        if not origin or not destination:
            return Response({'error': 'Origin and destination are required.'}, status=status.HTTP_400_BAD_REQUEST)
        
        api_key = '5b3ce3597851110001cf6248f3302b270ec94f7286a9bdde2335bc24'
        url = 'https://api.openrouteservice.org/v2/directions/driving-car'
        params = {
            'api_key': api_key,
            'start': origin,
            'end': destination
        }

        response = requests.get(url, params=params)
        data = response.json()
        
        if response.status_code == 403:
            logger.error(f'Forbidden error: {data}')
            return Response({'error': 'Access to the OpenRouteService API has been disallowed. Please check your API key permissions.'}, status=status.HTTP_403_FORBIDDEN)
        
        if response.status_code != 200:
            logger.error(f'Error fetching route information: {data}')
            return Response({'error': 'Error fetching route information.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        if 'features' not in data or not data['features']:
            logger.error(f'Unexpected API response structure: {data}')
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
            logger.error(f'Error processing route information: {e}, response data: {data}')
            return Response({'error': 'Error processing route information.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UserProfileView(generics.RetrieveUpdateAPIView):
    """
    View for retrieving and updating the authenticated user's profile.
    """
    queryset = User.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user

class UserTripsView(APIView):
    """
    View for listing all trips of the authenticated user.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        trips = Trip.objects.filter(user=request.user)
        serializer = TripDetailSerializer(trips, many=True)
        return Response(serializer.data)

class UserProfileTemplateView(View):
    """
    View for rendering user profile template.
    """
    def get(self, request):
        return render(request, 'user/profile.html')

def send_trip_update(trip_data):
    """
    Helper function to send trip updates via Django Channels.
    """
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        'trips',
        {
            'type': 'send_trip_update',
            'text': trip_data
        }
    )
