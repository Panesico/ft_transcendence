async function startNewGame(gameMode, gameType, gameRound, p1_name, p2_name) {
  // Set up the canvas
  const canvas = document.createElement('canvas');
  canvas.width = 900;
  canvas.height = 550;
  const ctx = canvas.getContext('2d');
  ctx.fillStyle = '#d3d3d3';  // Set the fill color
  ctx.strokeStyle = '#d3d3d3';

  // Game configuration variables for each game
  const cfg = gameType === 'pong' ? {
    ballSize: 15,
    paddleWidth: 15,
    paddleHeight: 80,
    borderWidth: 15,
  } :
                                    {};

  // Allowed controls depending on game mode (local(2p), remote(1p))
  const keys = gameMode === 'local' ?
      {w: false, s: false, 5: false, 8: false, ' ': false, Escape: false} :
      {w: false, s: false, ' ': false, Escape: false};

  // Gets WebSocket for the game mode and game type
  function getCalcGameSocket(gameMode, gameType) {
    let calcGameSocket;
    if ((gameMode === 'local' || gameMode === 'remote') &&
        (gameType === 'pong' || gameType === 'cows')) {
      calcGameSocket =
          new WebSocket(`/wss/calcgame/${gameMode}/?gameType=${gameType}`);
    } else {
      let lang = getCookie('django_language');
      let error = 'Input error';
      if (lang === 'fr')
        error = 'Erreur de saisie';
      else if (lang === 'es')
        error = 'Error de entrada';
      displayError(error);
    }
    return calcGameSocket;
  }

  function addIndicatorToThisPlayer(player_role) {
    const player1Container = document.querySelector('#player1-container');
    if (player1Container && player_role === '1')
      player1Container.style.borderLeft = '8px solid #198754';

    const player2Container = document.querySelector('#player2-container');
    if (player2Container && player_role === '2')
      player2Container.style.borderRight = '8px solid #198754';
  }

  function displayCanvasElement() {
    const gameContainer = document.querySelector('#game-container');
    gameContainer.innerHTML = '';
    gameContainer.appendChild(canvas);
  }

  function showCountdown(gameState, count) {
    document.querySelector('.scorePlayer1').textContent =
        gameState.scorePlayer1;
    document.querySelector('.scorePlayer2').textContent =
        gameState.scorePlayer2;

    ctx.clearRect(0, 0, canvas.width, canvas.height);
    ctx.font = '60px PixeloidSans';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillText(count, canvas.width / 2, canvas.height / 2);
  }

  // Render the game state on the canvas
  function renderPongGame(gameState) {
    document.querySelector('.scorePlayer1').textContent =
        gameState.scorePlayer1;
    document.querySelector('.scorePlayer2').textContent =
        gameState.scorePlayer2;

    // Clear canvas
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // Draw center line
    let centerLineY = 0;
    while (centerLineY < canvas.height) {
      ctx.fillRect(
          canvas.width / 2, centerLineY + 0.5 * cfg.borderWidth, 1,
          cfg.borderWidth);
      centerLineY += 2 * cfg.borderWidth;
    }

    // Draw top and bottom borders
    ctx.fillRect(0, 0, canvas.width, cfg.borderWidth);
    ctx.fillRect(
        0, canvas.height - cfg.borderWidth, canvas.width, cfg.borderWidth);

    // Draw the left paddle
    ctx.fillRect(
        2 * cfg.paddleWidth, gameState.leftPaddleY, cfg.paddleWidth,
        cfg.paddleHeight);
    // Draw the right paddle
    ctx.fillRect(
        canvas.width - 3 * cfg.paddleWidth, gameState.rightPaddleY,
        cfg.paddleWidth, cfg.paddleHeight);

    // Draw ball
    ctx.fillRect(gameState.ballX, gameState.ballY, cfg.ballSize, cfg.ballSize);
  }

  return new Promise((resolve, reject) => {
    const calcGameSocket = getCalcGameSocket(gameMode, gameType);
    if (calcGameSocket === undefined) return;

    let game_id;
    let player_role;

    function setPlayerReadyCheckBoxes(player_role) {
      const player1Ready = document.getElementById('player1-ready');
      const player2Ready = document.getElementById('player2-ready');
      if (player_role === '1') {
        player1Ready.disabled = false;
        player1Ready.addEventListener(
            'click', () => togglePlayerReady(player_role));
      } else if (player_role === '2') {
        player2Ready.disabled = false;
        player2Ready.addEventListener(
            'click', () => togglePlayerReady(player_role));
      }
    }

    function updateOpponentReadyCheckBoxes(opponent) {
      const player1Ready = document.getElementById('player1-ready');
      const player2Ready = document.getElementById('player2-ready');
      if (opponent === '1') {
        player1Ready.checked = true;
      } else if (opponent === '2') {
        player2Ready.checked = true;
      }
    }

    function togglePlayerReady(player_role) {
      const player1Ready = document.getElementById('player1-ready');
      const player2Ready = document.getElementById('player2-ready');
      if (player_role === '1' && player1Ready.checked) {
        calcGameSocket.send(
            JSON.stringify({type: 'player_ready', player: 'player1', game_id}));
        player1Ready.disabled = true;
      } else if (player_role === '2' && player2Ready.checked) {
        calcGameSocket.send(
            JSON.stringify({type: 'player_ready', player: 'player2', game_id}));
        player2Ready.disabled = true;
      }
    }

    calcGameSocket.onopen = function(e) {
      console.log('startNewGame > .onopen, connection opened.');
      if (gameMode === 'local')
        calcGameSocket.send(JSON.stringify({
          type: 'opening_connection, game details',
          p1_name: p1_name,
          p2_name: p2_name,
          game_type: gameType
        }));
      else if (gameMode === 'remote')
        calcGameSocket.send(JSON.stringify({
          type: 'opening_connection, my name is',
          p1_name: p1_name,
          game_type: gameType
        }));
    };

    calcGameSocket.onmessage = function(e) {
      let data = JSON.parse(e.data);

      if (data.type ===
          'waiting_room') {  // while finding an opponent in remote
        console.log('startNewGame > .onmessage waiting_room:', data.message);
        // Load html waiting room
        document.querySelector('main').innerHTML = data.html;

      }  // displays Start button in local and checkboxes in remote
      else if (data.type === 'game_start') {
        console.log('startNewGame > .onmessage game_start:', data.message);
        // Load start game page
        document.querySelector('main').innerHTML = data.html;
        if (gameMode === 'local') {
          addStartButtonListener()
        } else if (gameMode === 'remote') {
          game_id = data.game_id;
          player_role = data.player_role;
          addIndicatorToThisPlayer(player_role);
          announceGame(data.title, data.message);
          setPlayerReadyCheckBoxes(player_role);
        }

      }  // updates oppenent's ready checkbox in remote
      else if (data.type === 'opponent_ready') {
        console.log('startNewGame > .onmessage opponent_ready:', data.message);
        updateOpponentReadyCheckBoxes(data.opponent)

      } else if (data.type === 'game_countdown') {
        console.log('startNewGame > .onmessage game_countdown:', data.message);
        if (data.countdown === 3) displayCanvasElement();
        showCountdown(data.game_state, data.countdown);

      } else if (data.type === 'game_update') {
        // console.log('startNewGame > .onmessage game_update:', data.message);
        if (gameType === 'pong')
          renderPongGame(data.game_state);
        else if (gameType === 'cows')
          renderCowsGame(data.game_state);

      } else if (data.type === 'game_end') {
        console.log('startNewGame > .onmessage game_end:', data.message);
        console.log('game_result:', data.game_result);
        document.querySelector('#game-container').innerHTML = data.html;
        document.querySelector('.scorePlayer1').textContent =
            data.game_result.p1_score;
        document.querySelector('.scorePlayer2').textContent =
            data.game_result.p2_score;

        if (gameRound != 'single')
          console.log('game_end gameRound:', gameRound);

        resolve(data.game_result);
        calcGameSocket.close();

      } else
        console.log('startNewGame > .onmessage data:', data);
    };

    calcGameSocket.onclose = function(e) {
      if (!e.wasClean) {
        console.error('WebSocket closed unexpectedly:', e);
        reject('WebSocket closed unexpectedly');
      } else
        console.log('startNewGame > .onclose, connection closed');
    };

    calcGameSocket.onerror = function(e) {
      console.error('startNewGame > .onerror, error occurred: ', e);
      reject(error);
    };

    // Event listeners for controls
    window.addEventListener('keydown', (e) => {
      if (e.key in keys) {
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
      calcGameSocket.send(JSON.stringify(
          {type: 'key_press', keys: pressedKeys, game_id, player_role}));
    }

    // Event listener for start button
    function addStartButtonListener() {
      const startButton = document.getElementById('startGame-button');
      if (startButton) {
        startButton.addEventListener('click', () => {
          startButton.removeEventListener('click', arguments.callee);
          calcGameSocket.send(JSON.stringify({type: 'players_ready'}));
        });
      }
    }
  });
}
