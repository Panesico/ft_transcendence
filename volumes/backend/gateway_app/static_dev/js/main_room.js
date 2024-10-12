let mainRoomSocket;

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

function addNotification(data)
{
  const notificationDropdown = document.getElementById('navbarDropdownNotifications');
  const notificationDropdownClass = document.getElementById('notificationClassContent');
  receiver_username = data.receiver_username;
  receiver_id = data.receiver_id;
  sender_username = data.receiver_username;
  sender_username = data.sender_username;
  sender_id = data.sender_id;
  sender_avatar_url = data.sender_avatar_url;
  console.log('addNotification > receiver_username:', receiver_username);
  console.log('addNotification > receiver_id:', receiver_id);
  console.log('addNotification > sender_username:', sender_username);
  console.log('addNotification > sender_id:', sender_id);
  console.log('addNotification > sender_avatar_url:', sender_avatar_url);

  // Remove the 'no notifications' message
  const emptyMessage = document.getElementById('notificationContent');
  if (emptyMessage)
  {
    if (emptyMessage.innerHTML.trim() === 'You have no notifications') {
      console.log('addNotification > Removing empty message');
      emptyMessage.remove();
    }
    else {
      console.log('addNotification > No empty message to remove');
      console.log('addNotification > emptyMessage.innerHTML:', emptyMessage.innerHTML);
    }

  }

  // Create a new notification element
  const newNotification = document.createElement('li');
  newNotification.classList.add('dropdown-item');
  const message = 'You have a friend request from ' + sender_username;
  newNotification.textContent = message;
  newNotification.style.color = 'red';
  console.log('addNotification > receiver_id:', receiver_id);

  // Change default empty message to the new notification
  if (notificationDropdownClass) {
    notificationDropdownClass.appendChild(newNotification);
    console.log('addNotification > notificationDropdown:', notificationDropdown);
    const bellIcon = notificationDropdown.querySelector('img');
    if (bellIcon) {
      bellIcon.src = '/media/utils_icons/bell_up.png';
    }
  }
  else {
    console.log('addNotification > notificationDropdown is null');
  }
}