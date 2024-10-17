import json, asyncio, logging, requests, os
from datetime import datetime
logger = logging.getLogger(__name__)

def get_authentif_variables(user_id):
  authentif_api_url = 'https://authentif:9001/api/getUserInfo/' + str(user_id)
  logger.debug(f"get_authentif_variables > authentif_api_url: {authentif_api_url}")
  response = requests.get(authentif_api_url, verify=os.getenv("CERTFILE"))
  logger.debug(f"get_authentif_variables > Response: {response}")
  if response.status_code == 200:
    return response.json()
  else:
    logger.debug(f"-------> get_authentif_variables > Response: {response}")
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

async def invite_to_game(self, content, users_connected):
  csrf_token = self.scope['cookies']['csrftoken']
  headers = {
      'X-CSRFToken': csrf_token,
      'Cookie': f'csrftoken={csrf_token}',
      'Content-Type': 'application/json',
      'Referer': 'https://gateway:8443',
  }

  logger.debug(f'invite_to_game > content: {content}')
  sender_id = content.get('sender_id', '')
  receiver_id = content.get('receiver_id', '')
  sender_avatar_url = content.get('sender_avatar_url', '')
  sender_username = content.get('sender_username', '')
  logger.debug(f'invite_to_game > sender_username: {sender_username}')
  receiver_username = self.username
  logger.debug(f'invite_to_game > sender_username: {sender_username}')
  message = sender_username + ' has invited you to join a game.'
  date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

  if receiver_id in users_connected:
    await users_connected[receiver_id].send_json({
      'type': 'game_request',
      'sender_id': sender_id,
      'sender_username': sender_username,
      'receiver_username': receiver_username,
      'receiver_id': receiver_id,
      'sender_avatar_url': sender_avatar_url,
      'receiver_avatar_url': self.avatar_url,
      'message': message,
      'date': date
    })

  # Save notification in database
  profileapi_url = 'https://profileapi:9002/api/createnotif/'
  notification_data = { 'sender_id': sender_id, 'receiver_id': receiver_id, 'type': 'game_request', 'message': message }
  try:
    response = requests.post(profileapi_url, json=notification_data, headers=headers, verify=os.getenv("CERTFILE"))
    logger.debug(f'invite_to_game > response: {response}')
    logger.debug(f'invite_to_game > response.json(): {response.json()}')

    response.raise_for_status()
    if response.status_code == 201:
      logger.debug(f'invite_to_game > Notification saved')
    else:
      logger.debug(f'invite_to_game > Error saving notification')
      return
  except Exception as e:
    logger.debug(f'invite_to_game > Error saving notification: {e}')
    return

