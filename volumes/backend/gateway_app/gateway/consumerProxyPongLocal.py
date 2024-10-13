import os, json, logging, websockets, ssl, asyncio, aiohttp
from channels.generic.websocket import AsyncWebsocketConsumer
from django.template.loader import render_to_string
logger = logging.getLogger(__name__)

logging.basicConfig(level=logging.DEBUG)

class ProxyCalcGameLocal(AsyncWebsocketConsumer):
    async def connect(self):
        logger.debug("ProxyCalcGameLocal > connect")
        await self.accept()

        # Create an SSL context that explicitly trusts the calcgame certificate
        ssl_context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
        ssl_context.load_verify_locations(os.getenv("CERTFILE"))

        # Establish the WebSocket connection with the trusted certificate
        self.calcgame_ws = await websockets.connect(
            "wss://calcgame:9004/pongcalc_consumer/local/",
            ssl=ssl_context
        )

        # Listener Loop as background task that listens for messages from the calcgame WebSocket and sends those updates to the client. 
        self.calcgame_task = asyncio.create_task(self.listen_to_calcgame())

    async def disconnect(self, close_code):
        logger.debug("ProxyCalcGameLocal > disconnect")
        # Close the WebSocket connection to the calcgame service
        if self.calcgame_ws:
            await self.calcgame_ws.close()

        # Cancel the background task listening to calcgame
        if hasattr(self, 'calcgame_task'):
            self.calcgame_task.cancel()

    async def receive(self, text_data):
        # Handle messages received from the client
        logger.debug("ProxyCalcGameLocal > receive from client")
        data = json.loads(text_data)
        # save the player names and context to build html later
        if data['type'] == 'opening_connection, game details':
            self.p1_name = data['p1_name']
            self.p2_name = data['p2_name']
            self.context = {
                'user': self.scope['user'],
                'session': self.scope['session'],
                'cookies': self.scope['cookies'],
            }
            logger.debug(f"ProxyCalcGameLocal > opening_connection with players: {self.p1_name}, {self.p2_name}")
            logger.debug(f"ProxyCalcGameLocal > self.context['user']: {self.context['user']}, ['user'].id: {self.context['user'].id}")

            self.p1_id = self.context['user'].id if self.context['user'].id else 0
            self.p2_id = 0
            info = {
                'tournament_id': 0,
                'game_round': 'single',
                'game_type': 'pong',
                'p1_name': self.p1_name,
                'p2_name': self.p2_name,
                'p1_id': self.p1_id,
                'p2_id': self.p2_id,
            }
            html = render_to_string('fragments/game_fragment.html', {'context': self.context, 'info': info})
            logger.debug(f"ProxyCalcGameLocal > sending game_start page to client")
            await self.send(json.dumps({
                'type': 'game_start',
                'message': 'Game starting...',
                'html': html,
            }))
        # Forward the message from the client to the calcgame WebSocket server
        await self.calcgame_ws.send(text_data)

    async def listen_to_calcgame(self):
        try:
            while True:
                # Continuously receive messages from calcgame
                calcgame_response = await self.calcgame_ws.recv()
                data = json.loads(calcgame_response)
                if data['type'] == 'game_end':
                    # Game ended
                    await self.game_end(calcgame_response)
                    break
                else:
                    await self.send(calcgame_response)

        except websockets.exceptions.ConnectionClosed:
            logger.debug("ProxyCalcGameLocal > calcgame connection closed")
            pass

    async def game_end(self, calcgame_response):
        logger.debug("ProxyCalcGameLocal > game_end")
        data_calcgame_response = json.loads(calcgame_response)
        game_result = data_calcgame_response.get('game_result')
        logger.debug(f"ProxyCalcGameLocal > game_end game_result: {game_result}")

        html = render_to_string('fragments/game_end_fragment.html', {
              'context': self.context,
              'game_result': game_result
            })
        data_calcgame_response['html'] = html

        # Save game to database
        await self.save_game_to_database(game_result, data_calcgame_response)

        # Notify player that the game has ended
        await self.send(json.dumps(data_calcgame_response))
        

    async def save_game_to_database(self, game_result, data_calcgame_response):
        logger.debug("ProxyCalcGameLocal > save_game_to_database")
        # Save game to database
        play_url = 'https://play:9003/api/saveGame/'

        csrf_token = self.context['cookies'].get('csrftoken')        
        headers = {
            'X-CSRFToken': csrf_token,
            'Cookie': f'csrftoken={csrf_token}',
            'Content-Type': 'application/json',
            'Referer': 'https://gateway:8443',
        }
        
        data = {
            'game_type': 'pong',
            'game_round': 'single',
            'p1_name': self.p1_name,
            'p2_name': self.p2_name,
            'p1_id': self.p1_id,
            'p2_id': self.p2_id,
            'p1_score': game_result.get('p1_score'),
            'p2_score': game_result.get('p2_score'),
            'game_winner_name': game_result.get('game_winner_name'),
            'game_winner_id': self.p1_id if game_result.get('game_winner_name') == 'p1_name' else self.p2_id,
        }
        
        ssl_context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
        ssl_context.load_verify_locations(os.getenv("CERTFILE"))

        # async http request to save game in play container
        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(play_url, json=data, headers=headers, ssl=False) as response:
                    # Check if response status is 200 OK
                    if response.status == 200:
                        response_json = await response.json()
                        logger.debug(f"ProxyPongCalcRemote > calcgame responds: {response_json.get('message')}")
                    else:
                        logger.error(f"ProxyPongCalcRemote > Failed to save game. Status code: {response.status}")
            except aiohttp.ClientError as e:
                logger.error(f"ProxyPongCalcRemote > Error during request: {e}")
