import json, asyncio, logging, requests, os
from datetime import datetime
from .handleInvite import get_authentif_variables

logger = logging.getLogger(__name__)

async def sendChatMessage(content, users_connected, self):
  sender_id = content.get('sender_id', '')
  receiver_id = content.get('receiver_id', '')
  message = content.get('message', '')
  date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

  logger.debug(f'senChatMessage > sender_id: {sender_id}')
  logger.debug(f'senChatMessage > receiver_id: {receiver_id}')
  logger.debug(f'senChatMessage > message: {message}')

  # Check if user_id is in users_connected
  if receiver_id in users_connected:
    logger.debug(f'senChatMessage > receiver_id: {receiver_id} is in users_connected')
    # Get current date and time
    await users_connected[receiver_id].send_json({
      'type': 'chat_message',
      'message': message,
      'sender_id': sender_id,
      'receiver_id': receiver_id,
      'date': date
    })

  # Save chat message request in database
  logger.debug(f'senChatMessage > Save chat message in database')
  profileapi_url = 'https://profileapi:9002/livechat/api/saveChatMessage/'
  message_data = { 'sender_id': sender_id, 'receiver_id': receiver_id, 'message': message, 'type': 'chat_message', 'date': date }
  csrf_token = self.scope['cookies']['csrftoken']
  headers = {
      'X-CSRFToken': csrf_token,
      'Cookie': f'csrftoken={csrf_token}',
      'Content-Type': 'application/json',
      'HTTP_HOST': 'profileapi',
      'Referer': 'https://gateway:8443',
  }
  try:
    response = requests.post(
          profileapi_url, json=message_data, headers=headers, verify=os.getenv("CERTFILE"))
    logger.debug(f'senChatMessage > response: {response}')
    logger.debug(f'senChatMessage > response.json(): {response.json()}')

    response.raise_for_status()
    if response.status_code == 201:
      # We can now mark the chat as read
      logger.debug(f'senChatMessage > Chat message saved in database')
    else:
      logger.debug(f'senChatMessage > Error saving chat message in database')
  except Exception as e:
    logger.debug(f'senChatMessage > Error saving chat message in database: {e}')
    return


async def checkForChatMessages(self):
  # Get the database chat messages
  profileapi_url = 'https://profileapi:9002/livechat/api/getReceivedChatMessages/' + str(self.user_id) + '/'
  csrf_token = self.scope['cookies']['csrftoken']
  headers = {
      'X-CSRFToken': csrf_token,
      'Cookie': f'csrftoken={csrf_token}',
      'Content-Type': 'application/json',
      'HTTP_HOST': 'profileapi',
      'Referer': 'https://gateway:8443',
  }
  response = requests.get(profileapi_url, headers=headers, verify=os.getenv("CERTFILE"))
  logger.debug(f'checkForChatMessages > response.json(): {response.json()}')

  response.raise_for_status()
  if response.status_code == 200:
    chat_messages = sorted(response.json(), key=lambda x: x['timestamp'])
    logger.debug(f'checkForChatMessages > chat_messages: {chat_messages}')
    logger.debug(f'checkForChatMessages > info user connected: {self.user_id}')
    
  unread_messages = 0
  for chat_message in chat_messages:
    logger.debug(f'checkForChatMessages > chat_message: {chat_message}')
    if chat_message['read'] == False:
      unread_messages += 1

      

     

  