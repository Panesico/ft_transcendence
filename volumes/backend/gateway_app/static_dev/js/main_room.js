let mainRoomSocket;

window.onload = () => {
  // Get the User ID
  // const userID = document.getElementById('userID').value;
  const userID = 1;
  // if (userID === '' || userID === undefined) {
  //   console.error('User ID is not defined');
  //   return;

  // Establish connection to the main room
  mainRoomSocket = new WebSocket(`wss://localhost:8443/wss/mainroom/`);
  console.log('mainRoomSocket.readyState:', mainRoomSocket.readyState);

  // On websocket open
  mainRoomSocket.onopen = function(e) {
    console.log('mainRoomSocket opened');
    mainRoomSocket.send(JSON.stringify({'message': 'main socket opened', 'userID': userID}));
  };

  // On websocket message
  mainRoomSocket.onmessage = function(e) {
    const data = JSON.parse(e.data);
    console.log('Received message from socket: ', data);
  };
    // if (type === 'suggestions') {
    //   matching_usernames = data['suggestions'];
    //   console.log('Matching usernames:', matching_usernames);
    //   update_dropdown(matching_usernames);
    // }

  // On websocket close
  mainRoomSocket.onclose = function(e) {
    console.warn('mainRoomSocket socket closed unexpectedly');
  };
}

// Close the main room socket when the window is closed
window.onbeforeunload = () => {
  if (mainRoomSocket && mainRoomSocket.readyState === WebSocket.OPEN) {
    mainRoomSocket.close();
  }
}
