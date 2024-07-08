from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import json
import decimal
from datetime import datetime, date

def default_serializer(obj):
    if isinstance(obj, decimal.Decimal):
        return float(obj)
    elif isinstance(obj, (datetime, date)):
        return obj.isoformat()
    else:
        return str(obj)

def send_trip_update(trip_data):
    # Convert trip_data to a JSON string, converting Decimals and other non-serializable objects
    trip_data_json = json.dumps(trip_data, default=default_serializer)
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        'trips',
        {
            'type': 'send_trip_update',
            'text': trip_data_json
        }
    )
