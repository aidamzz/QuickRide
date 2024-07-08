import datetime
import decimal
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .utils import get_address_from_coords  # Import the utility function
import json

class UserManager(BaseUserManager):
    def create_user(self, phone_number, password=None, **extra_fields):
        if not phone_number:
            raise ValueError('The Phone Number field must be set')
        user = self.model(phone_number=phone_number, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone_number, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(phone_number, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    name = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=20, unique=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = ['name']

    def __str__(self):
        return self.phone_number

# user/models.py
class Trip(models.Model):
    STATUS_CHOICES = [
        ('REQUESTED', 'Requested'),
        ('ACCEPTED', 'Accepted'),
        ('IN_PROGRESS', 'In Progress'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
    ]

    PAYMENT_STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('PAID', 'Paid'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    driver = models.ForeignKey('driver.Driver', on_delete=models.SET_NULL, null=True, blank=True)
    origin = models.CharField(max_length=255)
    origin_address = models.CharField(max_length=255, null=True, blank=True)  # Add this field
    destination = models.CharField(max_length=255)
    destination_address = models.CharField(max_length=255, null=True, blank=True)  # Add this field
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='REQUESTED')
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='PENDING')
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.name} - {self.origin} to {self.destination}"


import simplejson as json
import datetime
import decimal
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, decimal.Decimal):
            return float(obj)
        if isinstance(obj, (datetime.datetime, datetime.date)):
            return obj.isoformat()
        return super(CustomJSONEncoder, self).default(obj)

def send_trip_update(trip_data):
    # Convert the trip_data dictionary to a JSON string using the custom encoder
    trip_data_json = json.dumps(trip_data, cls=CustomJSONEncoder)
    print(trip_data_json, '.........................................................')
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        'trips',
        {
            'type': 'send_trip_update',
            'text': trip_data_json
        }
    )

# Example usage
trip_data = {
    "id": 27,
    "origin": "-0.12408341352957655,51.50257689362153",
    "destination": "-0.08050391320452821,51.491130511083455",
    "user_name": "uuuu",
    "driver_name": "uuuu",
    "status": "ACCEPTED",
    "payment_status": "PENDING",
    "price": decimal.Decimal('9.73'),
    "created_at": datetime.datetime.now(),
}

send_trip_update(trip_data)

@receiver(post_save, sender=Trip)
def trip_post_save(sender, instance, **kwargs):
    trip_data = {
        'id': instance.id,
        'origin': instance.origin,
        'destination': instance.destination,
        'user_name': instance.user.name,  # Ensure 'user_name' is used consistently
        'driver_name': instance.driver.user.name if instance.driver else 'N/A',
        'status': instance.status,
        'payment_status': instance.payment_status,
        'price': instance.price,
        'created_at': instance.created_at.strftime('%Y-%m-%d %H:%M:%S'),
    }
    send_trip_update(trip_data)
