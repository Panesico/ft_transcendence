import json, asyncio, logging, requests, os
from datetime import datetime
from .handleInvite import get_authentif_variables
from django.utils.translation import activate, gettext as _
from django.template.loader import render_to_string
import prettyprinter
from prettyprinter import pformat
prettyprinter.set_default_config(depth=None, width=80, ribbon_width=80)


logger = logging.getLogger(__name__)

def readMessage(message):
  logger.debug(f"readMessage > message: {message}")
  return message

async def requestResponse(content, users_connected, receiver_avatar_url, self):
  logger.debug(f'requestResponse > Friend request response: {content}')
  # language = self.scope['cookies']['django_language']
  # activate(language)
  sender_id = content.get('sender_id', '')
  sender_username = content.get('sender_username', '')
  receiver_username = content.get('receiver_username', '')
  receiver_id = content.get('receiver_id', '')
  sender_avatar_url = content.get('sender_avatar_url', '')
  game_mode = content.get('game_mode', '')
  game_type = content.get('game_type', '')
  html = ''
  receiver_avatar_url = receiver_avatar_url
  response = content.get('response', '')
  type = content.get('type', '')
  logger.debug(f'requestResponse > type: {type}')
  if type == 'friend_request_response' and response == 'accept':
    message = _('has accepted your friend request.')
  elif type == 'friend_request_response' and response == 'decline':
    message = _('has declined your friend request.')
  elif type == 'game_request_response' and response == 'accept':
    message = _('is waiting to play ') + game_type.capitalize()
  elif type == 'game_request_response' and response == 'decline':
    message = _('has declined the game request.')
  elif type == 'cancel_waiting_room':
    message = _('has canceled the game request.')
    user = { 'username': receiver_username }
    context = {
        'user': user,
        'session': self.scope['session'],
        'cookies': self.scope['cookies'],
    }
    html = render_to_string('fragments/home_fragment.html', context=context)
  elif type == 'next_in_tournament':
    message = content.get('notify_player', '')
    receiver_id = sender_id
    receiver_username = sender_username
  elif type == 'blocked':
    message = content.get('message', '')
  logger.debug(f'requestResponse > message: {message}, type: {type}')

  # Send response to frontend sender
  logger.debug(f'requestResponse > sender_id: {sender_id}, users_connected: {users_connected}, type: {type}')
  if sender_id in users_connected:
    logger.debug(f'requestResponse > sender_id: {sender_id} is in users_connected {response}')
    await users_connected[sender_id].send_json({
      'type': type,
      'response': response,
      'message': message,
      'sender_username': sender_username,
      'sender_id': sender_id,
      'sender_avatar_url': sender_avatar_url,
      'receiver_username': receiver_username,
      'receiver_avatar_url': receiver_avatar_url,
      'receiver_id': receiver_id,
      'date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
      'game_mode': game_mode,
      'game_type': game_type,
      'html': html,
    })
  
  # Set the notification as read
  profileapi_url = 'https://profileapi:9002/api/setnotifasread/' + str(sender_id) + '/' + str(receiver_id) + '/' + str(type) + '/' + str(response) + '/'
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
    logger.debug(f'requestResponse > response: {response}')
    logger.debug(f'requestResponse > response.json(): {response.json()}')

    response.raise_for_status()
    if response.status_code == 200:
      logger.debug(f'requestResponse > Notification marked as read')
    else:
      logger.debug(f'requestResponse > Error marking notification as read')
  

  except Exception as e:
    logger.debug(f'requestResponse > Error marking notification as read: {e}')
    return

   # Save the notification in database
  message = receiver_username + ' ' + message
  logger.debug(f'requestResponse > message: {message}')
  profileapi_url = 'https://profileapi:9002/api/createnotif/'
  notification_data = { 'sender_id': receiver_id, 'receiver_id': sender_id, 'message': message, 'type': type, 'game_type': game_type }
  try:
    response = requests.post(
          profileapi_url, json=notification_data, headers=headers, verify=os.getenv("CERTFILE"))

    response.raise_for_status()
    if response.status_code == 201:
      logger.debug(f'requestResponse > Notification saved in database')
    else:
      logger.debug(f'requestResponse > Error saving notification')
  except Exception as e:
    logger.debug(f'requestResponse > Error saving notification: {e}')
    return

