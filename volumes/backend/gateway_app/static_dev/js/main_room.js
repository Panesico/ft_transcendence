let mainRoomSocket;

unreadNotifications = false;

// Safe way to send messages by socket
function sendMessagesBySocket(message, socket) {
  // if user id == 0 do not use websocket
  if (document.getElementById('userID').value === '0') {
    console.warn('Client is not logged in, cannot use websocket');
    return;
  }

  console.log('sendMessagesBySocket > message:', message);
  if (socket && socket.readyState === WebSocket.OPEN) {
    socket.send(JSON.stringify(message));
    return true;
  }
  else if (socket && socket.readyState !== WebSocket.OPEN) {
    console.error('sendMessagesBySocket > socker not ready > socket.readyState:', socket.readyState, 'socker.OPEN:', WebSocket.OPEN);
    return false;
  }
}

// Add event listener to the notification
document.addEventListener('DOMContentLoaded', function () {
  const notificationDropdown = document.getElementById('navbarDropdownNotifications');
  notificationDropdown.addEventListener('click', function () {
    console.log('Notification dropdown clicked');
    unreadNotifications = false;
    const bellIcon = notificationDropdown.querySelector('img');
    if (bellIcon.src.includes('bell_up')) {
      bellIcon.src = '/media/utils_icons/bell_down.png';

      // Mark notification as read
      sendMessagesBySocket({ 'type': 'mark_notification_as_read', 'receiver_id': receiver_id }, mainRoomSocket);
    }
  }
  );
});

// Routine when user reload the page
window.onload = () => {
  // Handle form submission
  handleFormSubmission();

  // Get the User ID
  const userID = document.getElementById('userID').value;
  console.log('userID:', userID);
  if (userID === 0 || userID === '0' || userID === '' || userID === undefined || userID === null || userID === 'None' || userID === '[object HTMLInputElement]') {
    console.warn('Client is not logged in');
    return;
  }

  // Establish connection to the main room
  const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
  const hostname = window.location.hostname;
  const port = window.location.port ? `:${window.location.port}` : '';
  mainRoomSocket = new WebSocket(`${protocol}//${hostname}${port}/wss/mainroom/${userID}/`);
  console.log('mainRoomSocket.readyState:', mainRoomSocket.readyState);
  console.log('mainRoomSocket userID:', userID);

  // On websocket open
  mainRoomSocket.onopen = function (e) {
    console.log('mainRoomSocket opened');
    sendMessagesBySocket({ 'type': 'message', 'message': 'main socket opened', }, mainRoomSocket);
    //    mainRoomSocket.send(JSON.stringify({'type': 'message', 'message': 'main socket opened',}));
  };

  // On websocket message
  mainRoomSocket.onmessage = function (e) {
    const data = JSON.parse(e.data);
    parseSocketMessage(data);
  };

  // On websocket close
  mainRoomSocket.onclose = function (e) {
    console.error('mainRoomSocket socket closed unexpectedly');
  };

  // Close the main room socket when the window is closed
  window.onbeforeunload = () => {
    if (mainRoomSocket && mainRoomSocket.readyState === WebSocket.OPEN) {
      mainRoomSocket.close();
    }
  }


  // Close the main room socket when the window is closed
  window.onbeforeunload = () => {
    if (mainRoomSocket && mainRoomSocket.readyState === WebSocket.OPEN) {
      mainRoomSocket.close();
    }
  }

  // Parse the socket message
  function parseSocketMessage(data) {
    if (data.type === 'friend_request') {
      addRequestNotification(data);
    }
    else if (data.type === 'friend_request_response') {
      addResponseNotification(data);
    }
    else if (data.type === 'chat') {
      handleChatMessages(data);
    }
    else if (data.type === 'game_request') {
      addRequestNotification(data);
    }
    else if (data.type === 'game_request_response') {
      addResponseNotification(data);
    }
    else if (data.type === 'cancel_waiting_room') {
      addResponseNotification(data);
    }
    else if (data.type === 'user_connected' || data.type === 'user_left') {
      updateOnlineFriends(data);
    }
    else if (data.type === 'next_in_tournament') {
      addResponseNotification(data);
    }
    // else if (data.type === 'connected_friends') {
    //   addOnlineStatusBadge(data);
    // }
    else {
      console.log('parseSocketMessage > data.type:', data.type);
    }
  }
}
