// pong.js

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
const paddleWidth = 15;
const paddleHeight = 80;
const ballSize = 15;
let leftPaddleY = (canvas.height - paddleHeight) / 2;
let rightPaddleY = (canvas.height - paddleHeight) / 2;
let ballX = canvas.width / 2;
let ballY = canvas.height / 2;
let ballSpeedX = 6;  // 6
let ballSpeedY = 4;  // 4
const paddleSpeed = 7;
let scorePlayer1 = 0;
let scorePlayer2 = 0;
let frameCount = 0;        // frame count
let lastContactFrame = 0;  // last frame where ball made contact with paddle
let gameStarted = false;
let gameEnded = false;

// Controls
const keys = {
  w: false,
  s: false,
  ArrowUp: false,
  ArrowDown: false
};

// Event listeners for controls
window.addEventListener('keydown', (e) => {
  if (e.key in keys) {
    keys[e.key] = true;
  }
});
window.addEventListener('keyup', (e) => {
  if (e.key in keys) {
    keys[e.key] = false;
  }
});

// Display winner splash screen with "Play Again" button
function showWinner(winner) {
  gameEnded = true;

  ctx.clearRect(0, 0, canvas.width, canvas.height);  // Clear the canvas

  // Display winner text
  ctx.fillStyle = '#d3d3d3';
  ctx.font = '40px PixeloidSans';
  ctx.textAlign = 'center';
  ctx.fillText(`${winner} Wins!`, canvas.width / 2, canvas.height / 2 - 50);

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

  // Listen for click to play again
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
    // Reset game state
    scorePlayer1 = 0;
    scorePlayer2 = 0;
    scorePlayer1Element.textContent = scorePlayer1;
    scorePlayer2Element.textContent = scorePlayer2;
    gameStarted = false;
    gameEnded = false;

    // Remove the event listener
    canvas.removeEventListener('click', playAgainClickHandler);

    // Start the game again
    gameStarted = true;
    gameLoop();
  }
}

// Calculate coordinates for the paddles and ball
function calculatePaddleAndBallCoordinates() {
  // Move paddles
  if (keys.w && leftPaddleY > paddleWidth) {
    leftPaddleY -= paddleSpeed;
  }
  if (keys.s && leftPaddleY < canvas.height - paddleHeight - paddleWidth) {
    leftPaddleY += paddleSpeed;
  }
  if (keys.ArrowUp && rightPaddleY > paddleWidth) {
    rightPaddleY -= paddleSpeed;
  }
  if (keys.ArrowDown &&
      rightPaddleY < canvas.height - paddleHeight - paddleWidth) {
    rightPaddleY += paddleSpeed;
  }

  // Move ball
  ballX += ballSpeedX;
  ballY += ballSpeedY;
}

// Check ball collision with paddles
function checkBallCollision() {
  // console.log(
  //     'ballX, ballY: ', ballX.toPrecision(4), ballY.toPrecision(4),
  //     'ballSpeedX, ballSpeedY: ', ballSpeedX.toPrecision(2),
  //     ballSpeedY.toPrecision(2), 'lastContactFrame: ', lastContactFrame,
  //     'frameCount: ', frameCount);

  // Ball collision with top and bottom canvas borders
  if (ballY <= paddleWidth || ballY >= canvas.height - ballSize - paddleWidth) {
    ballSpeedY = -ballSpeedY;
  }

  // Ball collision with left paddle
  if (lastContactFrame < frameCount - 50      //
      && ballX <= 3 * paddleWidth             // ballX <= 60
      && ballX > 3 * paddleWidth - 7          // ballX > 53
      && ballY + ballSize >= leftPaddleY      // ballY + 15 >= leftPaddleY
      && ballY <= leftPaddleY + paddleHeight  // ballY <= leftPaddleY + 80
      && ballSpeedX < 0) {
    lastContactFrame = frameCount;
    ballSpeedX = -ballSpeedX;
  }
  // Ball collision with sides of left paddle
  else if (
      lastContactFrame < frameCount - 50      //
      && ballX <= 3 * paddleWidth             // ballX <= 60
      && ballX > 2 * paddleWidth              // ballX > 45
      && ballY + ballSize >= leftPaddleY      // ballY + 15 >= leftPaddleY
      && ballY <= leftPaddleY + paddleHeight  // ballY <= leftPaddleY + 80
      && ballSpeedX < 0) {
    // check correct ball direction
    if ((ballSpeedY > 0 && ballY < leftPaddleY + paddleHeight / 2) ||
        (ballSpeedY < 0 && ballY > leftPaddleY + paddleHeight / 2)) {
      lastContactFrame = frameCount;
      ballSpeedY = -ballSpeedY;
    }
  }

  // Ball collision with right paddle
  if (lastContactFrame < frameCount - 50                        //
      && ballX >= canvas.width - 3 * paddleWidth - ballSize     // ballX >= 610
      && ballX < canvas.width - 3 * paddleWidth - ballSize + 7  // ballX < 617
      && ballY + ballSize >= rightPaddleY                       //
      && ballY <= rightPaddleY + paddleHeight                   //
      && ballSpeedX > 0) {
    lastContactFrame = frameCount;
    ballSpeedX = -ballSpeedX;
  }
  // Ball collision with sides of right paddle
  else if (
      lastContactFrame < frameCount - 50                     //
      && ballX >= canvas.width - 3 * paddleWidth - ballSize  // ballX >= 610
      && ballX < canvas.width - 2 * paddleWidth - ballSize   // ballX < 625
      && ballY + ballSize >= rightPaddleY                    //
      && ballY <= rightPaddleY + paddleHeight                //
      && ballSpeedX > 0) {
    // check correct ball direction
    if ((ballSpeedY > 0 && ballY < rightPaddleY + paddleHeight / 2) ||
        (ballSpeedY < 0 && ballY > rightPaddleY + paddleHeight / 2)) {
      lastContactFrame = frameCount;
      ballSpeedY = -ballSpeedY;
    }
  }
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
    ballY = canvas.height / 2;
    ballSpeedX = -ballSpeedX;
  }
}

