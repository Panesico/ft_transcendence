/* -------------------Friend Request notification------------------- */

function removeEmptyMessage()
{
  const emptyMessage = document.getElementById('notificationContent');
  if (emptyMessage)
  {
    if (emptyMessage.innerHTML.trim() === 'You have no notifications') {
      console.log('addFriendRequestNotification > Removing empty message');
      emptyMessage.remove();
      unreadNotifications = false;

    }
    else {
      console.log('addFriendRequestNotification > No empty message to remove');
      console.log('addFriendRequestNotification > emptyMessage.innerHTML:', emptyMessage.innerHTML);
    }

  }
}

function createAvatarElement(avatar_url)
{
  const avatar = document.createElement('img');
  avatar.src = avatar_url;
  avatar.alt = 'Avatar';
  avatar.style.height = '3rem';
  avatar.style.width = '3rem';
  avatar.style.objectFit = 'cover';
  avatar.style.borderRadius = '50%';
  avatar.style.marginRight = '10px';
  avatar.style.border = '1px solid white';
  return avatar;
}

function createMessageElement(sender_username, response)
{
  const message = document.createElement('span');
  message.textContent = `${sender_username} ${response}`;
//  message.textContent = `${sender_username} sent you a friend request.`;
  message.style.marginLeft = '10px';
  return message;
}

function appendAvatarAndMessage(avatar, message, newNotification)
{
  // Style the notification
  newNotification.style.color = 'white';
  newNotification.style.setProperty('--bs-dropdown-link-hover-bg', 'transparent');
  
  newNotification.appendChild(avatar);
  newNotification.appendChild(message);
  // Set data atribute to identify the notification
  newNotification.setAttribute('data-type', 'friend-invite');
  newNotification.setAttribute('data-userid', sender_id);
}

  function createAcceptButton(sender_id, receiver_id, newNotification)
  {
    const acceptButton = document.createElement('img');
    acceptButton.src = '/media/utils_icons/accept.png';
    acceptButton.alt = 'Accept';
    acceptButton.style.height = '2rem';
    acceptButton.style.width = '2rem';
    acceptButton.style.objectFit = 'cover';
    acceptButton.style.marginLeft = '10px';
    acceptButton.style.cursor = 'pointer';
    acceptButton.style.backgroundColor = 'transparent';

  //   acceptButton.onclick = function() {
  //     mainRoomSocket.send(JSON.stringify({'type': 'friend_request_response', 'response': 'accept', 'sender_id': sender_id, 'receiver_id': receiver_id}));
  // //    newNotification.remove(); uncomment
  //   }

    newNotification.appendChild(acceptButton);

    return acceptButton;
  }

  function changeNotificationIconToUp(notificationDropdownClass, newNotification, notificationDropdown)
{
  if (notificationDropdownClass) {
    notificationDropdownClass.appendChild(newNotification);
    console.log('addFriendRequestNotification > notificationDropdown:', notificationDropdown);
    const bellIcon = notificationDropdown.querySelector('img');
    if (bellIcon) {
      bellIcon.src = '/media/utils_icons/bell_up.png';
    }
  }
  else {
    console.log('addFriendRequestNotification > notificationDropdown is null');
  }
}

function createDeclineButton(sender_id, receiver_id, newNotification)
{
  const declineButton = document.createElement('img');
  declineButton.src = '/media/utils_icons/decline.png';
  declineButton.alt = 'Decline';
  declineButton.style.height = '2rem';
  declineButton.style.width = '2rem';
  declineButton.style.objectFit = 'cover';
  declineButton.style.marginLeft = '10px';
  declineButton.style.cursor = 'pointer'; // Change cursor to pointer to indicate it's clickable
  declineButton.style.backgroundColor = 'transparent';

//   declineButton.onclick = function() {
//     mainRoomSocket.send(JSON.stringify({'type': 'friend_request_response', 'response': 'decline', 'sender_id': sender_id, 'receiver_id': receiver_id}));
// //    newNotification.remove(); uncomment
//   }

  // Append the button to the newNotification element
  newNotification.appendChild(declineButton);

  return declineButton;
}

