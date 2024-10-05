let inviteFriendSocket; // Make the websocket accessible globally

function sendMessage(message) {
  console.log('Sending message to socket: ', message);
  inviteFriendSocket.send(JSON.stringify({'message': message}));
}

function onModalOpen() {
  console.log('Modal is open');

  /* WebSocket */
  inviteFriendSocket = new WebSocket('wss://localhost:8443/wss/profileapi/');
  // const inviteFriendSocket = new WebSocket('/wss/gamecalc/');

  inviteFriendSocket.onopen = function(e) {
    console.log('inviteFriendSocket socket connected');
  };

  inviteFriendSocket.onmessage = function(e) {
    const data = JSON.parse(e.data);
    const message = data['message'];
    console.log('Received message from socket: ', message);
  };

  inviteFriendSocket.onclose = function(e) {
    console.warn('inviteFriendSocket socket closed unexpectedly');
  };  
}

function onModalClose()
{
  if (inviteFriendSocket && inviteFriendSocket.readyState === WebSocket.OPEN) {
    inviteFriendSocket.close();
    console.log('Modal is closed and WebSocket is closed');
  } else {
    console.warn('WebSocket is not open or already closed');
  }
}

function listenFriendInvitation(modal) {
    console.log('inviteFrienModal');

    modal.addEventListener('show.bs.modal', () => {
      onModalOpen();
    })

    modal.addEventListener('hidden.bs.modal', () => {
      onModalClose();

  });
}