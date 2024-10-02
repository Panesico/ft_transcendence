// pong.js

const gameCalcSocket = new WebSocket('wss://localhost:8443/wss/gamecalc/');
// const gameCalcSocket = new WebSocket('/wss/gamecalc/');

gameCalcSocket.onopen = function(e) {
  console.log('GameCalc socket connected');
};

gameCalcSocket.onmessage = function(e) {
  const data = JSON.parse(e.data);
  const message = data['message'];
  console.log('Received message from socket: ', message);
};

gameCalcSocket.onclose = function(e) {
  console.error('GameCalc socket closed unexpectedly');
};

function sendMessage(message) {
  console.log('Sending message to socket: ', message);
  gameCalcSocket.send(JSON.stringify({'message': message}));
}

// Get the game container
const gameContainer = document.querySelector('.game-container');
const scorePlayer1Element = document.querySelector('.scorePlayer1');
const scorePlayer2Element = document.querySelector('.scorePlayer2');

// Set up the canvas
const canvas = document.createElement('canvas');
canvas.width = 650;
canvas.height = 450;
gameContainer.appendChild(canvas);
const ctx = canvas.getContext('2d');
ctx.fillStyle = '#d3d3d3';  // Set the fill color
ctx.strokeStyle = '#d3d3d3';

// Game variables
const maxScore = 2;
const ballSize = 15;
const paddleWidth = 15;
const paddleHeight = 80;
const borderWidth = 15;
let leftPaddleY = (canvas.height - paddleHeight) / 2;
let rightPaddleY = (canvas.height - paddleHeight) / 2;
let ballX = canvas.width / 2;
let ballY = canvas.height / 2;
let ballSpeedX = 6;  // 6
let ballSpeedY = 4;  // 4
const paddleSpeed = 10;
let scorePlayer1 = 0;
let scorePlayer2 = 0;
let frameCount = 0;        // frame count
let lastContactFrame = 0;  // last frame where ball made contact with paddle
let pauseFrameCount = 0;   // to avoid repeat pause key press
let gameStarted = false;
let gameEnded = false;
let gamePaused = false;

// Controls
const keys = {
  w: false,
  s: false,
  ArrowUp: false,
  ArrowDown: false,
  8: false,
  5: false,
  ' ': false,
  Escape: false
};

// Event listeners for controls
window.addEventListener('keydown', (e) => {
  // console.log('e.key: ', e.key);
  if (e.key in keys) {
    // console.log('e.key in keys: ', e.key);
    keys[e.key] = true;
  }
});
window.addEventListener('keyup', (e) => {
  if (e.key in keys) {
    keys[e.key] = false;
  }
});

async function resetAndStartGame() {
  scorePlayer1 = 0;
  scorePlayer2 = 0;
  scorePlayer1Element.textContent = scorePlayer1;
  scorePlayer2Element.textContent = scorePlayer2;
  gameStarted = true;
  gameEnded = false;

  leftPaddleY = (canvas.height - paddleHeight) / 2;
  rightPaddleY = (canvas.height - paddleHeight) / 2;
  ballSpeedX = (ballSpeedX > 0) ? -getRandomInt(4, 6) : getRandomInt(4, 6);
  ballSpeedY = (ballSpeedY > 0) ? -getRandomInt(1, 3) : getRandomInt(1, 3);

  await showCountdown();
  gameLoop();
}

// Display name of winner
function showWinner(winner) {
  ctx.font = '40px PixeloidSans';
  ctx.textAlign = 'center';
  ctx.fillText(`${winner} Wins!`, canvas.width / 2, canvas.height / 2 - 50);
}

