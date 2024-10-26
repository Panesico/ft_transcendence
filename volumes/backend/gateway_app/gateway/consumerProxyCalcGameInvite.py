import os, json, logging, websockets, ssl, asyncio
from datetime import datetime, timedelta
from channels.generic.websocket import AsyncWebsocketConsumer
from django.template.loader import render_to_string
from .utils import getUserId, getUserData, asyncRequest
from django.utils.translation import gettext as _

import prettyprinter
from prettyprinter import pformat
prettyprinter.set_default_config(depth=None, width=80, ribbon_width=80)

logger = logging.getLogger(__name__)
logging.getLogger('websockets').setLevel(logging.WARNING)

# On connect, adds self to waiting
# If 2 players in waiting, starts a game. Tracked in active_games
# self.active_games = {
            # "game_id": {
            #     "game_type": 'pong' or 'cows',
            #     "player1": {
            #         "channel_name": "channel_name",
            #         "player_name": "player_name",
            #         "player_id": "player_id",
            #         "ws": "ws",
            #         "context": "context",
            #         "ready": False,
            #     },
            #     "player2": { ... },
            #     "calcgame_ws": "calcgame_ws",
            #     "calcgame_task": "calcgame_task",
        # }

class ProxyCalcGameInvite(AsyncWebsocketConsumer):
    active_games = {} # Dictionary to store active games
    waiting = {} # Dictionary to store players waiting for a game
    unique_id = 1

    # Add check 
    # user should not be able to play against themselves through two remote games

    async def connect(self):
        logger.debug("ProxyCalcGameInvite > connect")
        await self.accept()
        
        # Extract the query selector from the WebSocket URL
        query_selector = self.scope['query_string'].decode('utf-8')
        if '=' in query_selector and len(query_selector.split('=')) > 1:
            game_type = query_selector.split('=')[1]
        else:
            game_type = None
        
        if game_type == None or game_type not in ['pong', 'cows']:
            logger.error("ProxyCalcGameInvite > No game_type provided, connection closed")
            await self.close()
            return
        
        # Generate a unique player ID for this connection
        connect_id = self.channel_name
        jwt_token = self.scope['cookies']['jwt_token']
        user_id = await getUserId(jwt_token)
        user = await getUserData(user_id)
        context = {
            'user': user,
            'session': self.scope['session'],
            'cookies': self.scope['cookies'],
        }

        if game_type not in self.waiting:
            self.waiting[game_type] = {}
        
        self.waiting[game_type][connect_id] = {
            'channel_name': self.channel_name,
            'player_name': None,
            'player_id': 0,
            'ws': self,
            'context': context,
        }
        
        logger.debug(f"Player connected and added to waiting: {connect_id}")

        await self.waiting_room(context)
        
        self.check_waiting_task = asyncio.create_task(self.check_waiting(game_type))
    

    async def check_waiting(self, game_type):
      while True:
        if game_type in self.waiting:
            for player_id, player_info in self.waiting[game_type].items():
                if player_info['player_name'] is not None:
                    for other_player_id, other_player_info in self.waiting[game_type].items():
                      # Check if 2 players have the same combined_id
                      if player_info['combined_id'] == other_player_info['combined_id'] and player_id != other_player_id:
                        logger.debug(f"Matched players with combined_id {player_info['combined_id']}")
                        self.waiting[game_type].pop(player_id)
                        self.waiting[game_type].pop(other_player_id)

                        # Create a new game
                        game_id = self.unique_id
                        self.unique_id += 1
                        self.active_games[game_id] = {
                          "game_type": player_info['game_type'],
                          "player1": player_info,
                          "player2": other_player_info,
                        }

                        await asyncio.sleep(2)
                        await self.start_game(game_id)
                        break                        

        await asyncio.sleep(1)


    async def start_game(self, game_id):
        logger.debug("")
        logger.debug(f"ProxyCalcGameInvite > start_game game_id: {game_id}")
        game = self.active_games[game_id]
        player1 = game['player1']
        player2 = game['player2']
        # logger.debug(f"ProxyCalcGameInvite > start_game game: {pformat(game)}")
        # logger.debug(f"ProxyCalcGameInvite > start_game player1: {pformat(player1)}")
        # logger.debug(f"ProxyCalcGameInvite > start_game player2: {pformat(player2)}")

        if player1['player_name'] == player2['player_name']:
            player1['player_name'] += "#1"
            player2['player_name'] += "#2"

        info = {
            'tournament_id': 0,
            'game_round': 'single',
            'game_type': game['game_type'],
            'p1_name': player1['player_name'],
            'p2_name': player2['player_name'],
            'p1_id': player1['player_id'],
            'p2_id': player2['player_id'],
            'p1_avatar_url': player1['context']['user']['avatar_url'],
            'p2_avatar_url': player2['context']['user']['avatar_url'],
        }
        html1 = render_to_string('fragments/game_remote_fragment.html', {'context': player1['context'], 'info': info})
        html2 = render_to_string('fragments/game_remote_fragment.html', {'context': player2['context'], 'info': info})

        try: # Notify players that the game is starting            
            await player1['ws'].send(json.dumps({
                'type': 'game_start',
                'game_id': game_id,
                'title': _('Game starting...'),
                'message': _('You are the player on the left'),
                'player_role': '1',
                'html': html1,
            }))

            await player2['ws'].send(json.dumps({
                'type': 'game_start',
                'game_id': game_id,
                'title': _('Game starting...'),
                'message': _('You are the player on the right'),
                'player_role': '2',
                'html': html2,
            }))
            
        except Exception as e:
            logger.error(f"ProxyCalcGameInvite > start_game Error notifying players: {e}")

        # Create an SSL context that explicitly trusts the calcgame certificate
        ssl_context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
        ssl_context.load_verify_locations(os.getenv("CERTFILE"))

        # Establish the WebSocket connection with the calcgame service
        calcgame_ws = await websockets.connect(
            f"wss://calcgame:9004/pongcalc_consumer/remote/{game['game_type']}/",
            ssl=ssl_context
        )

        # # Start listening for messages from calcgame
        calcgame_task = asyncio.create_task(self.listen_to_calcgame(game_id))

        # Store the WebSocket connection and task in the active_games dictionary
        self.active_games[game_id]['calcgame_ws'] = calcgame_ws
        self.active_games[game_id]['calcgame_task'] = calcgame_task


    async def disconnect(self, close_code):
        logger.debug("ProxyCalcGameInvite > disconnect")

        connect_id = self.channel_name

        # Remove the player from the appropriate waiting[game_type] list if they exist
        for game_type, waiting_players in self.waiting.items():
            if connect_id in waiting_players:
                del waiting_players[connect_id]
                logger.debug(f"Player {connect_id} disconnected and removed from waiting[{game_type}]")
                break  # Stop once the player is found and removed

        # Close the game if the player is in an active game
        for game_id, game in self.active_games.items():
            if connect_id == game['player1']['channel_name'] or connect_id == game['player2']['channel_name']:
                await self.close_game(game_id)
                break        

        # Close the WebSocket connection to the calcgame service if it exists
        if hasattr(self, 'calcgame_ws'):
            await self.calcgame_ws.close()

        # Cancel the background task listening to calcgame if it exists
        if hasattr(self, 'calcgame_task'):
            self.calcgame_task.cancel()


    async def receive(self, text_data):
        # Handle messages received from the client
        logger.debug(f"ProxyCalcGameInvite > receive from {self.channel_name}")
        logger.debug(f"ProxyCalcGameInvite > receive from client: {text_data}")
        data = json.loads(text_data)
        connect_id = self.channel_name

        if data['type'] == 'opening_connection, invite':
            # Client confirms connection with their player name
            game_type = data['game_type']
            if connect_id in self.waiting[game_type]:
                player = self.waiting[game_type][connect_id]
                player['player_name'] = data['p1_name']
                player['ready'] = False
                player['game_type'] = game_type
                player['player_id'] = player['context']['user']['user_id']
                player['queue_date'] = datetime.now()
                player['combined_id'] = f"{data['sender_id']}_{data['receiver_id']}"

                logger.debug(f"Updated waiting[{game_type}][connect_id] with player_name: {data['p1_name']}, player_id: {self.waiting[game_type][connect_id]['player_id']}, combined_id: {self.waiting[game_type][connect_id]['combined_id']}")
                # logger.debug(f"ProxyCalcGameInvite > opening_connection player: {pformat(player)}")
            else:
                logger.error(f"Player {connect_id} not found in waiting")

        elif data['type'] == 'player_ready':
            game = self.active_games[data['game_id']]
            
            # Mark player as ready
            if connect_id == game['player1']['channel_name']:
                game['player1']['ready'] = True
            elif connect_id == game['player2']['channel_name']:
                game['player2']['ready'] = True

            # notify other player that this player is ready
            if connect_id == game['player1']['channel_name']:
                await game['player2']['ws'].send(json.dumps({
                    'type': 'opponent_ready',
                    'game_id': data['game_id'],
                    'opponent': '1',
                }))
            elif connect_id == game['player2']['channel_name']:
                await game['player1']['ws'].send(json.dumps({
                    'type': 'opponent_ready',
                    'game_id': data['game_id'],
                    'opponent': '2',
                }))
            logger.debug(f"player1 ready: {game['player1']['ready']}, player2 ready: {game['player2']['ready']}")

            # If both players are ready, notify calcgame
            if game['player1']['ready'] and game['player2']['ready']:
                await game['calcgame_ws'].send(
                    json.dumps({
                        'type': 'players_ready',
                        'game_id': data['game_id'],
                    })
                )
            
        else:
            # Forward client message to calcgame websocket
            if data['game_id'] and data['game_id'] in self.active_games and 'calcgame_ws' in self.active_games[data['game_id']]:
                calcgame_ws = self.active_games[data['game_id']]['calcgame_ws']
                await calcgame_ws.send(text_data)

    async def listen_to_calcgame(self, game_id):
        try:
            while True:
                # Continuously receive messages from calcgame
                calcgame_ws = self.active_games[game_id]['calcgame_ws']
                calcgame_response = await calcgame_ws.recv()
                data = json.loads(calcgame_response)
                
                if not data['type'] == 'game_update' and data['message']:
                    logger.debug(f"ProxyCalcGameLocal > from calcgame: {data['message']}")
                    
                if data['type'] == 'connection_established, calcgame says hello':
                    # Connection established with calcgame, send back game info
                    player1 = self.active_games[game_id]['player1']
                    player2 = self.active_games[game_id]['player2']

                    text_data = json.dumps({
                        'type': 'opening_connection, game details',
                        'game_id': game_id,
                        'p1_name': player1['player_name'],
                        'p2_name': player2['player_name'],
                    })
                    logger.debug(f"ProxyCalcGameInvite > listen_to_calcgame:  p1_name: {player1['player_name']}, p2_name: {player2['player_name']}")
                    await calcgame_ws.send(text_data)

                    # Send message received from calcgame to both players
                    await player1['ws'].send(calcgame_response)
                    await player2['ws'].send(calcgame_response)       

                elif data['type'] == 'game_end':
                    # Game ended
                    await self.game_end(game_id, calcgame_response)
                    break

                else:
                    # Send message received from calcgame to both players
                    player1 = self.active_games[game_id]['player1']
                    player2 = self.active_games[game_id]['player2']
                    await player1['ws'].send(calcgame_response)
                    await player2['ws'].send(calcgame_response)                

        except websockets.exceptions.ConnectionClosed:
            logger.debug("ProxyCalcGameInvite > calcgame connection closed")
            pass

    async def waiting_room(self, context):
        logger.debug("ProxyCalcGameInvite > player in waiting_room")

        html = render_to_string('fragments/waiting_room.html', context=context)

        await self.send(json.dumps({
            'type': 'waiting_room',
            'message': 'Waiting for another player to join...',
            'html': html,
        }))

    async def game_end(self, game_id, calcgame_response):
        logger.debug(f"ProxyCalcGameInvite > game_end game_id: {game_id}")
        game = self.active_games[game_id]
        player1 = game['player1']
        player2 = game['player2']
        dataCalcgame = json.loads(calcgame_response)
        game_result = dataCalcgame.get('game_result')

        # Update winner name with actual name
        if game_result.get('game_winner_name') == 'p1_name':
            game_result['game_winner_name'] = player1['player_name']
        else:
            game_result['game_winner_name'] = player2['player_name']

        # Save game to database
        await self.save_game_to_database(game_id, game, player1, player2, game_result)

        # Notify players that the game has ended and send game_end html
        html1 = render_to_string('fragments/game_end_fragment.html', {
              'context': player1['context'],
              'game_result': game_result
            })
        html2 = render_to_string('fragments/game_end_fragment.html', {
              'context': player2['context'],
              'game_result': game_result
            })

        dataCalcgame['html'] = html1
        await player1['ws'].send(json.dumps(dataCalcgame))

        dataCalcgame['html'] = html2
        await player2['ws'].send(json.dumps(dataCalcgame))


    async def save_game_to_database(self, game_id, game, player1, player2, game_result):
        logger.debug(f"ProxyCalcGameInvite > save_game_to_database game_id: {game_id}")
        # Save game to database
        play_url = 'https://play:9003/api/saveGame/'
        csrf_token = player1['context']['cookies'].get('csrftoken')
        
        if player1['player_name'].endswith("#1"):
            player1['player_name'] = player1['player_name'][:-2]
        if player2['player_name'].endswith("#2"):
            player2['player_name'] = player2['player_name'][:-2]

        data = {
            'game_type': game['game_type'],
            'game_round': 'single',
            'p1_name': player1['player_name'],
            'p2_name': player2['player_name'],
            'p1_id': player1['player_id'],
            'p2_id': player2['player_id'],
            'p1_score': game_result.get('p1_score'),
            'p2_score': game_result.get('p2_score'),
            'game_winner_name': player1['player_name'] if game_result.get('game_winner_name') == player1['player_name'] else player2['player_name'],
            'game_winner_id': player1['player_id'] if game_result.get('game_winner_name') == player1['player_id'] else player2['player_id'],
        }
        
        await asyncRequest("POST", csrf_token, play_url, data)

        # Close the websocket connection to the calcgame service
        await game['calcgame_ws'].close()
        logger.debug(f"ProxyCalcGameInvite > calcgame_ws closed")

        # Remove the game from active_games
        self.active_games.pop(game_id)
        logger.debug("ProxyCalcGameInvite > game removed from active_games")


    async def close_game(self, game_id):
        logger.debug(f"ProxyCalcGameRemote > close_game game_id: {game_id}")
        game = self.active_games[game_id]
        player1 = game['player1']
        player2 = game['player2']

        # Close the WebSocket connection to the calcgame service
        await game['calcgame_ws'].close()

        # The disconnecting player forfeits the game
        if player1['channel_name'] == self.channel_name:
            disconnecting_player = player1
            remaining_player = player2
            game_result = {
                'p1_score': 0,
                'p2_score': 3,
            }
        else:
            disconnecting_player = player2
            remaining_player = player1
            game_result = {
                'p1_score': 3,
                'p2_score': 0,
            }

        game_result['game_id'] = game_id
        game_result['game_winner_name'] = remaining_player['player_name']

        # Save game to database
        await self.save_game_to_database(game_id, game, player1, player2, game_result)

        # Notify the remaining player that the game has ended
        html = render_to_string('fragments/game_end_fragment.html', {
              'context': remaining_player['context'],
              'game_result': game_result
            })

        await remaining_player['ws'].send(json.dumps({
            'type': 'disconnection',
            'game_result': game_result,
            'html': html,
            'title': _('Forfeit'),
            'message': _('Your opponent has disconnected'),
        }))