import logging, random
logger = logging.getLogger(__name__)

def getRandomInt(min, max):
  return int((max - min + 1) * random.random() + min)

def update_ball_pos(gs):
  gs['ballX'] += gs['ballSpeedX']
  gs['ballY'] += gs['ballSpeedY']

def check_ball_border_collision(gs, cfg):
  if gs['ballY'] <= cfg['borderWidth'] \
      or gs['ballY'] >= cfg['canvas']['height'] - cfg['ballSize'] - cfg['borderWidth']:
      logger.debug("PongCalcLocal > Ball hits the top or bottom wall")
      gs['ballSpeedY'] = -gs['ballSpeedY']

def check_ball_paddle_collision(gs, cfg, frameCount, lastContactFrame):
  # Check if the ball hits the left paddle
  if gs['ballX'] <= cfg['borderWidth'] + cfg['paddleWidth'] \
      and gs['ballY'] >= gs['leftPaddleY'] \
      and gs['ballY'] <= gs['leftPaddleY'] + cfg['paddleHeight']:
    logger.debug("PongCalcLocal > Ball hits the left paddle")
    gs['ballSpeedX'] = -gs['ballSpeedX']
    lastContactFrame = frameCount

  # Check if the ball hits the right
  if gs['ballX'] >= cfg['canvas']['width'] - cfg['borderWidth'] - cfg['paddleWidth'] - cfg['ballSize'] \
      and gs['ballY'] >= gs['rightPaddleY'] \
      and gs['ballY'] <= gs['rightPaddleY'] + cfg['paddleHeight']:
    logger.debug("PongCalcLocal > Ball hits the right paddle")
    gs['ballSpeedX'] = -gs['ballSpeedX']
    lastContactFrame = frameCount

def check_ball_outofbounds(gs, cfg):
  # Check if the ball is out of bounds
  if gs['ballX'] < 0:
    logger.debug("PongCalcLocal > Ball is out of bounds")
    gs['scorePlayer2'] += 1
    return True
  elif gs['ballX'] >= cfg['canvas']['width'] - cfg['ballSize']:
    logger.debug("PongCalcLocal > Ball is out of bounds")
    gs['scorePlayer1'] += 1
    return True
  return False

def reset_ball_position(gs, cfg):
  logger.debug("PongCalcLocal > reset_ball_position")
  gs['ballX'] = cfg['canvas']['width'] / 2
  gs['ballY'] = getRandomInt(-125, 125) + cfg['canvas']['height'] / 2
  gs['ballSpeedX'] = -getRandomInt(4, 6) if gs['ballSpeedX'] > 0 else getRandomInt(4, 6)
  gs['ballSpeedY'] = -getRandomInt(1, 3) if gs['ballSpeedY'] > 0 else getRandomInt(1, 3)

