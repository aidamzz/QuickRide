# driver/routing.py
from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/trips/$', consumers.TripConsumer.as_asgi()),
]
