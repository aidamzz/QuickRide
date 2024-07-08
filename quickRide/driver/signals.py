from django.db.models.signals import post_save
from django.dispatch import receiver
from user.models import Trip
from .utils import send_trip_update

@receiver(post_save, sender=Trip)
def trip_post_save(sender, instance, **kwargs):
    trip_data = {
        'id': instance.id,
        'origin': instance.origin,
        'destination': instance.destination,
        'user_name': instance.user.name,
        'driver_name': instance.driver.user.name if instance.driver else 'N/A',
        'status': instance.get_status_display(),
        'payment_status': instance.get_payment_status_display(),
        'price': instance.price,
        'created_at': instance.created_at.isoformat(),
    }
    send_trip_update(trip_data)
