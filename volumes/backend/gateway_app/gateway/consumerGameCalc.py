import json, asyncio, logging
from channels.generic.websocket import AsyncWebsocketConsumer 
logger = logging.getLogger(__name__)

class PongCalcConsumer(AsyncWebsocketConsumer):
  canvas = {
    "width": 900,
    "height": 550,
  }
  maxScore = 2
  ballSize = 15
  paddleWidth = 15
  paddleHeight = 80
  borderWidth = 15
  paddleSpeed = 10

  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self.pressed_keys = set()
    # Game state
    self.gs = {
        "leftPaddleY": (self.canvas['height'] - self.paddleHeight) / 2,
        "rightPaddleY": (self.canvas['height'] - self.paddleHeight) / 2,
        "ballX": self.canvas['width'] / 2,
        "ballY": self.canvas['height'] / 2,
        "ballSpeedX": 6,
        "ballSpeedY": 4,
        "scorePlayer1": 0,
        "scorePlayer2": 0,
      }
    
  async def connect(self):
    # Accept the WebSocket connection
    await self.accept()
    logger.debug("PongCalcConsumer > Client connected")
    # Send an initial message to confirm the connection
    await self.send(text_data=json.dumps({
      'type': 'connection_established',
      'message': 'You are connected!'
    }))

  async def disconnect(self, close_code):
    # Handle WebSocket disconnection
    logger.debug("PongCalcConsumer > Client disconnected")
    # Cancel the game task if it's still running
    if hasattr(self, 'game_task'):
        self.game_task.cancel()

  async def receive(self, text_data):
    # Handle messages received from the client
    logger.debug(f"PongCalcConsumer> message received from client: {text_data}")
    data = json.loads(text_data)
    logger.debug(f"PongCalcConsumer > data: {data}")
    
    if data['type'] == 'key_press':
      logger.debug("PongCalcConsumer > key press event")
      self.update_pressed_keys(data['keys'])

    if data['type'] == 'game_start':
        await self.start_game()

  async def start_game(self):
    # Start the game
    logger.debug("PongCalcConsumer > Game started")
    await self.send(text_data=json.dumps({
      'type': 'game_start',
      'message': 'Game started!',
      "game_state": self.gs,
    }))
    # await self.game_loop()
    self.game_task = asyncio.create_task(self.game_loop())

  async def game_end(self):
    logger.debug("PongCalcConsumer > Game ended")
    winner = "Player 1" if self.gs['scorePlayer1'] > self.gs['scorePlayer2'] else "Player 2"

    # End the game
    await self.send(text_data=json.dumps({
      'type': 'game_end',
      'message': f'Game Over: {winner} wins!',
      'game_result': {
          'winner': winner,
          'scorePlayer1': self.gs['scorePlayer1'],
          'scorePlayer2': self.gs['scorePlayer2'],
        }
    }))

    # Cancel the game loop task
    self.game_task.cancel()

  async def game_loop(self):
      while True:
          # Wait before continuing the loop (in seconds)
          await asyncio.sleep(0.02)

          self.update_paddle_pos()
          
          self.gs['ballX'] += self.gs['ballSpeedX']
          self.gs['ballY'] += self.gs['ballSpeedY']

          # Check if the ball hits the top or bottom wall
          logger.debug(f"PongCalcConsumer > ballY: {self.gs['ballY']}, self.canvas['height'] - self.borderWidth: {self.canvas['height'] - self.borderWidth}")
          if self.gs['ballY'] <= self.borderWidth \
              or self.gs['ballY'] >= self.canvas['height'] - 2 * self.borderWidth:
            logger.debug("PongCalcConsumer > Ball hits the top or bottom wall")
            self.gs['ballSpeedY'] = -self.gs['ballSpeedY']
          
          # Check if the ball is out of bounds
          if self.gs['ballX'] < 0:
            self.gs['scorePlayer2'] += 1
          elif self.gs['ballX'] >= self.canvas['width'] - self.ballSize:
            self.gs['scorePlayer1'] += 1
            break

          # Send the updated game state to the client
          await self.send(text_data=json.dumps({
              'type': 'game_update',
              'game_state': self.gs
            }))
          
      await self.game_end()

  def update_pressed_keys(self, keys):
      # Update the set of pressed keys
      self.pressed_keys = {key: True for key in keys}

  def update_paddle_pos(self):
    logger.debug("PongCalcConsumer > update_paddle_pos")
    if 'w' in self.pressed_keys and self.gs['leftPaddleY'] > self.borderWidth:
        logger.debug("PongCalcConsumer > update_paddle_pos > w pressed")
      # if player == 'left':
        self.gs['leftPaddleY'] -= self.paddleSpeed
      # elif player == 'right':
      #   self.gs['rightPaddleY'] -= self.paddleSpeed
    
    if 's' in self.pressed_keys and self.gs['leftPaddleY'] < self.canvas['height'] - self.paddleHeight - self.borderWidth:
        self.gs['leftPaddleY'] += self.paddleSpeed

    if '8' in self.pressed_keys and self.gs['rightPaddleY'] > self.borderWidth:
        self.gs['rightPaddleY'] -= self.paddleSpeed

    if '5' in self.pressed_keys and self.gs['rightPaddleY'] < self.canvas['height'] - self.paddleHeight - self.borderWidth:
        self.gs['rightPaddleY'] += self.paddleSpeed

