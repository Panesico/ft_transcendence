import json, asyncio, logging, requests, os
from channels.generic.websocket import AsyncWebsocketConsumer, AsyncJsonWebsocketConsumer
from .handleMainRoom import readMessage, requestResponse, friendRequest, handleNewConnection, checkForNotifications, markNotificationAsRead
from .handleChatMessages import sendChatMessage, innitChat, getConversation, checkForChatMessages
from .handleInvite import get_authentif_variables, invite_to_game
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
    await handleNewConnection(self, users_connected)
    await checkForNotifications(self)
    await innitChat(self)


  async def disconnect(self, close_code):
    # Remove user from users_connected
    if self.user_id in users_connected:
      del users_connected[self.user_id]
      # Broadcast message to room group
      for user, connection in users_connected.items():
        await connection.send_json({
          'message': f'{self.user_id} has left the main room.',
          'type': 'user_left',
          'user_id': self.user_id,
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
    subTypeMessage = content.get('subtype', '')
    logger.debug(f'mainRoom > typeMessage: {typeMessage}')

    # Message / Logs
    if typeMessage == 'message':
      readMessage(content.get('message', ''))
    elif typeMessage == 'friend_request':
      await friendRequest(content, users_connected, self)
    elif typeMessage == 'friend_request_response':
      await requestResponse(content, users_connected, self.avatar_url, self)
    elif typeMessage == 'mark_notification_as_read':
      await markNotificationAsRead(self, content, self.user_id)
    elif typeMessage == 'chat':
      if subTypeMessage == 'chat_message':
        await sendChatMessage(content, users_connected, self)
      elif subTypeMessage == 'get_conversation':
        await getConversation(content, self)
      elif subTypeMessage == 'check_unread_messages':
        logger.debug(f'mainRoom > check_unread_messages')
        await checkForChatMessages(self)
    elif typeMessage == 'invite_game':
      logger.debug(f'mainRoom > invite_game')
      logger.debug(f'mainRoom > invite_game > content: {content}')
      await invite_to_game(self, content, users_connected)    
    elif typeMessage == 'game_request_response':
      await requestResponse(content, users_connected, self.avatar_url, self)
    elif typeMessage == 'cancel_waiting_room':
      logger.debug(f'mainRoom > cancel_waiting_room, username: {self.username}')
      await requestResponse(content, users_connected, self.avatar_url, self)
