import json, asyncio, logging, requests, os
from channels.generic.websocket import AsyncWebsocketConsumer, AsyncJsonWebsocketConsumer
from .handleMainRoom import readMessage, friendRequestResponse
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
      logger.debug(f'mainRoom > Friend request: {content}')
      sender_id = content.get('sender_id', '')
      sender_username = content.get('sender_username', '')
      receiver_username = content.get('receiver_username', '')
      receiver_id = content.get('receiver_id', '')
      logger.debug(f'mainRoom > sender_id: {sender_id}')
      logger.debug(f'mainRoom > sender_username: {sender_username}')
      logger.debug(f'mainRoom > receiver_username: {receiver_username}')
      logger.debug(f'mainRoom > receiver_id: {receiver_id}')
      sender_avatar_url = content.get('sender_avatar_url', '')
      # Check if user_id is in users_connected
      if receiver_id in users_connected:
        logger.debug(f'mainRoom > receiver_id: {receiver_id} is in users_connected')
        await users_connected[receiver_id].send_json({
          'type': 'friend_request',
          'message': f'You have a friend request from {receiver_username}',
          'sender_username': sender_username,
          'sender_id': sender_id,
          'sender_avatar_url': sender_avatar_url,
          'receiver_avatar_url': self.avatar_url,
          'receiver_username': receiver_username,
          'receiver_id': receiver_id
        })
      else:
        logger.debug(f'mainRoom > receiver_id: {receiver_id} is NOT in users_connected')
    
    # Friend request response
    if typeMessage == 'friend_request_response':
      await friendRequestResponse(content, users_connected, self.avatar_url)
      

      

      



      






    