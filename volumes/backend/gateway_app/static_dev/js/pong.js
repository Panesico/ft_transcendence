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

  const ballSize = 15
  const paddleWidth = 15
  const paddleHeight = 80
  const borderWidth = 15

  const keys =
      {w: false, s: false, 8: false, 5: false, ' ': false, Escape: false};


  function showCountdown(gameState, count) {
    scorePlayer1Element.textContent = gameState.scorePlayer1;
    scorePlayer2Element.textContent = gameState.scorePlayer2;

    ctx.clearRect(0, 0, canvas.width, canvas.height);
    ctx.font = '60px PixeloidSans';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillText(count, canvas.width / 2, canvas.height / 2);
  }

  // Render the game state on the canvas
  function renderGame(gameState) {
    scorePlayer1Element.textContent = gameState.scorePlayer1;
    scorePlayer2Element.textContent = gameState.scorePlayer2;

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
    ctx.fillRect(
        2 * paddleWidth, gameState.leftPaddleY, paddleWidth, paddleHeight);
    // Draw the right paddle
    ctx.fillRect(
        canvas.width - 3 * paddleWidth, gameState.rightPaddleY, paddleWidth,
        paddleHeight);

    // Draw ball
    ctx.fillRect(gameState.ballX, gameState.ballY, ballSize, ballSize);
  }

  return new Promise((resolve, reject) => {
    const gameCalcSocket = new WebSocket('/wss/calcgame/pong/local/');

    // Handle connection open
    gameCalcSocket.onopen = function(e) {
      console.log('gameCalcSocket WebSocket connection established.');
      // Start the game
      gameCalcSocket.send(JSON.stringify(
          {type: 'opening_connection', p1_name: p1_name, p2_name: p2_name}));
    };

    // Handle messages from the server
    gameCalcSocket.onmessage = function(e) {
      const data = JSON.parse(e.data);

      if (data.type === 'connection_established') {
        // Start the game
        gameCalcSocket.send(JSON.stringify({type: 'game_start'}));

      } else if (data.type === 'game_start') {
        console.log('Game start received', data);
        showCountdown(data.game_state, data.countdown);

      } else if (data.type === 'game_update') {
        // console.log('Game update received:', data);
        renderGame(data.game_state);

      } else if (data.type === 'game_end') {
        console.log('Game ended:', data.game_result);
        resolve(data.game_result);
        gameCalcSocket.close();
      } else
        console.log('gameCalcSocket.onmessage data:', data);
    };

    // Handle connection errors
    gameCalcSocket.onerror = function(error) {
      console.error('WebSocket error:', error);
      reject(error);
    };

    // Handle connection close
    gameCalcSocket.onclose = function(e) {
      if (!e.wasClean) {
        console.error('WebSocket closed unexpectedly:', e);
        reject('WebSocket closed unexpectedly');
      }
    };

    // Event listeners for controls
    window.addEventListener('keydown', (e) => {
      // console.log('e.key: ', e.key);
      if (e.key in keys) {
        // console.log('e.key in keys: ', e.key);
        keys[e.key] = true;
        notifyKeyPressed();
      }
    });
    window.addEventListener('keyup', (e) => {
      if (e.key in keys) {
        keys[e.key] = false;
        notifyKeyPressed();
      }
    });

    function notifyKeyPressed() {
      // console.log('keys:', keys);
      // Filter out the keys that are pressed
      const pressedKeys = Object.keys(keys).filter(key => keys[key]);
      // console.log('pressedKeys:', pressedKeys);
      gameCalcSocket.send(
          JSON.stringify({type: 'key_press', keys: pressedKeys}));
    }
  });
}

async function executeRemotePongGame(p1_name) {
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

  const ballSize = 15
  const paddleWidth = 15
  const paddleHeight = 80
  const borderWidth = 15

  const keys = {w: false, s: false, ' ': false, Escape: false};
  // {w: false, s: false, 8: false, 5: false, ' ': false, Escape: false};

  // Render the game state on the canvas
  function renderGame(gameState) {
    scorePlayer1Element.textContent = gameState.scorePlayer1;
    scorePlayer2Element.textContent = gameState.scorePlayer2;

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
    ctx.fillRect(
        2 * paddleWidth, gameState.leftPaddleY, paddleWidth, paddleHeight);
    // Draw the right paddle
    ctx.fillRect(
        canvas.width - 3 * paddleWidth, gameState.rightPaddleY, paddleWidth,
        paddleHeight);

    // Draw ball
    ctx.fillRect(gameState.ballX, gameState.ballY, ballSize, ballSize);
  }

  return new Promise((resolve, reject) => {
    const gameCalcSocket = new WebSocket('/wss/calcgame/pong/remote/');

    // Handle connection open
    gameCalcSocket.onopen = function(e) {
      console.log('gameCalcSocket WebSocket connection established.');
      // Start the game
      gameCalcSocket.send(
          JSON.stringify({type: 'opening_connection', p1_name: p1_name}));
    };

    // Handle messages from the server
    gameCalcSocket.onmessage = function(e) {
      const data = JSON.parse(e.data);

      if (data.type === 'game_start') {
        console.log('Game start received', data);
        renderGame(data.game_state);

      } else if (data.type === 'game_update') {
        // console.log('Game update received:', data);
        renderGame(data.game_state);

      } else if (data.type === 'game_end') {
        console.log('Game ended:', data.game_result);
        resolve(data.game_result);
        gameCalcSocket.close();
      } else if (data.type === 'connection_established') {
        // Start the game
        gameCalcSocket.send(JSON.stringify({type: 'game_start'}));
      } else
        console.log('gameCalcSocket.onmessage data:', data);
    };

    // Handle connection errors
    gameCalcSocket.onerror = function(error) {
      console.error('WebSocket error:', error);
      reject(error);
    };

    // Handle connection close
    gameCalcSocket.onclose = function(e) {
      if (!e.wasClean) {
        console.error('WebSocket closed unexpectedly:', e);
        reject('WebSocket closed unexpectedly');
      }
    };

    // Event listeners for controls
    window.addEventListener('keydown', (e) => {
      // console.log('e.key: ', e.key);
      if (e.key in keys) {
        // console.log('e.key in keys: ', e.key);
        keys[e.key] = true;
        notifyKeyPressed();
      }
    });
    window.addEventListener('keyup', (e) => {
      if (e.key in keys) {
        keys[e.key] = false;
        notifyKeyPressed();
      }
    });

    function notifyKeyPressed() {
      // console.log('keys:', keys);
      // Filter out the keys that are pressed
      const pressedKeys = Object.keys(keys).filter(key => keys[key]);
      // console.log('pressedKeys:', pressedKeys);
      gameCalcSocket.send(
          JSON.stringify({type: 'key_press', keys: pressedKeys}));
    }
  });
}
