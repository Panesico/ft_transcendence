// pong.js

// const gameCalcSocket = new
// WebSocket('wss://localhost:8443/wss/gamecalc/pong/');
// // const gameCalcSocket = new WebSocket('/wss/gamecalc/pong/');

// gameCalcSocket.onopen = function(e) {
//   console.log('GameCalc socket connected');
// };

// gameCalcSocket.onmessage = function(e) {
//   const data = JSON.parse(e.data);
//   const message = data['message'];
//   console.log('Received message from socket: ', message);
// };

// gameCalcSocket.onclose = function(e) {
//   console.error('GameCalc socket closed unexpectedly');
// };

// function sendMessage(message) {
//   console.log('Sending message to socket: ', message);
//   gameCalcSocket.send(JSON.stringify({'message': message}));
// }

async function executePongGame(p1_name, p2_name) {
  // Get the game container
  const gameContainer = document.querySelector('#game-container');
  const scorePlayer1Element = document.querySelector('.scorePlayer1');
  const scorePlayer2Element = document.querySelector('.scorePlayer2');
  scorePlayer1Element.textContent = 0;
  scorePlayer2Element.textContent = 0;

  // Set up the canvas
  const canvas = document.createElement('canvas');
  canvas.width = 900;
  canvas.height = 550;
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
  const paddleSpeed = 10;
  let leftPaddleY = (canvas.height - paddleHeight) / 2;
  let rightPaddleY = (canvas.height - paddleHeight) / 2;
  let ballX = canvas.width / 2;
  let ballY = canvas.height / 2;
  let ballSpeedX = 6;  // 6
  let ballSpeedY = 4;  // 4
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
    if (ballY <= borderWidth ||
        ballY >= canvas.height - ballSize - borderWidth) {
      ballSpeedY = -ballSpeedY;
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
      ballSpeedX =
          (ballSpeedX > 0) ? -getRandomInt(2, 14) : getRandomInt(2, 14);
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
        ballSpeedY =
            (ballSpeedY > 0) ? -getRandomInt(4, 8) : getRandomInt(4, 8);
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
        canvas.width - 3 * paddleWidth, rightPaddleY, paddleWidth,
        paddleHeight);

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
  function gameLoop(resolve) {
    frameCount++;

    // Toggle pause game if spacebar or escape is pressed
    if ((keys[' '] || keys.Escape) && frameCount > pauseFrameCount + 10) {
      gamePaused = !gamePaused;
      pauseFrameCount = frameCount;
    }

    if (gamePaused) {
      drawPauseCanvas();
      requestAnimationFrame(() => gameLoop(resolve));
      return;
    }

    calculatePaddleAndBallCoordinates();

    checkBallCollision();

    checkBallOutOfBounds();

    // ----- Exit game if maxScore is reached -----
    if (scorePlayer1 === maxScore || scorePlayer2 === maxScore) {
      gameEnded = true;
      const game_result = {
        'winner': (scorePlayer1 === maxScore) ? p1_name : p2_name,
        'scorePlayer1': scorePlayer1,
        'scorePlayer2': scorePlayer2
      };
      // return (game_result);
      resolve(game_result);
      return;
    }

    drawPlayCanvas();

    // Continue next frame
    requestAnimationFrame(() => gameLoop(resolve));
  }

  async function showCountdown() {
    let count = 3;

    function delay(ms) {
      return new Promise(resolve => setTimeout(resolve, ms));
    }

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

    return new Promise(resolve => {
      gameLoop(resolve);
    });
  }

  const game_result = await resetAndStartGame();
  console.log('Game ended');
  return game_result;
}
