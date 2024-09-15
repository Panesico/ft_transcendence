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
let count = 0;             // frame count
let lastContactCount = 0;  // last contact frame count
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
  ctx.font = '40px Arial';
  ctx.textAlign = 'center';
  ctx.fillText(`${winner} Wins!`, canvas.width / 2, canvas.height / 2 - 50);

  // Display "Play Again" button
  ctx.font = '30px Arial';
  ctx.fillText('Play Again', canvas.width / 2, canvas.height / 2 + 50);

  // Draw rectangle around "Play Again" text
  const buttonX = canvas.width / 2 - 85;   // Approximate X position
  const buttonY = canvas.height / 2 + 50;  // Y position of text
  const buttonWidth = 170;
  const buttonHeight = 70;
  ctx.strokeStyle = '#d3d3d3';
  ctx.lineWidth = 2;
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

  const buttonX = canvas.width / 2 - 75;
  const buttonY = canvas.height / 2 + 20;
  const buttonWidth = 150;
  const buttonHeight = 40;

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

// Game loop
function gameLoop() {
  count++;
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

  // console.log(
  //     'ballX, ballY: ', ballX.toPrecision(4), ballY.toPrecision(4),
  //     'ballSpeedX, ballSpeedY: ', ballSpeedX.toPrecision(2),
  //     ballSpeedY.toPrecision(2), 'lastContactCount: ', lastContactCount,
  //     'count: ', count);
  // Ball collision with left paddle
  if (lastContactCount < count - 50           //
      && ballX <= 3 * paddleWidth             // ballX <= 60
      && ballX > 3 * paddleWidth - 7          // ballX > 53
      && ballY + ballSize >= leftPaddleY      // ballY + 15 >= leftPaddleY
      && ballY <= leftPaddleY + paddleHeight  // ballY <= leftPaddleY + 80
      && ballSpeedX < 0) {
    lastContactCount = count;
    ballSpeedX = -ballSpeedX;
  }
  // Ball collision with sides of left paddle
  else if (
      lastContactCount < count - 50           //
      && ballX <= 3 * paddleWidth             // ballX <= 60
      && ballX > 2 * paddleWidth              // ballX > 45
      && ballY + ballSize >= leftPaddleY      // ballY + 15 >= leftPaddleY
      && ballY <= leftPaddleY + paddleHeight  // ballY <= leftPaddleY + 80
      && ballSpeedX < 0) {
    // check correct ball direction
    if ((ballSpeedY > 0 && ballY < leftPaddleY + paddleHeight / 2) ||
        (ballSpeedY < 0 && ballY > leftPaddleY + paddleHeight / 2)) {
      lastContactCount = count;
      ballSpeedY = -ballSpeedY;
    }
  }

  // Ball collision with right paddle
  if (lastContactCount < count - 50                             //
      && ballX >= canvas.width - 3 * paddleWidth - ballSize     // ballX >= 610
      && ballX < canvas.width - 3 * paddleWidth - ballSize + 7  // ballX < 617
      && ballY + ballSize >= rightPaddleY                       //
      && ballY <= rightPaddleY + paddleHeight                   //
      && ballSpeedX > 0) {
    lastContactCount = count;
    ballSpeedX = -ballSpeedX;
  }
  // Ball collision with sides of right paddle
  else if (
      lastContactCount < count - 50                          //
      && ballX >= canvas.width - 3 * paddleWidth - ballSize  // ballX >= 610
      && ballX < canvas.width - 2 * paddleWidth - ballSize   // ballX < 625
      && ballY + ballSize >= rightPaddleY                    //
      && ballY <= rightPaddleY + paddleHeight                //
      && ballSpeedX > 0) {
    // check correct ball direction
    if ((ballSpeedY > 0 && ballY < rightPaddleY + paddleHeight / 2) ||
        (ballSpeedY < 0 && ballY > rightPaddleY + paddleHeight / 2)) {
      lastContactCount = count;
      ballSpeedY = -ballSpeedY;
    }
  }

  // Ball out of bounds
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

  if (scorePlayer1 == 3) {
    showWinner('Player 1');
    return;
  } else if (scorePlayer2 == 3) {
    showWinner('Player 2');
    return;
  }
  // Clear canvas
  ctx.clearRect(0, 0, canvas.width, canvas.height);

  // Draw center line
  let centerLineY = 0;
  while (centerLineY < canvas.height) {
    ctx.fillRect(
        canvas.width / 2, centerLineY + 0.5 * paddleWidth, 1, paddleWidth);
    centerLineY += 2 * paddleWidth;
  }

  // // debug goal line
  // ctx.fillRect(canvas.width - 3 * paddleWidth, 0, 1, canvas.height);
  // ctx.fillRect(2 * paddleWidth, 0, 1, canvas.height);
  // ctx.fillRect(3 * paddleWidth, 0, 1, canvas.height);
  // // debug ball position
  // ctx.fillRect(ballX, 0, 1, canvas.height);
  // ctx.fillRect(0, ballY, canvas.width, 1);

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

  // Continue next frame
  requestAnimationFrame(gameLoop);
}

// Draw the "Start" text on the canvas
function drawStartScreen() {
  ctx.clearRect(0, 0, canvas.width, canvas.height);  // Clear the canvas
  ctx.fillStyle = '#d3d3d3';    // Set the fill color for the text
  ctx.font = '40px Arial';      // Set the font for the text
  ctx.textAlign = 'center';     // Center the text horizontally
  ctx.textBaseline = 'middle';  // Center the text vertically
  ctx.fillText('Start', canvas.width / 2, canvas.height / 2);  // Draw "Start"

  // Draw rectangle around "Start" text
  const buttonX = canvas.width / 2 - 70;  // Approximate X position
  const buttonY = canvas.height / 2;      // Y position of text
  const buttonWidth = 145;
  const buttonHeight = 70;
  ctx.strokeStyle = '#d3d3d3';
  ctx.lineWidth = 2;
  ctx.strokeRect(
      buttonX, buttonY - buttonHeight / 2, buttonWidth, buttonHeight);
}

// Event listener for user click on the canvas
canvas.addEventListener('click', function(event) {
  if (!gameStarted) {
    const rect = canvas.getBoundingClientRect();
    const mouseX = event.clientX - rect.left;
    const mouseY = event.clientY - rect.top;

    // Check if click is within the "Start" text bounds (simple box around text)
    const startX = canvas.width / 2 - 50;
    const startY = canvas.height / 2 - 30;
    const textWidth = 100;
    const textHeight = 60;

    if (mouseX >= startX && mouseX <= startX + textWidth && mouseY >= startY &&
        mouseY <= startY + textHeight) {
      gameStarted = true;
      gameLoop();
    }
  }
});

drawStartScreen();
