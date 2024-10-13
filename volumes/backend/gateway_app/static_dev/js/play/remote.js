async function newRemoteGame(game_type, p1_name) {
  // Set up the canvas
  const canvas = document.createElement('canvas');
  canvas.width = 900;
  canvas.height = 550;
  const ctx = canvas.getContext('2d');
  ctx.fillStyle = '#d3d3d3';  // Set the fill color
  ctx.strokeStyle = '#d3d3d3';

  const ballSize = 15
  const paddleWidth = 15
  const paddleHeight = 80
  const borderWidth = 15

  const keys = {w: false, s: false, ' ': false, Escape: false};

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
  function renderGame(gameState) {
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
        gameCalcSocket.send(
            JSON.stringify({type: 'player_ready', player: 'player1', game_id}));
        player1Ready.disabled = true;
      } else if (player_role === '2' && player2Ready.checked) {
        gameCalcSocket.send(
            JSON.stringify({type: 'player_ready', player: 'player2', game_id}));
        player2Ready.disabled = true;
      }
    }

    gameCalcSocket.onopen = function(e) {
      //
      console.log('newRemoteGame > .onopen, connection opened.');
      gameCalcSocket.send(JSON.stringify(
          {type: 'opening_connection, my name is', p1_name: p1_name}));
    };

    gameCalcSocket.onmessage = function(e) {
      let data = JSON.parse(e.data);

      if (data.type === 'waiting_room') {
        console.log('newRemoteGame > .onmessage waiting_room:', data.message);
        // Load html waiting room
        document.querySelector('main').innerHTML = data.html;

      } else if (data.type === 'game_start') {
        console.log(
            'newRemoteGame > .onmessage game_start:', data.message,
            ' player_role:', data.player_role);
        // Load game html
        document.querySelector('main').innerHTML = data.html;
        game_id = data.game_id;
        player_role = data.player_role;
        addIndicatorToThisPlayer(player_role);
        announceGame(data.title, data.message);
        setPlayerReadyCheckBoxes(player_role);

      } else if (data.type === 'opponent_ready') {
        console.log('newRemoteGame > .onmessage opponent_ready:', data.message);
        updateOpponentReadyCheckBoxes(data.opponent)

      } else if (data.type === 'game_countdown') {
        console.log('newRemoteGame > .onmessage game_countdown:', data.message);
        if (data.countdown === 3) displayCanvasElement();
        showCountdown(data.game_state, data.countdown);

      } else if (data.type === 'game_update') {
        // console.log('newRemoteGame > .onmessage game_update:', data.message);
        renderGame(data.game_state);

      } else if (data.type === 'game_end') {
        console.log('newRemoteGame > .onmessage game_end:', data.message);
        document.querySelector('#game-container').innerHTML = data.html;
        document.querySelector('.scorePlayer1').textContent =
            data.game_result.p1_score;
        document.querySelector('.scorePlayer2').textContent =
            data.game_result.p2_score;

        resolve(data.game_result);
        gameCalcSocket.close();

      } else
        console.log('newRemoteGame > .onmessage data:', data);
    };

    gameCalcSocket.onclose = function(e) {
      console.log('newRemoteGame > .onclose, connection closed');
    };

    gameCalcSocket.onerror = function(e) {
      console.error('newRemoteGame > .onerror, error occurred: ', e);
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
      gameCalcSocket.send(JSON.stringify(
          {type: 'key_press', keys: pressedKeys, game_id, player_role}));
    }
  });
}

async function findRemoteGame() {
  const game_type =
      document.querySelector('input[name="chosenGame"]:checked').id;
  const p1_name = document.getElementById('player1-input').value;

  // Check if the name is empty
  if (p1_name.length === 0 || p1_name.trim().length === 0) {
    let lang = getCookie('django_language');
    document.getElementById('error-div').style.display = 'block'
    let error = 'Name can\'t be empty';
    if (lang === 'fr')
      error = 'Le nom ne peut pas être vide';
    else if (lang === 'es')
      error = 'El nombre no puede estar vacío';
    document.querySelector('.errorlist').textContent = error;
    return;
  }

  let game_result = {};
  game_result = await newRemoteGame(game_type, p1_name);
  console.log('findRemoteGame > game_result: ', game_result);
}
