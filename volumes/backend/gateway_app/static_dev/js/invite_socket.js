let inviteFriendSocket;  // Make the websocket accessible globally

function onModalOpen() {
  console.log('Modal is open');

  /* WebSocket */
  inviteFriendSocket = new WebSocket('wss://localhost:8443/wss/profileapi/');
  // const inviteFriendSocket = new WebSocket('/wss/calcgame/');

  inviteFriendSocket.onopen = function(e) {
    console.log('inviteFriendSocket socket connected');
    inviteFriendSocket.send(
        JSON.stringify({'query': 'inviteFriendSocket is connected'}));
  };

  inviteFriendSocket.onmessage = function(e) {
    const data = JSON.parse(e.data);
    const message = data['message'];
    console.log('Received message from socket: ', message);
  };

  inviteFriendSocket.onclose = function(e) {
    console.warn('inviteFriendSocket socket closed unexpectedly');
  };

  // Ensure inviteFriendSocket is defined before calling send
  if (inviteFriendSocket) {
    console.log(
        'inviteFriendSocket.readyState:', inviteFriendSocket.readyState);
  } else {
    console.error('inviteFriendSocket is not defined');
  }
  // if (inviteFriendSocket && inviteFriendSocket.readyState ===
  // WebSocket.OPEN) {
  //   inviteFriendSocket.send(JSON.stringify({'query': 'test'}));
  // } else {
  //   console.error('WebSocket is not open or not defined.');
  // }
}

function onModalClose() {
  if (inviteFriendSocket && inviteFriendSocket.readyState === WebSocket.OPEN) {
    inviteFriendSocket.close();
    console.log('Modal is closed and WebSocket is closed');
  } else {
    console.warn('WebSocket is not open or already closed');
  }
}

function sendMessageInviteSocket(message) {
  console.log('Sending message to socket: ', message);
  inviteFriendSocket.send(JSON.stringify({'message': message}));
}

function listenFriendInvitation(modal) {
  console.log('inviteFrienModal');
  let inputField = document.getElementById('username_input');

  modal.addEventListener('show.bs.modal', () => {
    onModalOpen();
  })

  // Event listen for key press
  console.log('inputField.addEventListene:');

  inputField.addEventListener('keyup', (e) => {
    clearTimeout(timeout);
    let inputText = e.target.value;

    console.log('inputText:', inputText);
    // Debounce the request (e.g., wait 300ms before sending)
    timeout = setTimeout(() => {
      if (inviteFriendSocket.readyState === WebSocket.OPEN) {
        inviteFriendSocket.send(JSON.stringify({query: inputText}));
      }
    }, 300);
  });

  modal.addEventListener('hidden.bs.modal', () => {
    onModalClose();
  });
}