# async def cancelGameRequest(content, users_connected, receiver_avatar_url, self):
#   logger.debug(f'cancelGameRequest > Game request response: {content}')

#   sender_id = content.get('sender_id', '')
#   sender_username = content.get('sender_username', '')
#   receiver_username = content.get('receiver_username', '')
#   receiver_id = content.get('receiver_id', '')
#   sender_avatar_url = content.get('sender_avatar_url', '')
#   game_mode = content.get('game_mode', '')
#   game_type = content.get('game_type', '')
#   receiver_avatar_url = receiver_avatar_url
#   response = content.get('response', '')
#   type = content.get('type', '')

#   logger.debug(f'cancelGameRequest > type: {type}')
#   message = f'{sender_username} has canceled the game request.'

#   csrf_token = self.scope['cookies']['csrftoken']
#   headers = {
#           'X-CSRFToken': csrf_token,
#           'Cookie': f'csrftoken={csrf_token}',
#           'Content-Type': 'application/json',
#           'HTTP_HOST': 'profileapi',
#           'Referer': 'https://gateway:8443',
#       }
#   try:
#     response = requests.get(profileapi_url, headers=headers, verify=os.getenv("CERTFILE"))
#     logger.debug(f

async def friendRequest(content, users_connected, self):
  sender_id = content.get('sender_id', '')
  sender_username = content.get('sender_username', '')
  receiver_id = content.get('receiver_id', '')
  sender_avatar_url = content.get('sender_avatar_url', '')
  msg_body = _('sent you a friend request')
  message = sender_username + ' ' + msg_body
  game_type = content.get('game_type', '')
  receiver_avatar_url = content.get('receiver_avatar_url', '')

  # Get username of receiver
  user_data = get_authentif_variables(receiver_id)
  receiver_username = user_data.get('username', '')
  logger.debug(f'friendRequest > receiver_username: {receiver_username}')
  if user_data is None:
    logger.debug(f'friendRequest > Error getting receiver_username')
    return
  logger.debug(f'friendRequest > sender_id: {sender_id}')
  logger.debug(f'friendRequest > Friend request: {content}')
  logger.debug(f'friendRequest > sender_username: {sender_username}')
  logger.debug(f'friendRequest > receiver_id: {receiver_id}')

  # Save friend request in database
  logger.debug(f'friendRequest > Save friend request in database')
  profileapi_url = 'https://profileapi:9002/api/createnotif/'
  notification_data = { 'sender_id': sender_id, 'receiver_id': receiver_id, 'message': message, 'type': 'friend_request', 'game_type': game_type }
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
      # Check if user_id is in users_connected
      if receiver_id in users_connected:
        logger.debug(f'friendRequest > receiver_id: {receiver_id} is in users_connected')
        # Get current date and time
        date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        await users_connected[receiver_id].send_json({
          'type': 'friend_request',
          'message': message,
          'sender_username': sender_username,
          'sender_id': sender_id,
          'sender_avatar_url': sender_avatar_url,
          'receiver_avatar_url': self.avatar_url,
          'receiver_username': receiver_username,
          'receiver_id': receiver_id,
          'date': date,
          'receiver_avatar_url': receiver_avatar_url
        })
    else:
      logger.debug(f'friendRequest > Error saving friend request in database')
  except Exception as e:
    logger.debug(f'friendRequest > Error saving friend request in database: {e}')
    return

async def handleNewConnection(self, users_connected):
  logger.debug('')
  logger.debug(f'mainRoom > handleNewConnection')
  # Get user id from URL
  self.user_id = self.scope['url_route']['kwargs']['user_id']
  # If user is not connected, close connection
  if (self.user_id == 'None' or self.user_id == 0):
    logger.debug(f'mainRoom > self.user_id: {self.user_id} closed connection')
    await self.close()
  logger.debug(f'mainRoom > self.user_id: {self.user_id}')

