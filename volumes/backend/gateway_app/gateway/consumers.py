import json, asyncio, logging, requests, os
from channels.generic.websocket import AsyncWebsocketConsumer
from .handleInvite import get_authentif_variables, find_matching_usernames, is_valid_key
logger = logging.getLogger(__name__)

class FormConsumer(AsyncWebsocketConsumer):

  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)

  async def connect(self):
    # Accept the WebSocket connection
      logger.debug('FormConsumer > connect')
      await self.accept()
      # Send an initial message to confirm the connection
      await self.send(text_data=json.dumps({
        'type': 'connection_established',
        'message': 'You are connected!'
      }))
      self.user_input = ""

  async def disconnect(self, close_code):
      logger.debug('FormConsumer > disconnect')
      pass
    
  async def receive(self, text_data):
      # Handle messages received from the client
      logger.debug(f"FormConsumer > message received from client: {text_data}")

      # Parse the JSON message
      key_pressed = json.loads(text_data).get('key', '')
      user_id = json.loads(text_data).get('userID', '')
      if user_id:
        self.user_id = user_id
        logger.debug(f'FormConsumer > self.user_id: {self.user_id}')
        profile_data = get_authentif_variables(self.user_id)
        self.usernames = profile_data.get('usernames')
        logger.debug(f'FormConsumer > usernames: {self.usernames}')

      logger.debug(f'FormConsumer > key_pressed: {key_pressed}')

      # update key pressed
      if key_pressed == 'Backspace':
          self.user_input = self.user_input[:-1]
      elif key_pressed.isascii() and is_valid_key(key_pressed):
          self.user_input += key_pressed
          logger.debug(f'FormConsumer > self.user_input: {self.user_input}')
      
      # Find matching usernames
      matching_usernames = find_matching_usernames(self.usernames, self.user_input)
      logger.debug(f'FormConsumer > matching_usernames: {matching_usernames}')

      # # Send back suggestions based on the constructed string
      await self.send(text_data=json.dumps({
        'type': 'suggestions',
        'suggestions': matching_usernames,
        'message': 'Suggestions sent!'
      }))

  


