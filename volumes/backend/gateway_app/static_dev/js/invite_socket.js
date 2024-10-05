function init_socket() {
  console.log('formInviteFriend');
  /* WebSocket */
  const formSocket = new WebSocket('wss://localhost:8443/wss/profileapi/');
  // const formSocket = new WebSocket('/wss/gamecalc/');

  formSocket.onopen = function(e) {
    console.log('formSocket socket connected');
  };

  formSocket.onmessage = function(e) {
    const data = JSON.parse(e.data);
    const message = data['message'];
    console.log('Received message from socket: ', message);
  };

  formSocket.onclose = function(e) {
    console.error('formSocket socket closed unexpectedly');
  };

  function sendMessage(message) {
    console.log('Sending message to socket: ', message);
    formSocket.send(JSON.stringify({'message': message}));
  }
}

function invite_socket() {
    console.log('formInviteFriend');

    const formSocket = new WebSocket('wss://localhost:8443/wss/profileapi/');
    const body = document.getElementById('body');
    const modalIsOpen = body.classList.contains('modal-open');
    
    if (modalIsOpen) {
      init_socket();
      console.log('modalIsOpen');
    }
}