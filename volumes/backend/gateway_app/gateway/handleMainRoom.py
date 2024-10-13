import json, asyncio, logging, requests, os
logger = logging.getLogger(__name__)

def readMessage(message):
  logger.debug(f"readMessage > message: {message}")
  return message

async def friendRequestResponse(content, users_connected, receiver_avatar_url):
  logger.debug(f'mainRoom > Friend request response: {content}')

  sender_id = content.get('sender_id', '')
  sender_username = content.get('sender_username', '')
  receiver_username = content.get('receiver_username', '')
  receiver_id = content.get('receiver_id', '')
  sender_avatar_url = content.get('sender_avatar_url', '')
  receiver_avatar_url = receiver_avatar_url
  response = content.get('response', '')

  logger.debug(f'mainRoom > sender_id: {sender_id}')
  logger.debug(f'mainRoom > sender_username: {sender_username}')
  logger.debug(f'mainRoom > receiver_username: {receiver_username}')
  logger.debug(f'mainRoom > receiver_id: {receiver_id}')
  logger.debug(f'mainRoom > receiver_avatar: {receiver_avatar_url}')

  # Send response to frontend sender
  if sender_id in users_connected:
    logger.debug(f'mainRoom > sender_id: {sender_id} is in users_connected {response}')
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
    