function listenUserResponse(acceptButton, declineButton, sender_id, receiver_id, sender_username, receiver_username)
{
  acceptButton.addEventListener('click', function() {
    console.log('Accept button clicked');
    sendMessagesBySocket({'type': 'friend_request_response', 'response': 'accept', 'sender_id': sender_id, 'receiver_id': receiver_id, 'sender_username': sender_username, 'receiver_username': receiver_username}, mainRoomSocket);
//    mainRoomSocket.send(JSON.stringify({'type': 'friend_request_response', 'response': 'accept', 'sender_id': sender_id, 'receiver_id': receiver_id}));
  });

  declineButton.addEventListener('click', function() {
    console.log('Decline button clicked');
    sendMessagesBySocket({'type': 'friend_request_response', 'response': 'decline', 'sender_id': sender_id, 'receiver_id': receiver_id, 'sender_username': sender_username, 'receiver_username': receiver_username}, mainRoomSocket);
//    mainRoomSocket.send(JSON.stringify({'type': 'friend_request_response', 'response': 'decline', 'sender_id': sender_id, 'receiver_id': receiver_id}));
  });
}
function addFriendRequestNotification(data)
{
  const notificationDropdown = document.getElementById('navbarDropdownNotifications');
  const notificationDropdownClass = document.getElementById('notificationClassContent');
  receiver_username = data.receiver_username;
  receiver_id = data.receiver_id;
  sender_username = data.receiver_username;
  sender_username = data.sender_username;
  sender_id = data.sender_id;
  sender_avatar_url = data.sender_avatar_url;

  // Remove the 'no notifications' message
  removeEmptyMessage();

  // Create a new notification element
  const newNotification = document.createElement('li');
  newNotification.classList.add('dropdown-item');

  // Create an img element for the avatar
  const avatar = createAvatarElement(sender_avatar_url);

  // Create a span element for the message
  const message = createMessageElement(sender_username, ' sent you a friend request.');

  // Append the avatar and message to the newNotification element
  appendAvatarAndMessage(avatar, message, newNotification);

  // Add button to accept the friend request represented by accept png
  const acceptButton = createAcceptButton(sender_id, receiver_id, newNotification);
  
  // Add button to decline the friend request represented by decline png
  const declineButton = createDeclineButton(sender_id, receiver_id, newNotification);

  // Change default down icon notification to the new notification icon
  changeNotificationIconToUp(notificationDropdownClass, newNotification, notificationDropdown);

  // Set unreadNotifications to true
  unreadNotifications = true;

  // Add event listener to the buttons accept and decline
  listenUserResponse(acceptButton, declineButton, sender_id, receiver_id, sender_username, receiver_username);
}

/* -------------------Friend Response notification------------------- */
function addFriendResponseNotification(data)
{
  const notificationDropdown = document.getElementById('navbarDropdownNotifications');
  const notificationDropdownClass = document.getElementById('notificationClassContent');
  receiver_username = data.receiver_username;
  receiver_id = data.receiver_id;
  sender_username = data.receiver_username;
  sender_username = data.sender_username;
  sender_id = data.sender_id;
  receiver_avatar_url = data.receiver_avatar_url;

  // Remove the 'no notifications' message
  removeEmptyMessage();

  // Create a new notification element
  const newNotification = document.createElement('li');
  newNotification.classList.add('dropdown-item');

  // Create an img element for the avatar
  const avatar = createAvatarElement(receiver_avatar_url);

  // Create a span element for the message
  if (data.response === 'accept') {
    const message = createMessageElement(receiver_username, ' accepted your friend request.');
    appendAvatarAndMessage(avatar, message, newNotification);
  }
  else {
    const message = createMessageElement(receiver_username, ' declined your friend request.');
    appendAvatarAndMessage(avatar, message, newNotification);
  }

  // Change default down icon notification to the new notification icon
  changeNotificationIconToUp(notificationDropdownClass, newNotification, notificationDropdown);

  // Set unreadNotifications to true
  unreadNotifications = true;
}