# Check if user is already connected
# if self.user_id not in users_connected and self.user_id is not None:
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
  else:
    logger.debug(f'mainRoom > Error getting user info')
    await self.close()

  # Broadcast message to room group
  for user, connection in users_connected.items():
    await connection.send_json({
      'message': f'{self.user_id} has joined the main room.',
      'type': 'user_connected',
      'user_id': self.user_id,
    })
  # else:
  #   logger.debug(f'mainRoom > self.user_id: {self.user_id} closed connection')
  #   await self.close()

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
    notifications = sorted(response.json(), key=lambda x: x['date'])
    logger.debug(f'checkForNotifications > notifications: {notifications}')
    logger.debug(f'checkForNotifications > info user connected: {self.user_id}')
    
    for notification in notifications:
      logger.debug(f'checkForNotifications > notification: {notification}')

      # Find notification concerning the user_id that are unread
      if notification['receiver'] == self.user_id:
        logger.debug(f'checkForNotifications > notification concerning user_id: {self.user_id}')
        logger.debug(f'checkForNotifications > notification: {notification}')

        # Get sender info
        sender_data = get_authentif_variables(notification['sender'])
        sender_username = sender_data.get('username', '')
        sender_avatar_url = '/media/' + sender_data.get('avatar_url', '')

        # Get receiver info
        receiver_data = get_authentif_variables(notification['receiver'])
        receiver_username = receiver_data.get('username', '')
        receiver_avatar_url = '/media/' + receiver_data.get('avatar_url', '')

        # If notif is a response, reverse sender and receiver info
        if notification['type'] == 'game_request_response' or notification['type'] == 'friend_request_response' or notification['type'] == 'cancel_waiting_room':
          sender_username = receiver_data.get('username', '')
          sender_avatar_url = '/media/' + receiver_data.get('avatar_url', '')
          receiver_username = sender_data.get('username', '')
          receiver_avatar_url = '/media/' + sender_data.get('avatar_url', '')

        # Send notification to frontend
        await self.send_json({
          'type': notification['type'],
          'message': notification['message'],
          'sender_id': notification['sender'],
          'sender_username': sender_username,
          'sender_avatar_url': sender_avatar_url,
          'receiver_id': notification['receiver'],
          'receiver_username': receiver_username,
          'receiver_avatar_url': receiver_avatar_url,
          'status': notification['status'],
          'date': notification['date'],
          'game_type': notification['game_type']
        })
  else:
    logger.debug(f'checkForNotifications > Error retrieving notifications from database')
    return

async def markNotificationAsRead(self, content, user_id):
  profileapi_url = 'https://profileapi:9002/api/setallnotifasread/' + str(user_id) + '/'
  csrf_token = self.scope['cookies']['csrftoken']
  headers = {
      'X-CSRFToken': csrf_token,
      'Cookie': f'csrftoken={csrf_token}',
      'Content-Type': 'application/json',
      'HTTP_HOST': 'profileapi',
      'Referer': 'https://gateway:8443',
  }
  response = requests.get(profileapi_url, headers=headers, verify=os.getenv("CERTFILE"))
  logger.debug(f'markNotificationAsRead > response.json(): {response.json()}')

  response.raise_for_status()
  if response.status_code == 200:
    logger.debug(f'markNotificationAsRead > Notification marked as read')
  else:
    logger.debug(f'markNotificationAsRead > Error marking notification as read')
    return


# async def getConnectedFriends(self, content, users_connected):  
#   # Get friends
#   logger.debug(f"getConnectedFriends > content: {content}")

#   profile_api_url = 'https://profileapi:9002/api/getfriends/' + content.get('sender_id', '') + '/'
#   response = requests.get(profile_api_url, verify=os.getenv("CERTFILE"))
#   friends = response.json()
#   logger.debug(f"getConnectedFriends > friends: {friends}")
#   logger.debug(f"getConnectedFriends > users_connected: {users_connected}")

#   if response.ok:
#     connected_friends_ids = [friend['user_id'] for friend in friends if friend['user_id'] in users_connected]
#     logger.debug(f"getConnectedFriends > connected_friends_ids: {connected_friends_ids}")

#     await self.send_json({
#       'type': 'connected_friends',
#       'sender_id': self.user_id,
#       'connected_friends_ids': connected_friends_ids,
#     })
#   else:
#     logger.error(f"getConnectedFriends > Error retrieving friends")

