let mainRoomSocket;

unreadNotifications = false;

// Add event listener to the notification
document.addEventListener('DOMContentLoaded', function() {
  const notificationDropdown = document.getElementById('navbarDropdownNotifications');
  notificationDropdown.addEventListener('click', function() {
    console.log('Notification dropdown clicked');
    unreadNotifications = false;
    const bellIcon = notificationDropdown.querySelector('img');
    if (bellIcon) {
      bellIcon.src = '/media/utils_icons/bell_down.png';
    }
  }
  );
});

// // Check if user read notifications
// function checkNotifications()
// {
//   console.log('checkNotifications > unreadNotifications:', unreadNotifications);
//   if (unreadNotifications === true)
//   {
//     console.log('checkNotifications > unreadNotifications:', unreadNotifications);
//     const notificationDropdown = document.getElementById('navbarDropdownNotifications');
//     const bellIcon = notificationDropdown.querySelector('img');
//     if (bellIcon) {
//       bellIcon.src = '/media/utils_icons/bell_down.png';
//     }
//   }
// }

window.onload = () => {
  // Handle form submission
  handleFormSubmission();

  // Get the User ID
  const userID = document.getElementById('userID').value;
  console.log('userID:', userID);
  //const userID = 1;
  if (userID === '' || userID === undefined || userID === 'None') {
    console.warn('User ID is not defined');
    return;
  }

  // Establish connection to the main room
  main_room_socketPath = 'wss://localhost:8443/wss/mainroom/' + userID;
  console.log('main_room_socketPath:', main_room_socketPath);
  mainRoomSocket = new WebSocket(`wss://localhost:8443/wss/mainroom/${userID}/`);
  console.log('mainRoomSocket.readyState:', mainRoomSocket.readyState);

  // On websocket open
  mainRoomSocket.onopen = function(e) {
    console.log('mainRoomSocket opened');
    mainRoomSocket.send(JSON.stringify({'type': 'message', 'message': 'main socket opened',}));
  };

  // On websocket message
  mainRoomSocket.onmessage = function(e) {
    const data = JSON.parse(e.data);
    console.log('Received message from socket: ', data);
    parseSocketMessage(data);
  };

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


// Close the main room socket when the window is closed
window.onbeforeunload = () => {
  if (mainRoomSocket && mainRoomSocket.readyState === WebSocket.OPEN) {
    mainRoomSocket.close();
  }
}

function sendFriendRequest(sender_username, sender_id, sender_avatar_url, receiver_username, receiver_id)
{
  console.log('sendFriendRequest > sender_username:', sender_username);
  console.log('sendFriendRequest > sender_id:', sender_avatar_url);
  console.log('sendFriendRequest > sender_avatar_url:', sender_avatar_url);
  console.log('sendFriendRequest > receiver_username:', receiver_username);
  console.log('sendFriendRequest > receiver_id:', receiver_id);
  mainRoomSocket.send(JSON.stringify({'type': 'friend_request', 'sender_username': sender_username, 'sender_id': sender_id, 'sender_avatar_url': sender_avatar_url, 'receiver_username': receiver_username, 'receiver_id': receiver_id}));
}

function parseSocketMessage(data)
{
  if (data.type === 'friend_request') {
    addNotification(data);
  }
  else
  {
    console.log('parseSocketMessage > data.type:', data.type);
  }
}