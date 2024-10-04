
async function saveGameResultInDatabase(
    tournament_id, game_round, p1_name, p1_id, p2_name, p2_id, game_result) {
  let path = window.location.pathname;
  let url = '';
  // console.log('path: ', path);
  if (path === '/game/') {
    url = 'saveGame/';
  } else if (path === '/game') {
    url = path + '/saveGame/';
  } else if (path === '/tournament/') {
    url = 'update/';
  } else if (path === '/tournament') {
    url = path + '/update/';
  }
  // console.log('url: ', url);

  const jsonData = {
    'tournament_id': tournament_id,
    'game_type': 'pong',
    'game_round': game_round,
    'p1_name': p1_name,
    'p2_name': p2_name,
    'p1_id': p1_id,
    'p2_id': p2_id,
    'p1_score': game_result.scorePlayer1,
    'p2_score': game_result.scorePlayer2,
    'game_winner_name': game_result.winner,
    'game_winner_id': (game_result.winner == p1_name) ? p1_id : p2_id,
  };

  const response = await fetch(url, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': getCookie('csrftoken')
    },
    credentials: 'include',
    body: JSON.stringify(jsonData)
  });

  const data = await response.json();
  console.log('data.status: ', data.status);
  console.log('data.message: ', data.message);

  document.querySelector('main').innerHTML = data.html;
}

// Show the winner and next round button
function nextRound(tournament_round, p1_name, p2_name) {
  document.getElementById('startGame-winner').remove();
  document.getElementById('nextRound-button').remove();
  document.getElementById('startGame-button').style.display = 'block';
  document.getElementById('namePlayer1').textContent = p1_name;
  document.getElementById('namePlayer2').textContent = p2_name;
  document.querySelector('.scorePlayer1').textContent = 0;
  document.querySelector('.scorePlayer2').textContent = 0;
  document.querySelector('h1').textContent = tournament_round;

  announceGame(tournament_round, `${p1_name} vs ${p2_name}`);
}

// Start button clicked from game or tournament page
async function startGame(
    tournament_id, game_round, p1_name, p1_id, p2_name, p2_id) {
  console.log(tournament_id, game_round, p1_name, p1_id, p2_name, p2_id);
  // If normal game: startGame(0, 'Single','Player1', 0, 'Player2', 0)
  // Tournament: startGame('3', 'Semi-Final 1', 'django_superuser',1, 'Name2',0)

  // Remove the start game button and previous winner name
  document.getElementById('startGame-button')?.remove();
  document.getElementById('playAgain-button')?.remove();
  document.getElementById('nextRound-button')?.remove();
  document.getElementById('startGame-winner')?.remove();

  // Execute the game
  const game_result = await executePongGame(p1_name, p2_name);
  console.log('game_result: ', game_result);

  // Save the game result in the database
  saveGameResultInDatabase(
      tournament_id, game_round, p1_name, p1_id, p2_name, p2_id, game_result);
}
