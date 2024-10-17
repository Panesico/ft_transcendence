import os, json, logging, websockets, ssl, asyncio, aiohttp, jwt
from django.conf import settings

import prettyprinter
from prettyprinter import pformat
prettyprinter.set_default_config(depth=None, width=80, ribbon_width=80)

logger = logging.getLogger(__name__)
logging.getLogger('websockets').setLevel(logging.WARNING)

async def getDecodedJWT(jwt_token):
    decoded_data = jwt.decode(
        jwt_token,
        settings.SECRET_KEY,
        algorithms=["HS256"]
    )
    return decoded_data

# Get user_id from JWT token
async def getUserId(jwt_token):
    decoded_data = await getDecodedJWT(jwt_token)
    user_id = decoded_data['user_id']
    return user_id
    
# Get user data from user_id
async def getUserData(user_id):
    user = {
        'user_id': user_id,
        'username': None,
        'avatar_url': None,
        'profile': {},
    }
    # logger.debug(f"getUserData > user_id: {user_id}")
    if user_id == 0:
      return user

    url = 'https://authentif:9001/api/getUserInfo/' + str(user_id)

    response = await asyncRequest("GET", "", url, "")
    if response.get('status') == 'success':
        user['username'] = response.get('username')
        user['avatar_url'] = response.get('avatar_url')

    url = 'https://profileapi:9002/api/profile/' + str(user_id)

    response = await asyncRequest("GET", "", url, "")
    if response.get('status') != 'error':
        user['profile'] = response

    return user

# Async http request, csrf_token and data can be "" for 'GET' requests
async def asyncRequest(method, csrf_token, url, data):
    headers = {
        'X-CSRFToken': csrf_token,
        'Cookie': f'csrftoken={csrf_token}',
        'Content-Type': 'application/json',
        'Referer': 'https://gateway:8443',
    }
            
    ssl_context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
    ssl_context.load_verify_locations(os.getenv("CERTFILE"))

    # async http request
    if method == "GET":
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url, headers=headers, ssl=ssl_context) as response:
                    response_json = await response.json()
                    logger.debug(f"asyncRequest > get response: {response_json.get('message')}")
            except aiohttp.ClientError as e:
                logger.error(f"asyncRequest > Error during request: {e}")
                return None
          
    elif method == "POST":
        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(url, json=data, headers=headers, ssl=ssl_context) as response:
                    response_json = await response.json()
                    logger.debug(f"asyncRequest > post response: {response_json.get('message')}")
            except aiohttp.ClientError as e:
                logger.error(f"asyncRequest > Error during request: {e}")
                return None
            
    else:
        logger.error(f"asyncRequest > Unknown method: {method}")
        return None
    
    return response_json