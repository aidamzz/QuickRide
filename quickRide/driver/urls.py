# driver/urls.py
from django.urls import path
from .views import DriverRegistrationView, DriverLoginView, DriverRegistrationTemplateView, DriverLoginTemplateView, RequestedTripsView

urlpatterns = [
    path('api/register/', DriverRegistrationView.as_view(), name='api_register_driver'),
    path('api/login/', DriverLoginView.as_view(), name='api_login_driver'),
    path('register/', DriverRegistrationTemplateView.as_view(), name='register_driver_template'),
    path('login/', DriverLoginTemplateView.as_view(), name='login_driver_template'),
    path('requested-trips/', RequestedTripsView.as_view(), name='requested-trips'), 
]
