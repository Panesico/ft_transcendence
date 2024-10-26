function getInitialVariables(gameType, initialVars) {
  // initialVars = {
  //   'canvas': {
  //     'width': 900,
  //     'height': 550,
  //   },
  //   'maxScore': 2,
  //   'ballSize': 15,
  //   'paddleWidth': 15,
  //   'paddleHeight': 80,
  //   'borderWidth': 15,
  //   'paddleSpeed': 10
  // };

  // Set up the canvas
  const canvas = document.createElement('canvas');
  canvas.width = initialVars.canvas.width;
  canvas.height = initialVars.canvas.height;
  const ctx = canvas.getContext('2d');
  ctx.fillStyle = '#d3d3d3';
  ctx.strokeStyle = '#d3d3d3';

  // Game configuration variables for each game
  let cfg = (gameType === 'pong')
    ? { // if pong
      ballSize: initialVars.ballSize,
      paddleWidth: initialVars.paddleWidth,
      paddleHeight: initialVars.paddleHeight,
      borderWidth: initialVars.borderWidth,
      canvas,
      ctx,
      keys: initialVars.keys,
    } : { // if cows
      playerDimension: initialVars.playerDimension,
      cowDimension: initialVars.cowDimension,
      canvas,
      ctx,
      keys: initialVars.keys,
    };

  // Load images for cows game
  if (gameType === 'cows') {
    const baseUrl = window.location.origin;

    cfg.player1Image = new Image();
    cfg.player1Image.src = `${baseUrl}/static/images/game/spaceship1.png`;

    cfg.player2Image = new Image();
    cfg.player2Image.src = `${baseUrl}/static/images/game/spaceship2.png`;

    cfg.cowImage = new Image();
    cfg.cowImage.src = `${baseUrl}/static/images/game/cow400.png`;

    cfg.backgroundImage = new Image();
    cfg.backgroundImage.src = `${baseUrl}/static/images/game/nightsky.jpg`;

    cfg.earthImage = new Image();
    cfg.earthImage.src = `${baseUrl}/static/images/game/earth.png`;
  }

  return cfg;
}

// Add indicator next to player name for remote games
function addIndicatorToThisPlayer(player_role) {
  const player1Container = document.querySelector('#player1-container');
  if (player1Container && player_role === '1')
    player1Container.style.borderLeft = '8px solid #198754';

  const player2Container = document.querySelector('#player2-container');
  if (player2Container && player_role === '2')
    player2Container.style.borderRight = '8px solid #198754';
}

// Display the canvas element
function displayCanvasElement(cfg) {
  const gameContainer = document.querySelector('#game-container');
  gameContainer.innerHTML = '';
  gameContainer.appendChild(cfg.canvas);
}

// Display the countdown on the canvas
function showCountdown(cfg, gameState, count) {
  document.querySelector('.scorePlayer1').textContent = gameState.scorePlayer1;
  document.querySelector('.scorePlayer2').textContent = gameState.scorePlayer2;

  cfg.ctx.clearRect(0, 0, cfg.canvas.width, cfg.canvas.height);
  cfg.ctx.font = '60px PixeloidSans';
  cfg.ctx.textAlign = 'center';
  cfg.ctx.textBaseline = 'middle';
  cfg.ctx.fillText(count, cfg.canvas.width / 2, cfg.canvas.height / 2);
}

// Render the pong game state on the canvas
function renderPongGame(cfg, gameState) {
  document.querySelector('.scorePlayer1').textContent = gameState.scorePlayer1;
  document.querySelector('.scorePlayer2').textContent = gameState.scorePlayer2;

  // Clear canvas
  cfg.ctx.clearRect(0, 0, cfg.canvas.width, cfg.canvas.height);

  // Draw center line
  let centerLineY = 0;
  while (centerLineY < cfg.canvas.height) {
    cfg.ctx.fillRect(
      cfg.canvas.width / 2, centerLineY + 0.5 * cfg.borderWidth, 1,
      cfg.borderWidth);
    centerLineY += 2 * cfg.borderWidth;
  }

  // Draw top and bottom borders
  cfg.ctx.fillRect(0, 0, cfg.canvas.width, cfg.borderWidth);
  cfg.ctx.fillRect(
    0, cfg.canvas.height - cfg.borderWidth, cfg.canvas.width,
    cfg.borderWidth);

  // Draw the left paddle
  cfg.ctx.fillRect(
    2 * cfg.paddleWidth, gameState.leftPaddleY, cfg.paddleWidth,
    cfg.paddleHeight);
  // Draw the right paddle
  cfg.ctx.fillRect(
    cfg.canvas.width - 3 * cfg.paddleWidth, gameState.rightPaddleY,
    cfg.paddleWidth, cfg.paddleHeight);

  // Draw ball
  cfg.ctx.fillRect(
    gameState.ballX, gameState.ballY, cfg.ballSize, cfg.ballSize);
}