async def checkIfUsersAreBlocked(self, content):
  sender_id = content.get('sender_id', '')
  receiver_id = content.get('receiver_id', '')
  type = content.get('type', '')
  profileapi_url = 'https://profileapi:9002/api/getBlockedUsers/' + str(sender_id) + '/' + str(receiver_id) + '/'
  csrf_token = self.scope['cookies']['csrftoken']
  headers = {
      'X-CSRFToken': csrf_token,
      'Cookie': f'csrftoken={csrf_token}',
      'Content-Type': 'application/json',
      'HTTP_HOST': 'profileapi',
      'Referer': 'https://gateway:8443',
  }
  response = requests.get(profileapi_url, headers=headers, verify=os.getenv("CERTFILE"))
  logger.debug(f'checkIfUsersAreBlocked > response: {response}')
  logger.debug(f'checkIfUsersAreBlocked > response.json(): {response.json()}')
  if response.ok:
    status = response.json().get('status', '')
    logger.debug(f'checkIfUsersAreBlocked > status: {status}')
    if status == 'blocked':
      # Send message to frontend
      return True
  else:
    logger.debug(f'checkIfUsersAreBlocked > Error checking if users are blocked')
  return False

async def block_user_responses(self, content, users_connected):
  logger.debug(f'block_user_responses > content: {content}')
  sender_id = content.get('sender_id', '')
  receiver_id = content.get('receiver_id', '')

  # Get usernames
  sender_data = get_authentif_variables(sender_id)
  sender_avatar_url = '/media/' + sender_data.get('avatar_url', '')
  sender_username = sender_data.get('username', '')
  receiver_data = get_authentif_variables(receiver_id)
  receiver_username = receiver_data.get('username', '')
  receiver_avatar_url = '/media/' + receiver_data.get('avatar_url', '')
  game_type = ""
  logger.debug(f'block_user_responses > sender_username: {sender_username}')

  # Send to the sender if connected
  logger.debug(f'block_user_responses > users_connected: {users_connected}')
  message = _('You have blocked ')
  if sender_id in users_connected:
    logger.debug(f'block_user_responses > sender_id: {sender_id} is in users_connected')
    await users_connected[sender_id].send_json({
      'type': 'block',
      'message': f'You have blocked {receiver_username}',
      'receiver_username': receiver_username,
      'receiver_id': receiver_id,
      'block_sender': True,
      'sender_username': sender_username,
      'sender_avatar_url': sender_avatar_url,
      'receiver_avatar_url': receiver_avatar_url,
    })
  else:
    logger.debug(f'block_user_responses > sender_id: {sender_id} is not in users_connected')
  
  # Send to the receiver if connected
  message = _(' has blocked you.')
  if receiver_id in users_connected:
    logger.debug(f'block_user_responses > receiver_id: {receiver_username} is in users_connected')
    await users_connected[receiver_id].send_json({
      'type': 'block',
      'message': message,
      'sender_username': sender_username,
      'sender_id': sender_id,
      'block_sender': False,
      'receiver_username': receiver_username,
      'receiver_avatar_url': receiver_avatar_url,
      'sender_avatar_url': sender_avatar_url,
      'date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    })
  else:
    logger.debug(f'block_user_responses > receiver: {receiver_username} is not in users_connected')
  
  # Save the notification in database
  message = receiver_username + ' ' + message
  logger.debug(f'requestResponse > message: {message}')
  profileapi_url = 'https://profileapi:9002/api/createnotif/'
  notification_data = { 'sender_id': receiver_id, 'receiver_id': sender_id, 'message': message, 'type': type, 'game_type': game_type }
  try:
    response = requests.post(
          profileapi_url, json=notification_data, headers=headers, verify=os.getenv("CERTFILE"))

    response.raise_for_status()
    if response.status_code == 201:
      logger.debug(f'requestResponse > Notification saved in database')
    else:
      logger.debug(f'requestResponse > Error saving notification')
  except Exception as e:
    logger.debug(f'requestResponse > Error saving notification: {e}')
    return


  
  