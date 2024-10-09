
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

function findRemoteGame() {
  const p1_name = document.getElementById('player1-input').value;

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

  const game_type =
      document.querySelector('input[name="chosenGame"]:checked').id;

  const gameCalcSocket = new WebSocket('/wss/calcgame/pong/remote/');

  gameCalcSocket.onopen = function(e) {
    console.log('gameCalcSocket.onopen, connection opened.');
    gameCalcSocket.send(
        JSON.stringify({type: 'opening_connection', p1_name: p1_name}));
  };

  gameCalcSocket.onmessage = function(e) {
    let data = JSON.parse(e.data);
    console.log('gameCalcSocket.onmessage, data:', data);
    console.log('gameCalcSocket.onmessage, data.type:', data.type);
    console.log(
        'gameCalcSocket.onmessage, message received from server:',
        data.message);
    if (data.type === 'waiting_room') {
      console.log('Loading waiting_room');
      document.querySelector('main').innerHTML = data.html;
    }
  };

  gameCalcSocket.onclose = function(e) {
    console.log('gameCalcSocket.onclose, connection closed');
  };

  gameCalcSocket.onerror = function(e) {
    console.log('gameCalcSocket.onerror, error occurred');
  };
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
