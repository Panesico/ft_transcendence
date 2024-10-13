function checkValidInput(gameMode, gameType, p1_name, p2_name) {
  let lang = getCookie('django_language');

  // Check if the gameMode and gameType are valid
  if (!gameMode || !gameType ||
      (gameMode !== 'local' && gameMode !== 'remote') ||
      (gameType !== 'pong' && gameType !== 'cows')) {
    document.getElementById('error-div').style.display = 'block'
    let error = 'Invalid selection';
    if (lang === 'fr')
      error = 'Sélection invalide';
    else if (lang === 'es')
      error = 'Selección inválida';
    document.querySelector('.errorlist').textContent = error;

    return false;
  }

  // Check if the names are empty or only whitespace
  if ((gameMode === 'remote' &&
       (p1_name.length === 0 || p1_name.trim().length === 0)) ||
      (gameMode === 'local' &&
       (p1_name.length === 0 || p2_name.length === 0 ||
        p1_name.trim().length === 0 || p2_name.trim().length === 0))) {
    document.getElementById('error-div').style.display = 'block'
    let error = 'Name can\'t be empty';
    if (lang === 'fr')
      error = 'Le nom ne peut pas être vide';
    else if (lang === 'es')
      error = 'El nombre no puede estar vacío';
    document.querySelector('.errorlist').textContent = error;

    return false;
  }

  // Check if the names are different
  if (gameMode === 'local' && (p1_name === p2_name)) {
    document.getElementById('error-div').style.display = 'block'
    let error = 'Names must be different';
    if (lang === 'fr')
      error = 'Les noms doivent être différents';
    else if (lang === 'es')
      error = 'Los nombres deben ser diferentes';
    document.querySelector('.errorlist').textContent = error;

    return false;
  }

  return true;
}

// Toggles what's displayed depending on the game mode
function toggleGameMode() {
  const remoteMode = document.getElementById('remoteMode').checked;
  const player2Container = document.getElementById('form-player2');
  const player2Input = document.getElementById('player2-input');
  const button = document.getElementById('play-game-button');

  if (remoteMode) {
    player2Container.style.display = 'none';
    player2Input.required = false;
    button.textContent = 'Find remote game';
    // button.setAttribute('onclick', 'findRemoteGame()');
  } else {
    player2Container.style.display = 'block';
    player2Input.required = true;
    button.textContent = 'Play game';
    // button.setAttribute('onclick', 'playLocalGame()');
  }
}

// Called from button on Play page, starts a new game
async function playGame() {
  // gameMode: 'local' or 'remote' (or 'ai)
  // gameType: 'pong' or 'cows'

  let gameMode = document.querySelector('input[name="gameMode"]:checked').id;
  if (gameMode === 'localMode') gameMode = 'local';
  if (gameMode === 'remoteMode') gameMode = 'remote';

  const gameType =
      document.querySelector('input[name="chosenGame"]:checked').id;

  const p1_name = document.getElementById('player1-input').value;
  let p2_name = '';
  if (gameMode === 'local') {
    p2_name = document.getElementById('player2-input').value;
  }

  // check input selection
  if (!checkValidInput(gameMode, gameType, p1_name, p2_name)) return;

  // gameRound: 'single', 'Semi-Final 1', 'Semi-Final 2', 'Final'
  let gameRound = 'single';
  let game_result =
      await startNewGame(gameMode, gameType, gameRound, p1_name, p2_name);
  console.log('playGame > game_result: ', game_result);
}
