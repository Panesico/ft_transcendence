import json, asyncio, logging, requests, os
from channels.generic.websocket import AsyncWebsocketConsumer, AsyncJsonWebsocketConsumer
from .handleMainRoom import readMessage, friendRequestResponse, friendRequest
from .handleInvite import get_authentif_variables
logger = logging.getLogger(__name__)

#----------------- MAIN ROOM -----------------#
users_connected = {}
class mainRoom(AsyncJsonWebsocketConsumer):

  # constructor
  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self.room_group_name = 'main_room'
    self.room_user_name = None
    self.username = None
    self.avatar_url = None
    self.user_id = None

  async def connect(self):
        await self.accept()

        # Get user id from URL
        self.user_id = self.scope['url_route']['kwargs']['user_id']
        logger.debug(f'mainRoom > self.user_id: {self.user_id}')

        # Check if user is already connected
        if self.user_id not in users_connected and self.user_id is not None:
          users_connected[self.user_id] = self
          await self.send_json({
              'message': 'You are connected to the main room!'
          })

          # Get user info
          user_data = get_authentif_variables(self.user_id)
          if user_data is not None:
            self.username = user_data.get('username', '')
            logger.debug(f'mainRoom > self.username: {self.username}')
            self.avatar_url = '/media/' + user_data.get('avatar_url', '')
            logger.debug(f'mainRoom > self.avatar_url: {self.avatar_url}')
            await self.send_json({
              'message': f'Welcome {self.room_user_name}!'
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
    logger.debug(f'mainRoom > typeMessage: {typeMessage}')
    if typeMessage == 'message':
      readMessage(content.get('message', ''))
    
    # Friend request
    if typeMessage == 'friend_request':
      await friendRequest(content, users_connected, self)

    # Friend request response
    if typeMessage == 'friend_request_response':
      await friendRequestResponse(content, users_connected, self.avatar_url)
      

      

      



      






    