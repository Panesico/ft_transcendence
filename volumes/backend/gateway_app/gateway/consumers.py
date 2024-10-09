import json, asyncio, logging, requests, os
from channels.generic.websocket import AsyncWebsocketConsumer 
logger = logging.getLogger(__name__)

def get_authentif_variables(user_id):
  profile_api_url = 'https://authentif:9001/api/getUserInfo/' + str(user_id)
  logger.debug(f"get_edit_profile > profile_api_url: {profile_api_url}")
  response = requests.get(profile_api_url, verify=os.getenv("CERTFILE"))
  if response.status_code == 200:
    return response.json()
  else:
    logger.debug(f"-------> get_edit_profile > Response: {response}")
    return None

def find_matching_usernames(usernames, user_input):
  # Perform a case-insensitive search for usernames containing the user input
  matching_usernames = [username for username in usernames if user_input in username]
  logger.debug(f'FormConsumer > matching_usernames: {matching_usernames}')

  # Convert the QuerySet to a list and return it
  return matching_usernames

def is_valid_key(key):
    # List of keys to ignore
    ignored_keys = {'Shift', 'Ctrl', 'Alt', 'Meta', 'CapsLock', 'Tab', 'Enter', 'Backspace', 'Escape'}
    return key not in ignored_keys

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
    
  # def find_matching_usernames(self, user_input):
  #     # Perform a case-insensitive search for usernames containing the user input
  #     matching_usernames = User.objects.filter(username__icontains=user_input).values_list('username', flat=True)
  #     logger.debug(f'FormConsumer > matching_usernames: {matching_usernames}')

  #     # Convert the QuerySet to a list and return it
  #     return list(matching_usernames)

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
        'suggestions': matching_usernames
      }))
  



  # def update_pressed_keys(self, keys):
  #     logger.debug('FormConsumer > update_pressed_keys')
  #     self.pressed_keys += keys
  #     logger.debug(f'FormConsumer > self.pressed_keys: {self.pressed_keys}')