async function saveGameResultInDatabase(winner) {
  let path = window.location.pathname;
  let url = '';
  // console.log('path: ', path);
  if (path === '/game/') {
    url = 'saveGame/';
  } else if (path === '/game') {
    url = path + '/saveGame/';
  }
  // console.log('url: ', url);
  player1_name = document.getElementById('namePlayer1').textContent
  player2_name = document.getElementById('namePlayer2').textContent
  // player1_id, player2_id

  const jsonData = {
    'game_type': 'Pong',
    'game_round': 'Single',
    'player1_name': player1_name,
    'player2_name': player2_name,
    'score_player1': scorePlayer1,
    'score_player2': scorePlayer2,
    'winner': winner,
  };

  let request = new Request(url, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': getCookie('csrftoken')
    },
    credentials: 'include',
    body: JSON.stringify(jsonData)
  });
  const response = await fetch(request);
  // console.log('response: ', response);
  const data = await response.json();
  // console.log('data: ', data);
}

// Display winner splash screen with "Play Again" button
function playAgain(winner, displayWinner) {
  gameEnded = true;

  ctx.clearRect(0, 0, canvas.width, canvas.height);  // Clear the canvas

  // Display winner's name if displayWinner is true
  if (displayWinner) {
    showWinner(winner);
    saveGameResultInDatabase(winner);
  }

  // Display "Play Again" button
  ctx.font = '30px PixeloidSans';
  ctx.fillText('Play Again', canvas.width / 2, canvas.height / 2 + 50);

  // Draw rectangle around "Play Again" text
  const buttonX = canvas.width / 2 - 106;
  const buttonY = canvas.height / 2 + 50;
  const buttonWidth = 210;
  const buttonHeight = 70;
  ctx.lineWidth = 4;
  ctx.strokeRect(
      buttonX, buttonY - buttonHeight / 2, buttonWidth, buttonHeight);

  // Event listener to play again
  canvas.addEventListener('click', playAgainClickHandler);
}

// Click handler for "Play Again"
function playAgainClickHandler(event) {
  if (!gameEnded) return;

  const rect = canvas.getBoundingClientRect();
  const mouseX = event.clientX - rect.left;
  const mouseY = event.clientY - rect.top;

  const buttonX = canvas.width / 2 - 106;
  const buttonY = canvas.height / 2 + 50;
  const buttonWidth = 210;
  const buttonHeight = 70;

  // Check if the click is inside the "Play Again" button
  if (mouseX >= buttonX && mouseX <= buttonX + buttonWidth &&
      mouseY >= buttonY && mouseY <= buttonY + buttonHeight) {
    // Remove the event listener
    canvas.removeEventListener('click', playAgainClickHandler);

    resetAndStartGame();
  }
}

// Calculate coordinates for the paddles and ball
function calculatePaddleAndBallCoordinates() {
  // Move paddles
  if (keys.w && leftPaddleY > borderWidth) {
    leftPaddleY -= paddleSpeed;
  }
  if (keys.s && leftPaddleY < canvas.height - paddleHeight - borderWidth) {
    leftPaddleY += paddleSpeed;
  }
  if (keys.ArrowUp && rightPaddleY > borderWidth) {
    rightPaddleY -= paddleSpeed;
  }
  if (keys.ArrowDown &&
      rightPaddleY < canvas.height - paddleHeight - borderWidth) {
    rightPaddleY += paddleSpeed;
  }
  if (keys[8] && rightPaddleY > borderWidth) {
    rightPaddleY -= paddleSpeed;
  }
  if (keys[5] && rightPaddleY < canvas.height - paddleHeight - borderWidth) {
    rightPaddleY += paddleSpeed;
  }

  // Move ball
  ballX += ballSpeedX;
  ballY += ballSpeedY;

  // console.log('ballX: ', ballX, 'ballY: ', ballY);
}

function getRandomInt(min, max) {
  let int = Math.floor(Math.random() * (max - min + 1)) + min;
  return int;
}

