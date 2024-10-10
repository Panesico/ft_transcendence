import json, asyncio, logging, requests, os
from channels.generic.websocket import AsyncWebsocketConsumer, AsyncJsonWebsocketConsumer
from .handle_invite import get_authentif_variables, find_matching_usernames, is_valid_key
logger = logging.getLogger(__name__)

#----------------- MAIN ROOM -----------------#
class mainRoom(AsyncJsonWebsocketConsumer):

  # constructor
  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self.room_group_name = 'main_room'
    self.room_user_name = None
    self.user_id = None

  async def connect(self):
        await self.accept()
        await self.send_json({
            'message': 'You are connected to the main room!'
        })

  async def disconnect(self, close_code):
    # Leave room group on disconnect
    await self.channel_layer.group_discard(
      self.room_group_name,
      self.channel_name
    )

  # Receive message from WebSocket
  async def receive_json(self, content):
    # Receive message from room group
    message = content.get('message', '')
    await self.send_json({
            'message': message
        })

    