import json, asyncio, logging, requests, os
from channels.generic.websocket import AsyncWebsocketConsumer, AsyncJsonWebsocketConsumer
from .handleMainRoom import readMessage
logger = logging.getLogger(__name__)

#----------------- MAIN ROOM -----------------#
users_connected = {}
class mainRoom(AsyncJsonWebsocketConsumer):

  # constructor
  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self.room_group_name = 'main_room'
    self.room_user_name = None
    self.user_id = None

  async def connect(self):
        await self.accept()
        self.user_id = self.scope['url_route']['kwargs']['user_id']
        logger.debug(f'mainRoom > self.user_id: {self.user_id}')
        if self.user_id not in users_connected and self.user_id is not None:
          users_connected[self.user_id] = self
          await self.send_json({
              'message': 'You are connected to the main room!'
          })
          # Broadcast message to room group
          for user, connection in users_connected.items():
            await connection.send_json({
              'message': f'{self.user_id} has joined the main room.'
            })
        else:
          logger.debug(f'mainRoom > self.user_id: {self.user_id} closed connection')
          await self.close()

  async def disconnect(self, close_code):
    # Remove user from users_connected
    if self.user_id in users_connected:
      del users_connected[self.user_id]
      # Broadcast message to room group
      for user, connection in users_connected.items():
        await connection.send_json({
          'message': f'{self.user_id} has left the main room.'
        })
    
    # Leave room group on disconnect
    await self.channel_layer.group_discard(
      self.room_group_name,
      self.channel_name
    )

  # Receive message from WebSocket
  async def receive_json(self, content):
    # Receive message from room group
    typeMessage = content.get('type', '')
    if typeMessage == 'message':
      readMessage(content.get('message', ''))

      



      






    