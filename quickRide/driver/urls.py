# driver/urls.py
from django.urls import path
from .views import AcceptTripView,  DriverProfileView, VehicleProfileView, DriverAcceptedTripsView, driver_profile, DriverRegistrationView, DriverLoginView, DriverRegistrationTemplateView, DriverLoginTemplateView, RequestedTripsView
from user.views import JWTLoginView
urlpatterns = [
    path('api/register/', DriverRegistrationView.as_view(), name='api_register_driver'),
    path('api/login/', DriverLoginView.as_view(), name='api_login_driver'),
    path('register/', DriverRegistrationTemplateView.as_view(), name='register_driver_template'),
    path('login/', DriverLoginTemplateView.as_view(), name='login_driver_template'),
    path('requested-trips/', RequestedTripsView.as_view(), name='requested-trips'),
    path('profile/', driver_profile, name='driver-profile'),
    path('profile/api/driver/', DriverProfileView.as_view(), name='driver-profile-api'),
    path('profile/api/vehicle/', VehicleProfileView.as_view(), name='vehicle-profile-api'),
    path('profile/api/trips/', DriverAcceptedTripsView.as_view(), name='driver-accepted-trips-api'),
    path('trips/<int:trip_id>/accept/',  AcceptTripView.as_view(), name='accept_trip'),  # New endpoint
]