// Check ball collision with paddles
function checkBallCollision() {
  // console.log(
  //     'ballX, ballY: ', ballX.toPrecision(4), ballY.toPrecision(4),
  //     'ballSpeedX, ballSpeedY: ', ballSpeedX.toPrecision(2),
  //     ballSpeedY.toPrecision(2), 'lastContactFrame: ', lastContactFrame,
  //     'frameCount: ', frameCount);

  // Ball collision with top and bottom canvas borders
  if (ballY <= borderWidth || ballY >= canvas.height - ballSize - borderWidth) {
    ballSpeedY = -ballSpeedY;
    sendMessage('Ball hit top or bottom border');
  }

  if (
      // Ball collision with left paddle
      (lastContactFrame < frameCount - 30      //
       && ballX <= 3 * paddleWidth             // ballX <= 60
       && ballX > 2 * paddleWidth              // ballX > 53
       && ballY + ballSize >= leftPaddleY      // ballY + 15 >= leftPaddleY
       && ballY <= leftPaddleY + paddleHeight  // ballY <= leftPaddleY + 80
       && ballSpeedX < 0)                      //
      ||                                   // Ball collision with right paddle
      (lastContactFrame < frameCount - 30  //
       && ballX >= canvas.width - 3 * paddleWidth - ballSize  // ballX >= 610
       && ballX < canvas.width - 2 * paddleWidth - ballSize   // ballX < 625
       && ballY + ballSize >= rightPaddleY                    //
       && ballY <= rightPaddleY + paddleHeight                //
       && ballSpeedX > 0)                                     //
  ) {
    lastContactFrame = frameCount;
    ballSpeedX = (ballSpeedX > 0) ? -getRandomInt(2, 14) : getRandomInt(2, 14);
    ballSpeedY = (ballSpeedY > 0) ? getRandomInt(4, 8) : -getRandomInt(4, 8);
  } else if (
      // Ball collision with sides of left paddle
      (lastContactFrame < frameCount - 50      //
       && ballX <= 3 * paddleWidth             // ballX <= 60
       && ballX > 2 * paddleWidth              // ballX > 45
       && ballY + ballSize >= leftPaddleY      // ballY + 15 >= leftPaddleY
       && ballY <= leftPaddleY + paddleHeight  // ballY <= leftPaddleY + 80
       && ballSpeedX < 0)                      //
      ||  // Ball collision with sides of right paddle
      (lastContactFrame < frameCount - 50                     //
       && ballX >= canvas.width - 3 * paddleWidth - ballSize  // ballX >= 610
       && ballX < canvas.width - 2 * paddleWidth - ballSize   // ballX < 625
       && ballY + ballSize >= rightPaddleY                    //
       && ballY <= rightPaddleY + paddleHeight                //
       && ballSpeedX > 0)                                     //
  ) {
    // check correct ball direction
    if ((ballSpeedY > 0 && ballY < leftPaddleY + paddleHeight / 2) ||
        (ballSpeedY < 0 && ballY > leftPaddleY + paddleHeight / 2)) {
      lastContactFrame = frameCount;
      ballSpeedY = (ballSpeedY > 0) ? -getRandomInt(4, 8) : getRandomInt(4, 8);
    }
  }

  // console.log(
  //     'ballSpeedX: ', ballSpeedX, 'ballSpeedY: ', ballSpeedY,
  //     'frameCount: ', frameCount);
}

// Check if ball out of bounds
function checkBallOutOfBounds() {
  // Update score
  if (ballX < 0) {
    scorePlayer2++;
    scorePlayer2Element.textContent = scorePlayer2;
  } else if (ballX > canvas.width) {
    scorePlayer1++;
    scorePlayer1Element.textContent = scorePlayer1;
  }

  // Reset ball position
  if (ballX < 0 || ballX > canvas.width) {
    ballX = canvas.width / 2;
    ballY = getRandomInt(-125, 125) + canvas.height / 2;
    ballSpeedX = (ballSpeedX > 0) ? -getRandomInt(4, 6) : getRandomInt(4, 6);
    ballSpeedY = (ballSpeedY > 0) ? -getRandomInt(1, 3) : getRandomInt(1, 3);
  }
}

