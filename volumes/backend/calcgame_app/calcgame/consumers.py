import json, asyncio, logging, random
from channels.generic.websocket import AsyncWebsocketConsumer 
logger = logging.getLogger(__name__)

def getRandomInt(min, max):
  return int((max - min + 1) * random.random() + min)

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

  frameCount = 0;        # frame count
  lastContactFrame = 0;  # last frame where ball made contact with paddle
  pauseFrameCount = 0;   # to avoid repeat pause key press
  gamePaused = False;

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
    logger.debug("PongCalcConsumer > before accept")
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
    pass

  async def receive(self, text_data):
    # Handle messages received from the client
    data = json.loads(text_data)
    logger.debug(f"PongCalcConsumer > received data: {data}")
    
    if data['type'] == 'opening_connection':
       self.p1_name = data['p1_name']
       self.p2_name = data['p2_name']
       logger.debug(f"PongCalcConsumer > Opening connection with players: {self.p1_name}, {self.p2_name}")
    if data['type'] == 'key_press':
      # logger.debug("PongCalcConsumer > key press event")
      self.update_pressed_keys(data['keys'])

    if data['type'] == 'game_start':
        await self.start_game()

  async def start_game(self):
    # Start the game and send initial game state to the client
    logger.debug("PongCalcConsumer > Game started")
    await self.send(text_data=json.dumps({
      'type': 'game_start',
      'message': 'Game started!',
      "game_state": self.gs,
    }))
    
    # Start the game loop as a task
    self.game_task = asyncio.create_task(self.game_loop())

  async def game_end(self):
    logger.debug("PongCalcConsumer > Game ended")
    winner = self.p1_name if self.gs['scorePlayer1'] > self.gs['scorePlayer2'] else self.p2_name

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
    if hasattr(self, 'game_task'):
      self.game_task.cancel()


  async def game_loop(self):
      while True:
          # Wait before continuing the loop (in seconds)
          await asyncio.sleep(0.02)

          self.update_paddle_pos()
          self.update_ball_pos()
          self.check_ball_border_collision()
          self.check_ball_paddle_collision() # to update
          if self.check_ball_outofbounds() == True: 
            logger.debug("PongCalcConsumer > resetting ball position...")
            self.reset_ball_position()

          # Break loop and end game if a player reaches the max score
          if self.gs['scorePlayer1'] >= self.maxScore or self.gs['scorePlayer2'] >= self.maxScore:
            logger.debug("PongCalcConsumer > Ending game...")
            break
          
          # Send the updated game state to the client
          await self.send(text_data=json.dumps({
              'type': 'game_update',
              'game_state': self.gs
            }))
          logger.debug(f"Sent game_update, game_state: {self.gs}")
          
      await self.game_end()

  def update_pressed_keys(self, keys):
      # Update the set of pressed keys
      self.pressed_keys = {key: True for key in keys}

  def update_paddle_pos(self):
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

  def update_ball_pos(self):
    self.gs['ballX'] += self.gs['ballSpeedX']
    self.gs['ballY'] += self.gs['ballSpeedY']
  
  def check_ball_border_collision(self):
     if self.gs['ballY'] <= self.borderWidth \
        or self.gs['ballY'] >= self.canvas['height'] - self.ballSize - self.borderWidth:
      logger.debug("PongCalcConsumer > Ball hits the top or bottom wall")
      self.gs['ballSpeedY'] = -self.gs['ballSpeedY']

  def check_ball_paddle_collision(self):
    # Check if the ball hits the left paddle
    if self.gs['ballX'] <= self.borderWidth + self.paddleWidth \
        and self.gs['ballY'] >= self.gs['leftPaddleY'] \
        and self.gs['ballY'] <= self.gs['leftPaddleY'] + self.paddleHeight:
      logger.debug("PongCalcConsumer > Ball hits the left paddle")
      self.gs['ballSpeedX'] = -self.gs['ballSpeedX']
      self.lastContactFrame = self.frameCount

    # Check if the ball hits the right
    if self.gs['ballX'] >= self.canvas['width'] - self.borderWidth - self.paddleWidth - self.ballSize \
        and self.gs['ballY'] >= self.gs['rightPaddleY'] \
        and self.gs['ballY'] <= self.gs['rightPaddleY'] + self.paddleHeight:
      logger.debug("PongCalcConsumer > Ball hits the right paddle")
      self.gs['ballSpeedX'] = -self.gs['ballSpeedX']
      self.lastContactFrame = self.frameCount

  def check_ball_outofbounds(self):
    # Check if the ball is out of bounds
    if self.gs['ballX'] < 0:
      logger.debug("PongCalcConsumer > Ball is out of bounds")
      self.gs['scorePlayer2'] += 1
      return True
    elif self.gs['ballX'] >= self.canvas['width'] - self.ballSize:
      logger.debug("PongCalcConsumer > Ball is out of bounds")
      self.gs['scorePlayer1'] += 1
      return True
    return False
  
  def reset_ball_position(self):
    logger.debug("PongCalcConsumer > reset_ball_position")
    self.gs['ballX'] = self.canvas['width'] / 2
    self.gs['ballY'] = getRandomInt(-125, 125) + self.canvas['height'] / 2
    self.gs['ballSpeedX'] = -getRandomInt(4, 6) if self.gs['ballSpeedX'] > 0 else getRandomInt(4, 6)
    self.gs['ballSpeedY'] = -getRandomInt(1, 3) if self.gs['ballSpeedY'] > 0 else getRandomInt(1, 3)


