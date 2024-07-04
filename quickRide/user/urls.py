from django.urls import path
from .views import RegisterView, LoginView, UserRegisterView, UserLoginView

urlpatterns = [
    path('api/register/', RegisterView.as_view(), name='api_register'),
    path('api/login/', LoginView.as_view(), name='api_login'),
    path('register/', UserRegisterView.as_view(), name='register'),
    path('login/', UserLoginView.as_view(), name='login'),  # This serves the HTML template for login
]
