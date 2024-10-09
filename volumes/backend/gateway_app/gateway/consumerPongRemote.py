import os, json, logging, websockets, ssl, asyncio
from channels.generic.websocket import AsyncWebsocketConsumer
from django.template.loader import render_to_string
logger = logging.getLogger(__name__)

logging.basicConfig(level=logging.DEBUG)

class ProxyPongCalcRemote(AsyncWebsocketConsumer):
    waiting_players = []
    active_games = {}

    async def connect(self):
        logger.debug("ProxyPongCalcRemote > connect")

        # Accept the WebSocket connection from the client
        await self.accept()

        # Generate a unique player ID for this connection
        player_id = self.channel_name
        ProxyPongCalcRemote.waiting_players.append(self)

        await self.waiting_room()

        # Check if we have two players connected
        if len(self.connected_players) == 2:
            player1 = ProxyPongCalcRemote.waiting_players.pop(0)
            player2 = ProxyPongCalcRemote.waiting_players.pop(0)

            game_id = f"game_{len(ProxyPongCalcRemote.active_games) + 1}"

            # Store the game in the active_games dictionary
            ProxyPongCalcRemote.active_games[game_id] = {
                "player1": player1,
                "player2": player2,
            }
            
            logger.debug(f"ProxyPongCalcRemote > Two players connected, starting with ID: {game_id}")
            await self.start_game(game_id, player1, player2)
        else:
            logger.debug(f"ProxyPongCalcRemote > Player connected: {player_id}. Waiting for another player.")

    async def start_game(self, game_id, player1, player2):
        # Create an SSL context that explicitly trusts the calcgame certificate
        ssl_context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
        ssl_context.load_verify_locations(os.getenv("CERTFILE"))

        context = {
            'user': self.scope['user'],
            'session': self.scope['session'],
            'cookies': self.scope['cookies'],
        }
        info = {
            'tournament_id': 0,
            'game_round': 'single',
            'game_type': data['game_type'],
            'p1_name': data['p1_name'],
            'p2_name': data['p2_name'],
            'p1_id': p1_id,
            'p2_id': 0,
        }
        html = render_to_string('fragments/game_fragment.html', {'context': context, 'info': info})

        await self.send(json.dumps({
            'type': 'starting',
            'message': 'starting',
            'html': html,
        }))

        # Notify both players that the game has started
        await player1.send(json.dumps({
            'type': 'game_start',
            'message': 'Game started!',
            'game_id': game_id,
            'player_role': 'player1'
        }))
        await player2.send(json.dumps({
            'type': 'game_start',
            'message': 'Game started!',
            'game_id': game_id,
            'player_role': 'player2'
        }))

        # Establish the WebSocket connection with the calcgame service
        self.calcgame_ws = await websockets.connect(
            "wss://calcgame:9004/pongcalc_consumer/remote/",
            ssl=ssl_context
        )

        # Start listening for messages from calcgame
        self.calcgame_task = asyncio.create_task(self.listen_to_calcgame())

        # Notify players that the game has started
        for player_id, consumer in self.connected_players.items():
            await consumer.send(json.dumps({
                'type': 'game_start',
                'message': '2 players connected, game has now started!',
            }))

    async def disconnect(self, close_code):
        logger.debug("ProxyPongCalcRemote > disconnect")

        # Remove the player from connected_players
        player_id = self.channel_name
        if player_id in self.connected_players:
            del self.connected_players[player_id]

        # Close the WebSocket connection to the calcgame service
        if hasattr(self, 'calcgame_ws'):
            await self.calcgame_ws.close()

        # Cancel the background task listening to calcgame
        if hasattr(self, 'calcgame_task'):
            self.calcgame_task.cancel()

        logger.debug(f"Player disconnected: {player_id}. Remaining players: {len(self.connected_players)}")

    async def receive(self, text_data):
        logger.debug(f"ProxyPongCalcRemote > receive from client: {text_data}")
        # Forward the message from the client to the calcgame WebSocket server
        if hasattr(self, 'calcgame_ws'):
            await self.calcgame_ws.send(text_data)

    async def listen_to_calcgame(self):
        try:
            while True:
                # Continuously receive messages from calcgame
                calcgame_response = await self.calcgame_ws.recv()

                logger.debug("ProxyPongCalcRemote > received from calcgame, forwarding to players")
                # Send the received message back to both players
                for player_id, consumer in self.connected_players.items():
                    await consumer.send(calcgame_response)

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