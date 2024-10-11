import os, json, logging, websockets, ssl, asyncio
from channels.generic.websocket import AsyncWebsocketConsumer
from django.template.loader import render_to_string
logger = logging.getLogger(__name__)

logging.basicConfig(level=logging.DEBUG)

# On connect, adds self to waiting_players
# If 2 players in waiting_players, starts a game. Tracked in active_games
# self.active_games = {
            # "game_id": {
            #     "player1": {
            #         "channel_name": "channel_name",
            #         "player_name": "player_name",
            #         "player_id": "player_id",
            #         "ws": "ws",
            #         "context": "context",
            #     },
            #     "player2": {
            #     },
            #     "calcgame_ws": "calcgame_ws",
            #     "calcgame_task": "calcgame_task",
        # }

class ProxyPongCalcRemote(AsyncWebsocketConsumer):
    # Dictionary to store active games
    active_games = {}
    # Dictionary to store players waiting for a game
    waiting_players = {}

    # Add check 
    # user shouldn't be able to play against themselves through two remote games

    async def connect(self):
        logger.debug("ProxyPongCalcRemote > connect")

        # Accept the WebSocket connection from the client
        await self.accept()

        # Generate a unique player ID for this connection
        connect_id = self.channel_name
        context = {
            'user': self.scope['user'],
            'session': self.scope['session'],
            'cookies': self.scope['cookies'],
        }
        self.waiting_players[connect_id] = {
            'channel_name': self.channel_name,
            'player_name': None,
            'player_id': 0,
            'ws': self,
            'context': context,
        }
        
        logger.debug(f"Player connected and added to waiting_players: {connect_id}")

        await self.waiting_room()
        
        self.check_waiting_players_task = asyncio.create_task(self.check_waiting_players())

    async def check_waiting_players(self):
        while True:
            # Filter players with player_name not None
            filtered_players = {k: v for k, v in self.waiting_players.items() 
            if v['player_name'] is not None}
            if len(filtered_players) >= 2:
                # Pop two players from filtered_players
                player1_id, player1 = filtered_players.popitem()
                player2_id, player2 = filtered_players.popitem()

                # Remove the popped players from waiting_players
                self.waiting_players.pop(player1_id)
                self.waiting_players.pop(player2_id)

                # Generate a unique game ID
                game_id = f"game_{len(self.active_games) + 1}"

                # Add the game to the active_games dictionary
                self.active_games[game_id] = {
                    "player1": player1,
                    "player2": player2,
                }

                # logger.debug(f"ProxyPongCalcRemote > Two players connected, starting with ID: {game_id}")
                # logger.debug(f"ProxyPongCalcRemote > start_game player1: {player1}")
                # logger.debug(f"ProxyPongCalcRemote > start_game player2: {player2}")
                await asyncio.sleep(2)
                await self.start_game(game_id)
            else:
                await asyncio.sleep(1)

    async def start_game(self, game_id):
        logger.debug("")
        logger.debug(f"ProxyPongCalcRemote > start_game game_id: {game_id}")
        player1 = self.active_games[game_id]['player1']
        player2 = self.active_games[game_id]['player2']
        logger.debug(f"ProxyPongCalcRemote > start_game player1: {player1}")
        logger.debug(f"ProxyPongCalcRemote > start_game player2: {player2}")

        # logger.debug(f"ProxyPongCalcRemote > start_game p1 context: {player1['context']}")
        # logger.debug(f"ProxyPongCalcRemote > start_game p2 context: {player2['context']}")
        info = {
            'tournament_id': 0,
            'game_round': 'single',
            'game_type': 'pong',
            'p1_name': player1['player_name'],
            'p2_name': player2['player_name'],
            'p1_id': player1['player_id'],
            'p2_id': player2['player_id'],
        }
        html1 = render_to_string('fragments/game_remote_fragment.html', {'context': player1['context'], 'info': info})
        # logger.debug(f"ProxyPongCalcRemote > start_game html1: {html1}")
        html2 = render_to_string('fragments/game_remote_fragment.html', {'context': player1['context'], 'info': info})

        try: # Notify players that the game is starting            
            await player1['ws'].send(json.dumps({
                'type': 'game_start',
                'game_id': game_id,
                'message': 'Game starting', # to translate
                'player_role': 'You are the player on the left', # to translate
                'html': html1,
            }))

            await player2['ws'].send(json.dumps({
                'type': 'game_start',
                'game_id': game_id,
                'message': 'Game starting', # to translate
                'player_role': 'You are the player on the right', # to translate
                'html': html2,
            }))
            
        except Exception as e:
            logger.error(f"ProxyPongCalcRemote > start_game Error notifying players: {e}")

        # Create an SSL context that explicitly trusts the calcgame certificate
        ssl_context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
        ssl_context.load_verify_locations(os.getenv("CERTFILE"))

        # Establish the WebSocket connection with the calcgame service
        calcgame_ws = await websockets.connect(
            "wss://calcgame:9004/pongcalc_consumer/remote/",
            ssl=ssl_context
        )

        # # Start listening for messages from calcgame
        calcgame_task = asyncio.create_task(self.listen_to_calcgame(game_id))

        # Store the WebSocket connection and task in the active_games dictionary
        self.active_games[game_id]['calcgame_ws'] = calcgame_ws
        self.active_games[game_id]['calcgame_task'] = calcgame_task


    async def disconnect(self, close_code):
        logger.debug("ProxyPongCalcRemote > disconnect")

        # Remove the player from waiting_players
        connect_id = self.channel_name
        if connect_id in self.waiting_players:
            del self.waiting_players[connect_id]
        logger.debug(f"Player {connect_id} disconnected and removed from waiting_players")

        # Close the WebSocket connection to the calcgame service
        if hasattr(self, 'calcgame_ws'):
            await self.calcgame_ws.close()

        # Cancel the background task listening to calcgame
        if hasattr(self, 'calcgame_task'):
            self.calcgame_task.cancel()
            

    async def receive(self, text_data):
        logger.debug(f"ProxyPongCalcRemote > receive from {self.channel_name}")
        logger.debug(f"ProxyPongCalcRemote > receive from client: {text_data}")
        data = json.loads(text_data)

        if data['type'] == 'opening_connection':
            connect_id = self.channel_name
            if connect_id in self.waiting_players:
                self.waiting_players[connect_id]['player_name'] = data['p1_name']
                if self.scope['user'].is_authenticated:
                  self.waiting_players[connect_id]['player_id'] = self.scope['user'].id
                logger.debug(f"Updated waiting_players[{connect_id}] with player_name: {data['p1_name']}, player_id: {self.waiting_players[connect_id]['player_id']}")
            else:
                logger.error(f"Player {connect_id} not found in waiting_players")

        # Forward the message from the client to the calcgame WebSocket server
        if hasattr(self, 'calcgame_ws'):
            await self.calcgame_ws.send(text_data)

    async def listen_to_calcgame(self, game_id):
        try:
            while True:
                logger.debug("ProxyPongCalcRemote > listen_to_calcgame")
                calcgame_ws = self.active_games[game_id]['calcgame_ws']
                # Continuously receive messages from calcgame
                calcgame_response = await calcgame_ws.recv()
                data = json.loads(calcgame_response)
                if data['type'] == 'game_end':
                    # Game ended, remove the game from active_games
                    self.active_games.pop(game_id)
                    logger.debug(f"ProxyPongCalcRemote > Game ended, removed game {game_id} from active_games")
                    break
                elif data['type'] == 'connection_established':
                    # Connection established with calcgame, send opening_connection message
                    text_data = json.dumps({
                        'type': 'opening_connection',
                        'game_id': game_id,
                        'p1_name': self.active_games[game_id]['player1']['player_name'],
                        'p2_name': self.active_games[game_id]['player2']['player_name'],
                    })
                    await calcgame_ws.send(text_data)
                else:
                    # Send message received from calcgame to both players
                    player1 = self.active_games[game_id]['player1']
                    player2 = self.active_games[game_id]['player2']
                    await player1['ws'].send(calcgame_response)
                    await player2['ws'].send(calcgame_response)                

        except websockets.exceptions.ConnectionClosed:
            logger.debug("ProxyPongCalcRemote > calcgame connection closed")
            pass

    async def waiting_room(self):
        logger.debug("ProxyPongCalcRemote > player in waiting_room")

        context = {
            'user': self.scope['user'],
            'session': self.scope['session'],
            'cookies': self.scope['cookies'],
        }
        html = render_to_string('fragments/waiting_room.html', context=context)

        await self.send(json.dumps({
            'type': 'waiting_room',
            'message': 'Waiting for another player to join...',
            'html': html,
        }))