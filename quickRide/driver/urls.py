from django.urls import path
from .views import DriverRegistrationView, register_vehicle, DriverLoginView

urlpatterns = [
    path('register/', DriverRegistrationView.as_view(), name='register_driver'),
    path('register_vehicle/', register_vehicle, name='register_vehicle'),
    path('login/', DriverLoginView.as_view(), name='driver_login'),
]