function checkWinner() {
  // Check for winner
  if (scorePlayer1 == 3) {
    showWinner('Player 1');
    return true;
  } else if (scorePlayer2 == 3) {
    showWinner('Player 2');
    return true;
  }
  return false;
}

function drawCanvas() {
  // Clear canvas
  ctx.clearRect(0, 0, canvas.width, canvas.height);

  // // debug draw goal lines
  // ctx.fillRect(canvas.width - 3 * paddleWidth, 0, 1, canvas.height);
  // ctx.fillRect(2 * paddleWidth, 0, 1, canvas.height);
  // ctx.fillRect(3 * paddleWidth, 0, 1, canvas.height);
  // // debug ball position
  // ctx.fillRect(ballX, 0, 1, canvas.height);
  // ctx.fillRect(0, ballY, canvas.width, 1);

  // Draw center line
  let centerLineY = 0;
  while (centerLineY < canvas.height) {
    ctx.fillRect(
        canvas.width / 2, centerLineY + 0.5 * paddleWidth, 1, paddleWidth);
    centerLineY += 2 * paddleWidth;
  }

  // Draw top and bottom borders
  ctx.fillRect(0, 0, canvas.width, paddleWidth);
  ctx.fillRect(0, canvas.height - paddleWidth, canvas.width, paddleWidth);

  // Draw the left paddle
  ctx.fillRect(2 * paddleWidth, leftPaddleY, paddleWidth, paddleHeight);
  // Draw the right paddle
  ctx.fillRect(
      canvas.width - 3 * paddleWidth, rightPaddleY, paddleWidth, paddleHeight);

  // Draw ball
  ctx.fillRect(ballX, ballY, ballSize, ballSize);
}

// Game loop
function gameLoop() {
  frameCount++;
  // // show mouse cursor coordinates
  // {
  //   onmousemove = (event) => {
  //     const rect = canvas.getBoundingClientRect();
  //     const mouseX = event.clientX - rect.left;
  //     const mouseY = event.clientY - rect.top;
  //     console.log('mouseX, mouseY: ', mouseX, mouseY);
  //   };
  // }

  calculatePaddleAndBallCoordinates();

  checkBallCollision();

  checkBallOutOfBounds();

  // Check for winner and exit game loop if true
  if (checkWinner()) return;

  drawCanvas();

  // Continue next frame
  requestAnimationFrame(gameLoop);
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
      buttonX, buttonY - buttonHeight / 2, buttonWidth, buttonHeight);

  // Listen for click to start game
  canvas.addEventListener('click', (event) => {
    if (!gameStarted) {
      // Get mouse coordinates with canvas offset
      const rect = canvas.getBoundingClientRect();
      const mouseX = event.clientX - rect.left;
      const mouseY = event.clientY - rect.top;

      if (mouseX >= buttonX && mouseX <= buttonX + buttonWidth &&
          mouseY >= buttonY && mouseY <= buttonY + buttonHeight) {
        gameStarted = true;
        gameLoop();
      }
    }
  });
}

drawStartScreen();
