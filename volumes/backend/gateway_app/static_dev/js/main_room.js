let mainRoomSocket;

window.onload = () => {
  // Handle form submission
  handleFormSubmission();

  // Get the User ID
  const userID = document.getElementById('userID').value;
  //const userID = 1;
  if (userID === '' || userID === undefined || userID === null) {
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

function sendFriendRequest(username, user_id)
{
  console.log('sendFriendRequest > username:', username);
  console.log('sendFriendRequest > user_id:', user_id);
  mainRoomSocket.send(JSON.stringify({'type': 'friend_request', 'user_id': user_id, 'username': username}));
}

function parseSocketMessage(data)
{
  if (data.type === 'friend_request') {
    addNotification(data);
  }
}

function addNotification(data)
{
  const notificationDropdown = document.getElementById('navbarDropdownNotifications');
  const notificationDropdownClass = document.getElementById('notificationClassContent');
  incoming_username = data.username;
  incoming_user_id = data.user_id;

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
  newNotification.textContent = `You have a friend request from ${data.username}`;
  newNotification.style.color = 'red';
  console.log('addNotification > incoming_user_id:', incoming_user_id);

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
  // const friendRequestModal = document.getElementById('friendRequestModal');
  // const friendRequestModalContent = document.getElementById('friendRequestModalContent');
  // const friendRequestModalAccept = document.getElementById('friendRequestModalAccept');
  // const friendRequestModalDecline = document.getElementById('friendRequestModalDecline');

  // friendRequestModalContent.innerHTML = `You have a friend request from ${data.username}`;
  // friendRequestModal.style.display = 'block';

  // friendRequestModalAccept.onclick = function() {
  //   mainRoomSocket.send(JSON.stringify({'type': 'friend_request_response', 'response': 'accept', 'user_id': data.user_id}));
  //   friendRequestModal.style.display = 'none';
  // }

  // friendRequestModalDecline.onclick = function() {
  //   mainRoomSocket.send(JSON.stringify({'type': 'friend_request_response', 'response': 'decline', 'user_id': data.user_id}));
  //   friendRequestModal.style.display = 'none';
}