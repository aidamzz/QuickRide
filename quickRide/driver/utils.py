# utils.py in driver app

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
