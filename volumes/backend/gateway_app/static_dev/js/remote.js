
// Start button clicked from game or tournament page
async function startRemoteGame(
    game_type, tournament_id, game_round, p1_name, p1_id, p2_name, p2_id) {
  console.log(
      game_type, tournament_id, game_round, p1_name, p1_id, p2_name, p2_id);
  // If normal game: startGame('pong', 0, 'single','Player1', 0, 'Player2', 0)
  // Tournament: startGame('pong', '3', 'Semi-Final 1', 'django_superuser',1,
  // 'Name2',0)

  // Remove the start game button and previous winner name
  document.getElementById('startGame-button')?.remove();
  document.getElementById('playAgain-button')?.remove();
  document.getElementById('nextRound-button')?.remove();
  document.getElementById('startGame-winner')?.remove();

  let game_result = {};
  // Execute the game
  if (game_type === 'pong') {
    game_result = await executeRemotePongGame(p1_name);
  } else if (game_type === 'cows') {
    game_result = await executeCowGame(p1_name, p2_name);
  }
  console.log('game_result: ', game_result);

  // Save the game result in the database
  // saveGameResultInDatabase(
  //     game_type, tournament_id, game_round, p1_name, p1_id, p2_name, p2_id,
  //     game_result);
}

async function newRemoteGame(game_type, p1_name) {
  return new Promise((resolve, reject) => {
    const gameCalcSocket = new WebSocket('/wss/calcgame/pong/remote/');

    gameCalcSocket.onopen = function(e) {
      console.log('newRemoteGame > .onopen, connection opened.');
      gameCalcSocket.send(
          JSON.stringify({type: 'opening_connection', p1_name: p1_name}));
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
        announceGame(data.message, data.player_role);
      } else if (data.type === 'game_end') {
        console.log('newRemoteGame > .onmessage game_end:', data);
        resolve(data.game_result);
        gameCalcSocket.close();

      } else
        console.log('newRemoteGame > .onmessage data:', data);
    };

    gameCalcSocket.onclose = function(e) {
      console.log('newRemoteGame > .onclose, connection closed');
    };

    gameCalcSocket.onerror = function(e) {
      console.log('newRemoteGame > .onerror, error occurred', data);
    };
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

  // Save the game result in the database
  // saveGameResultInDatabase(
  //   game_type, tournament_id, game_round, p1_name, p1_id, p2_name, p2_id,
  //   game_result);
}

function toggleRemoteMode() {
  const remoteMode = document.getElementById('remoteMode').checked;
  const player2Container = document.getElementById('form-player2');
  const player2Input = document.getElementById('player2-input');
  const button = document.getElementById('play-game-button');

  if (remoteMode) {
    player2Container.style.display = 'none';
    player2Input.required = false;
    button.textContent = 'Find remote game';
    button.setAttribute('onclick', 'findRemoteGame()');
  } else {
    player2Container.style.display = 'block';
    player2Input.required = true;
    button.textContent = 'Play game';
    button.setAttribute('onclick', 'playLocalGame()');
  }
}
