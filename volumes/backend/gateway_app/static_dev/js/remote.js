function findRemoteGame(params) {
  // const remoteGameSocket = new WebSocket('/wss/remotegame/' + params.game_id
  // + '/');
  const remoteGameSocket = new WebSocket('/wss/remotegame/');


  remoteGameSocket.onopen = function(e) {
    console.log('remoteGameSocket.onopen, connection opened.');
  };

  remoteGameSocket.onmessage = function(e) {
    let data = JSON.parse(e.data);
    console.log(
        'remoteGameSocket.onmessage, message received from server:',
        data.message);
  };

  remoteGameSocket.onclose = function(e) {
    console.log('remoteGameSocket.onclose, connection closed');
  };

  remoteGameSocket.onerror = function(e) {
    console.log('remoteGameSocket.onerror, error occurred');
  };

  const username = document.getElementById('player1').value;
  const chosenGame =
      document.querySelector('input[name="chosenGame"]:checked').value;
  const message = {'username': username, 'chosenGame': chosenGame};

  remoteGameSocket.send(JSON.stringify(message));
  console.log('Message sent:', message);
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
