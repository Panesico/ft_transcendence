import json, asyncio, logging, requests, os
logger = logging.getLogger(__name__)

def readMessage(message):
  logger.debug(f"readMessage > message: {message}")
  return message

async def friendRequestResponse(content, users_connected, receiver_avatar_url):
  logger.debug(f'friendRequestResponse > Friend request response: {content}')

  sender_id = content.get('sender_id', '')
  sender_username = content.get('sender_username', '')
  receiver_username = content.get('receiver_username', '')
  receiver_id = content.get('receiver_id', '')
  sender_avatar_url = content.get('sender_avatar_url', '')
  receiver_avatar_url = receiver_avatar_url
  response = content.get('response', '')

  logger.debug(f'friendRequestResponse > sender_id: {sender_id}')
  logger.debug(f'friendRequestResponse > sender_username: {sender_username}')
  logger.debug(f'friendRequestResponse > receiver_username: {receiver_username}')
  logger.debug(f'friendRequestResponse > receiver_id: {receiver_id}')
  logger.debug(f'friendRequestResponse > receiver_avatar: {receiver_avatar_url}')

  # Send response to frontend sender
  if sender_id in users_connected:
    logger.debug(f'friendRequestResponse > sender_id: {sender_id} is in users_connected {response}')
    await users_connected[sender_id].send_json({
      'type': 'friend_request_response',
      'response': response,
      'message': f'{receiver_username} has accepted your friend request',
      'sender_username': sender_username,
      'sender_id': sender_id,
      'sender_avatar_url': sender_avatar_url,
      'receiver_username': receiver_username,
      'receiver_avatar_url': receiver_avatar_url,
      'receiver_id': receiver_id
    })

async def friendRequest(content, users_connected, self):
    sender_id = content.get('sender_id', '')
    sender_username = content.get('sender_username', '')
    receiver_username = content.get('receiver_username', '')
    receiver_id = content.get('receiver_id', '')
    sender_avatar_url = content.get('sender_avatar_url', '')

    logger.debug(f'friendRequest > sender_id: {sender_id}')
    logger.debug(f'friendRequest > Friend request: {content}')
    logger.debug(f'friendRequest > sender_username: {sender_username}')
    logger.debug(f'friendRequest > receiver_username: {receiver_username}')
    logger.debug(f'friendRequest > receiver_id: {receiver_id}')

    # Check if user_id is in users_connected
    if receiver_id in users_connected:
      logger.debug(f'friendRequest > receiver_id: {receiver_id} is in users_connected')
      await users_connected[receiver_id].send_json({
        'type': 'friend_request',
        'message': f'{receiver_username} sent you a friend request.',
        'sender_username': sender_username,
        'sender_id': sender_id,
        'sender_avatar_url': sender_avatar_url,
        'receiver_avatar_url': self.avatar_url,
        'receiver_username': receiver_username,
        'receiver_id': receiver_id
      })

    # Save friend request in database
    logger.debug(f'friendRequest > Save friend request in database')
    profileapi_url = 'https://profileapi:9002/api/createnotif/'
    notification_data = { 'sender_id': sender_id, 'receiver_id': receiver_id, 'message': f'{receiver_username} sent you a friend request.', 'type': 'friend_request' }
    csrf_token = self.scope['cookies']['csrftoken']
    headers = {
        'X-CSRFToken': csrf_token,
        'Cookie': f'csrftoken={csrf_token}',
        'Content-Type': 'application/json',
        'HTTP_HOST': 'profileapi',
        'Referer': 'https://gateway:8443',
    }
    context = {
            'user': self.scope['user'],
            'session': self.scope['session'],
            'cookies': self.scope['cookies'],
        }
    logger.debug(f'friendRequest > context: {context}')
    try:
      response = requests.post(
            profileapi_url, json=notification_data, headers=headers, verify=os.getenv("CERTFILE"))
      logger.debug(f'friendRequest > response: {response}')
      logger.debug(f'friendRequest > response.json(): {response.json()}')

      response.raise_for_status()
      if response.status_code == 201:
        logger.debug(f'friendRequest > Friend request saved in database')
      else:
        logger.debug(f'friendRequest > Error saving friend request in database')
    except Exception as e:
      logger.debug(f'friendRequest > Error saving friend request in database: {e}')
      return