// Render the cows game state on the canvas
function renderCowsGame(cfg, gameState) {
  document.querySelector('.scorePlayer1').textContent = gameState.scorePlayer1;
  document.querySelector('.scorePlayer2').textContent = gameState.scorePlayer2;
  cfg.ctx.fillStyle = 'rgba(255, 0, 0, 0.5)';

  cfg.ctx.clearRect(0, 0, cfg.canvas.width, cfg.canvas.height);

  // Draw background
  cfg.ctx.drawImage(cfg.backgroundImage, 0, 0, cfg.canvas.width, cfg.canvas.height);

  // Draw earth
  cfg.ctx.drawImage(cfg.earthImage, cfg.canvas.width / 2 - 100, cfg.canvas.height / 2 - 100, 200, 200);

  // Draw players
  cfg.ctx.drawImage(cfg.player1Image, gameState.player1X, gameState.player1Y, cfg.playerDimension, cfg.playerDimension);
  cfg.ctx.drawImage(cfg.player2Image, gameState.player2X, gameState.player2Y, cfg.playerDimension, cfg.playerDimension);

  // Draw hit zone
  if (gameState.player1_hit) {
    cfg.ctx.beginPath();
    cfg.ctx.arc(
      gameState.player1X + cfg.playerDimension / 2,
      gameState.player1Y + cfg.playerDimension / 2,
      cfg.playerDimension / 2, 0, Math.PI * 2
    );
    cfg.ctx.fill();
  }
  if (gameState.player2_hit) {
    cfg.ctx.beginPath();
    cfg.ctx.arc(
      gameState.player2X + cfg.playerDimension / 2,
      gameState.player2Y + cfg.playerDimension / 2,
      cfg.playerDimension / 2, 0, Math.PI * 2
    );
    cfg.ctx.fill();
  }

  // Draw cows
  gameState.cows.forEach(cow => {
    cfg.ctx.drawImage(cfg.cowImage, cow.x, cow.y, cfg.cowDimension, cfg.cowDimension);
  });
}


// Set checkboxes for player ready according to player role
function setPlayerReadyCheckBoxes(player_role, calcGameSocket, game_id) {
  const player1Ready = document.getElementById('player1-ready');
  const player2Ready = document.getElementById('player2-ready');
  if (player_role === '1') {
    player1Ready.disabled = false;
    player1Ready.addEventListener(
      'click', () => togglePlayerReady(player_role, calcGameSocket, game_id));
  } else if (player_role === '2') {
    player2Ready.disabled = false;
    player2Ready.addEventListener(
      'click', () => togglePlayerReady(player_role, calcGameSocket, game_id));
  }
}

// Update opponent's ready checkbox when informed by remote
function updateOpponentReadyCheckBoxes(opponent) {
  const player1Ready = document.getElementById('player1-ready');
  const player2Ready = document.getElementById('player2-ready');
  if (opponent === '1') {
    player1Ready.checked = true;
  } else if (opponent === '2') {
    player2Ready.checked = true;
  }
}

// Toggles player ready checkbox
function togglePlayerReady(player_role, calcGameSocket, game_id) {
  const player1Ready = document.getElementById('player1-ready');
  const player2Ready = document.getElementById('player2-ready');
  if (player_role === '1' && player1Ready.checked) {
    calcGameSocket.send(
      JSON.stringify({ type: 'player_ready', player: 'player1', game_id }));
    player1Ready.disabled = true;
  } else if (player_role === '2' && player2Ready.checked) {
    calcGameSocket.send(
      JSON.stringify({ type: 'player_ready', player: 'player2', game_id }));
    player2Ready.disabled = true;
  }
}

// Gets websocket for the game mode and game type
function getCalcGameSocket(gameMode, gameType, gameRound) {
  let calcGameSocket;

  // if tournament game
  if (gameRound != 'single' && (gameType === 'pong' || gameType === 'cows')) {
    calcGameSocket =
      new WebSocket(`/wss/calcgame/tournament/?gameType=${gameType}`);

  }  // if single game
  else if (
    gameRound === 'single' &&
    (gameMode === 'local' || gameMode === 'remote' || gameMode === 'invite') &&
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

// Attach and remove event listeners to navbar items on socket open/close
function setupNavbarEventListeners(socket) {
  const header = document.querySelector("#mainHeader");
  const navLinks = header.querySelectorAll("a");

  // Define the event listener for navigation
  function closeSocketOnNavbarClick() {
    if (socket) {
      // console.log("Closing WebSocket due to navigation.");
      socket.close();
      socket = null;

      removeNavbarListeners();
    }
  }

  // Remove event listeners from the navbar links
  function removeNavbarListeners(socket) {
    navLinks.forEach(link => {
      link.removeEventListener("click", closeSocketOnNavbarClick);
    });
  }

  // Attach event listeners to all navbar links
  navLinks.forEach(link => {
    link.addEventListener("click", closeSocketOnNavbarClick);
  });
}
