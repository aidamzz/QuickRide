# user/urls.py

from django.urls import path
from .views import UserRegisterView, UserProfileView, UserTripsView, UserProfileTemplateView, RegisterView, JWTLoginView, TripCreateView, TripDetailView, UserTripListView, DriverTripListView, TripRequestView, RouteInfoView, UserLoginFormView

urlpatterns = [
    path('register/', UserRegisterView.as_view(), name='register'),
    path('login/', JWTLoginView.as_view(), name='login'),  # Use the custom JWT login view
    path('api/register/', RegisterView.as_view(), name='api_register'),
    path('login-form/', UserLoginFormView.as_view(), name='login-form'),  # Use the form view for rendering the login form
    path('trips/', TripCreateView.as_view(), name='trip-create'),
    path('trips/<int:pk>/', TripDetailView.as_view(), name='trip-detail'),
    path('user-trips/', UserTripListView.as_view(), name='user-trips'),
    path('driver-trips/', DriverTripListView.as_view(), name='driver-trips'),
    path('request-trip/', TripRequestView.as_view(), name='request-trip'),
    path('api/route-info/', RouteInfoView.as_view(), name='route-info'),
    path('profile/', UserProfileTemplateView.as_view(), name='user-profile'),
    path('api/profile/', UserProfileView.as_view(), name='api-user-profile'),
    path('api/trips/', UserTripsView.as_view(), name='api-user-trips'),
]
