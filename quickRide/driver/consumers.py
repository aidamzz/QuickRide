# driver/consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer

class TripConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.channel_layer.group_add("trips", self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard("trips", self.channel_name)

    async def receive(self, text_data):
        pass  # No need to handle incoming WebSocket data for now

    async def send_trip_update(self, event):
        trip_data = event['text']
        await self.send(text_data=json.dumps({
            'trips': [trip_data]
        }))
