import json, asyncio, logging, requests, os
from .handleInvite import get_authentif_variables

logger = logging.getLogger(__name__)

def readMessage(message):
  logger.debug(f"readMessage > message: {message}")
  return message

async def friendRequestResponse(content, users_connected, receiver_avatar_url, self):
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
  
  # Set the notification as read
  profileapi_url = 'https://profileapi:9002/api/setnotifasread/' + str(sender_id) + '/' + str(receiver_id) + '/friend_request/'
  csrf_token = self.scope['cookies']['csrftoken']
  headers = {
          'X-CSRFToken': csrf_token,
          'Cookie': f'csrftoken={csrf_token}',
          'Content-Type': 'application/json',
          'HTTP_HOST': 'profileapi',
          'Referer': 'https://gateway:8443',
      }
  try:
    response = requests.get(profileapi_url, headers=headers, verify=os.getenv("CERTFILE"))
    logger.debug(f'friendRequestResponse > response: {response}')
    logger.debug(f'friendRequestResponse > response.json(): {response.json()}')

    response.raise_for_status()
    if response.status_code == 200:
      logger.debug(f'friendRequestResponse > Notification marked as read')
    else:
      logger.debug(f'friendRequestResponse > Error marking notification as read')
  except Exception as e:
    logger.debug(f'friendRequestResponse > Error marking notification as read: {e}')
    return


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
    try:
      response = requests.post(
            profileapi_url, json=notification_data, headers=headers, verify=os.getenv("CERTFILE"))
      logger.debug(f'friendRequest > response: {response}')
      logger.debug(f'friendRequest > response.json(): {response.json()}')

      response.raise_for_status()
      if response.status_code == 201:
        # We can now mark the notification as read

        logger.debug(f'friendRequest > Friend request saved in database')
      else:
        logger.debug(f'friendRequest > Error saving friend request in database')
    except Exception as e:
      logger.debug(f'friendRequest > Error saving friend request in database: {e}')
      return

async def handleNewConnection(self, users_connected):
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

async def checkForNotifications(self):
  # Get the database notifications
  profileapi_url = 'https://profileapi:9002/api/getnotif/' + str(self.user_id) + '/'
  csrf_token = self.scope['cookies']['csrftoken']
  headers = {
      'X-CSRFToken': csrf_token,
      'Cookie': f'csrftoken={csrf_token}',
      'Content-Type': 'application/json',
      'HTTP_HOST': 'profileapi',
      'Referer': 'https://gateway:8443',
  }
  response = requests.get(profileapi_url, headers=headers, verify=os.getenv("CERTFILE"))
  logger.debug(f'checkForNotifications > response: {response}')
  logger.debug(f'checkForNotifications > response.json(): {response.json()}')

  response.raise_for_status()
  if response.status_code == 200:
    notifications = response.json()
    logger.debug(f'checkForNotifications > notifications: {notifications}')
    for notification in notifications:
      logger.debug(f'checkForNotifications > notification: {notification}')

      # Find notification concerning the user_id that are unread
      if notification['receiver'] == self.user_id and notification['status'] == 'unread':
        logger.debug(f'checkForNotifications > notification concerning user_id: {self.user_id}')
        logger.debug(f'checkForNotifications > notification unread: {notification}')

        # Get sender info
        sender_data = get_authentif_variables(notification['sender'])
        sender_username = sender_data.get('username', '')
        sender_avatar_url = '/media/' + sender_data.get('avatar_url', '')

        # Get receiver info
        receiver_data = get_authentif_variables(notification['receiver'])
        receiver_username = receiver_data.get('username', '')
        receiver_avatar_url = '/media/' + receiver_data.get('avatar_url', '')


        await self.send_json({ # await users_connected[self.user_id].send_json({
          'type': 'friend_request',
          'message': notification['message'],
          'sender_id': notification['sender'],
          'sender_username': sender_username,
          'sender_avatar_url': sender_avatar_url,
          'receiver_id': notification['receiver'],
          'receiver_username': receiver_username,
          'receiver_avatar_url': receiver_avatar_url,
          'status': notification['status']
        })
  else:
    logger.debug(f'checkForNotifications > Error retrieving notifications from database')
    return


