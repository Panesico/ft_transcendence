import json, asyncio, logging, requests, os
logger = logging.getLogger(__name__)

def get_authentif_variables(user_id):
  profile_api_url = 'https://authentif:9001/api/getUserInfo/' + str(user_id)
  logger.debug(f"get_authentif_variables > profile_api_url: {profile_api_url}")
  response = requests.get(profile_api_url, verify=os.getenv("CERTFILE"))
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