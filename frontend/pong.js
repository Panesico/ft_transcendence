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

// Game variables
const paddleWidth = 15;
const paddleHeight = 80;
const ballSize = 15;
let leftPaddleY = (canvas.height - paddleHeight) / 2;
let rightPaddleY = (canvas.height - paddleHeight) / 2;
let ballX = canvas.width / 2;
let ballY = canvas.height / 2;
let ballSpeedX = 1;  // 7
let ballSpeedY = 1;  // 5
const paddleSpeed = 7;
let scorePlayer1 = 0;
let scorePlayer2 = 0;

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

// Game loop
function gameLoop() {
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

  // Ball collision with top and bottom
  if (ballY <= paddleWidth || ballY >= canvas.height - ballSize - paddleWidth) {
    ballSpeedY = -ballSpeedY;
  }
  // Ball collision with paddles
  if (ballX <= 4 * paddleWidth && ballY >= leftPaddleY &&
      ballY <= leftPaddleY + paddleHeight) {
    ballSpeedX = -ballSpeedX;
    if (ballX <= 3 * paddleWidth) {
      ballSpeedY = -ballSpeedY;
    }
  }
  if (ballX >= canvas.width - 4 * paddleWidth - ballSize &&
      ballY >= rightPaddleY && ballY <= rightPaddleY + paddleHeight) {
    ballSpeedX = -ballSpeedX;
    if (ballX >= canvas.width - 3 * paddleWidth - ballSize) {
      ballSpeedY = -ballSpeedY;
    }
  }

  // If ball hits side of paddle
  // {
  //   ballSpeedX = -ballSpeedX;
  //   ballSpeedY = -ballSpeedY;
  // }

  // Ball out of bounds
  if (ballX < 0) {
    scorePlayer2++;
    scorePlayer2Element.textContent = scorePlayer2;
  }
  if (ballX > canvas.width) {
    scorePlayer1++;
    scorePlayer1Element.textContent = scorePlayer1;
  }
  if (ballX < 0 || ballX > canvas.width) {
    // Reset ball position
    ballX = canvas.width / 2;
    ballY = canvas.height / 2;
    ballSpeedX = -ballSpeedX;
  }

  // Clear canvas
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  ctx.fillStyle = '#d3d3d3';  // Set the fill color

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

  // Request next frame
  requestAnimationFrame(gameLoop);
}

// Start the game loop
gameLoop();
