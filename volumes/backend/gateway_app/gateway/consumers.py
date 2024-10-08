import json, asyncio, logging
from channels.generic.websocket import AsyncWebsocketConsumer 
logger = logging.getLogger(__name__)

class FormConsumer(AsyncWebsocketConsumer):

  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self.pressed_keys = set()

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
    
  # def find_matching_usernames(self, user_input):
  #     # Perform a case-insensitive search for usernames containing the user input
  #     matching_usernames = User.objects.filter(username__icontains=user_input).values_list('username', flat=True)
  #     logger.debug(f'FormConsumer > matching_usernames: {matching_usernames}')

  #     # Convert the QuerySet to a list and return it
  #     return list(matching_usernames)

  async def receive(self, text_data):
      logger.debug(f"FormConsumer > message received from client: {text_data}")
      key_pressed = json.loads(text_data).get('key', '')
      logger.debug(f'FormConsumer > key_pressed: {key_pressed}')

      # update key pressed
      if key_pressed == 'Backspace':
          self.user_input = self.user_input[:-1]
      elif key_pressed.isalpha() or key_pressed.isnumeric():
          self.user_input += key_pressed
          logger.debug(f'FormConsumer > self.user_input: {self.user_input}')

      # Find matching usernames
      # matching_usernames = self.find_matching_usernames(self.user_input)
      # logger.debug(f'FormConsumer > matching_usernames: {matching_usernames}')

      # # Send back suggestions based on the constructed string
      # self.send(text_data=json.dumps({
      #     'suggestions': matching_usernames
      # }))
  



  # def update_pressed_keys(self, keys):
  #     logger.debug('FormConsumer > update_pressed_keys')
  #     self.pressed_keys += keys
  #     logger.debug(f'FormConsumer > self.pressed_keys: {self.pressed_keys}')