// Check for winner
function checkWinner() {
  if (scorePlayer1 === maxScore) {
    playAgain('Player 1', true);
    return true;
  } else if (scorePlayer2 === maxScore) {
    playAgain('Player 2', true);
    return true;
  }
  return false;
}

// Draw canvas with playing field
function drawPlayCanvas() {
  // Clear canvas
  ctx.clearRect(0, 0, canvas.width, canvas.height);

  // Draw center line
  let centerLineY = 0;
  while (centerLineY < canvas.height) {
    ctx.fillRect(
        canvas.width / 2, centerLineY + 0.5 * borderWidth, 1, borderWidth);
    centerLineY += 2 * borderWidth;
  }

  // Draw top and bottom borders
  ctx.fillRect(0, 0, canvas.width, borderWidth);
  ctx.fillRect(0, canvas.height - borderWidth, canvas.width, borderWidth);

  // Draw the left paddle
  ctx.fillRect(2 * paddleWidth, leftPaddleY, paddleWidth, paddleHeight);
  // Draw the right paddle
  ctx.fillRect(
      canvas.width - 3 * paddleWidth, rightPaddleY, paddleWidth, paddleHeight);

  // Draw ball
  ctx.fillRect(ballX, ballY, ballSize, ballSize);
}

// Draw canvas with "Paused" text
function drawPauseCanvas() {
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  ctx.font = '20px PixeloidSans';
  ctx.textAlign = 'center';
  ctx.textBaseline = 'middle';
  ctx.fillText(
      'Paused (press Space to resume)', canvas.width / 2, canvas.height / 2);
}

// Game loop
function gameLoop() {
  frameCount++;

  if (keys[' '] && frameCount > pauseFrameCount + 10) {
    sendMessage('Game paused');
    gamePaused = !gamePaused;
    pauseFrameCount = frameCount;
  }
  if (keys.Escape) {
    playAgain('', false);
    return;
  }

  if (gamePaused) {
    drawPauseCanvas();
    requestAnimationFrame(gameLoop);
    return;
  }

  calculatePaddleAndBallCoordinates();

  checkBallCollision();

  checkBallOutOfBounds();

  // Check for winner and exit game loop if true
  if (checkWinner()) return;

  drawPlayCanvas();

  // Continue next frame
  requestAnimationFrame(gameLoop);
}

function delay(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

async function showCountdown() {
  let count = 3;

  while (count > 0) {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    ctx.font = '60px PixeloidSans';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillText(count, canvas.width / 2, canvas.height / 2);

    count--;
    await delay(800);
  }
}

// Draw the "Start" text on the canvas
function drawStartScreen() {
  // Draw "Start" text
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  ctx.font = '40px PixeloidSans';
  ctx.textAlign = 'center';
  ctx.textBaseline = 'middle';
  ctx.fillText('Start', canvas.width / 2, canvas.height / 2);

  // Draw rectangle around "Start" text
  const buttonX = canvas.width / 2 - 76;
  const buttonY = canvas.height / 2;
  const buttonWidth = 150;
  const buttonHeight = 70;
  ctx.lineWidth = 4;
  ctx.strokeRect(
      buttonX, buttonY - buttonHeight / 2 - 2, buttonWidth, buttonHeight);

  // Listen for click to start game
  canvas.addEventListener('click', async (event) => {
    if (!gameStarted) {
      // Get mouse coordinates with canvas offset
      const rect = canvas.getBoundingClientRect();
      const mouseX = event.clientX - rect.left;
      const mouseY = event.clientY - rect.top;

      if (mouseX >= buttonX && mouseX <= buttonX + buttonWidth &&
          mouseY >= buttonY && mouseY <= buttonY + buttonHeight) {
        resetAndStartGame();
      }
    }
  });
}

// Wait for fonts to load
document.fonts.ready.then(() => {
  drawStartScreen();
});