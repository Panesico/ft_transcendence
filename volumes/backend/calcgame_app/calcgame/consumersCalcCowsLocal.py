import json, asyncio, logging
from channels.generic.websocket import AsyncWebsocketConsumer 
from .consumersCalcPongUtils import update_ball_pos, check_ball_border_collision, check_ball_paddle_collision, check_ball_outofbounds, reset_ball_position
logger = logging.getLogger(__name__)

class CowsCalcLocal(AsyncWebsocketConsumer):

  async def connect(self):
    # Accept the WebSocket connection
    await self.accept()
    logger.debug("CowsCalcLocal > Client connected")
    # Send an initial message to confirm the connection
    await self.send(text_data=json.dumps({
      'type': 'connection_established, calcgame says hello',
      'message': 'You are connected!'
    }))

  async def disconnect(self, close_code):
    # Handle WebSocket disconnection
    logger.debug("CowsCalcLocal > Client disconnected")
    pass

  async def receive(self, text_data):
    # Handle messages received from the client
    data = json.loads(text_data)
    logger.debug(f"CowsCalcLocal > received data: {data}")
    
    # if data['type'] == 'opening_connection, game details':
    #    self.p1_name = data['p1_name']
    #    self.p2_name = data['p2_name']
    #    logger.debug(f"CowsCalcLocal > opening_connection with players: {self.p1_name}, {self.p2_name}")

    # if data['type'] == 'players_ready':
    #     await self.start_game()

    # if data['type'] == 'key_press':
    #   # logger.debug("CowsCalcLocal > key press event")
    #   self.update_pressed_keys(data['keys'])