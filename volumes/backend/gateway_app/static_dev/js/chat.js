function innit_listening() {
  let friendsData = [];
  const userID = document.getElementById('userID').value;
  const chatButton = document.getElementById('chatButton');
  const contactAvatar = document.getElementById('contactAvatar');
  const contactDisplayName = document.getElementById('contactDisplayName');
  const messageInput = document.getElementById('messageInput');
  const sendButton = document.getElementById('sendButton');
  const unreadCount = document.getElementById('unreadChatsCount');
  const currentChatId = document.getElementById('currentChatId');
  const blockSwitchContainer = document.getElementById('blockSwitchContainer');

  // Listen for the chat button click
  chatButton.addEventListener('click', function () {
    const request = new Request('/getFriends/', {
      method: 'GET',
      headers: {
        'X-CSRFToken': getCookie('csrftoken'),
      },
      credentials: 'include',
    });

    // Reset header
    document.getElementById('contactContainer').style.display = 'none';
    contactDisplayName.textContent = selectFriendmsg;
    contactAvatar.src = contactAvatarSrc;
    currentChatId.value = '';
    blockSwitchContainer.style.display = 'none';

    // Reset conversation
    document.getElementById('conversation').innerHTML = '';

    // Fetch the friends
    fetch(request)
      .then((response) => response.json())
      .then((data) => {
        const contactList = document.getElementById('contactList');
        console.log('data:', data);
        friendsData = data.friends;

        // Clean the contact list
        contactList.innerHTML = '';
        if (friendsData.length === 0) {
          const noFriends = document.createElement('p');
          noFriends.textContent = noFriendsmsg;
          noFriends.classList.add('no-friends-message');
          contactList.appendChild(noFriends);
          return;
        }

        friendsData.forEach((friend) => {
          checkIfImBlocked(friend.user_id).then((imBlocked) => {
            const contactItem = document.createElement('li');
            contactItem.classList.add(
              'list-group-item',
              'bg-transparent',
              'text-white',
              'custom-contact',
              'd-flex',
              'align-items-center',
              'p-3',
              'position-relative',
            );
            contactItem.dataset.contactId = friend.user_id;

            // Create avatar element
            const avatar = document.createElement('img');
            avatar.src = friend.avatar || "{% static 'images/default_avatar.png' %}";
            avatar.classList.add('rounded-circle', 'me-2');
            avatar.style.height = '2rem';
            avatar.style.width = '2rem';
            avatar.alt = 'avatar';

            // Display online status element if friend is not blocked (always create element)
            const onlineStatus = document.createElement('span');
            onlineStatus.classList.add('position-absolute', 'translate-middle', 'bg-success', 'online-status-chat');
            onlineStatus.dataset.online = friend.user_id;
            if (friend.online && !imBlocked)
              onlineStatus.style.display = 'block';
            else
              onlineStatus.style.display = 'none';

            // Create display name element
            const displayName = document.createElement('span');
            displayName.textContent = friend.display_name;

            // Add the avatar and display name to the contact item
            contactItem.appendChild(avatar);
            contactItem.appendChild(displayName);
            contactItem.appendChild(onlineStatus);

            // Add the contact item to the contact list
            contactList.appendChild(contactItem);

            if (imBlocked) {
              contactItem.classList.add('blocked-contact');
            } else {
              // Listen to the click event on the contact item
              contactItem.addEventListener('click', function (event) {
                // Remove the 'selected-contact' class from all contacts
                const contacts = contactList.getElementsByClassName('list-group-item');
                for (let c of contacts) {
                  c.classList.remove('selected-contact');
                }
                // Add the 'selected-contact' class to the clicked contact
                contactItem.classList.add('selected-contact');

                // Update the avatar and display name
                document.getElementById('contactContainer').style.display = 'flex';
                const contactAvatarAndName = document.getElementById('contactAvatarAndName');
                const contactAvatarLink = document.getElementById('contactAvatarLink');
                const contactDisplayNameLink = document.getElementById('contactDisplayNameLink');

                contactAvatarLink.href = '/userprofile/' + friend.user_id + '/';
                contactDisplayNameLink.href = '/userprofile/' + friend.user_id + '/';

                const newContactAvatarLink = contactAvatarLink.cloneNode(true);
                contactAvatarAndName.replaceChild(newContactAvatarLink, contactAvatarLink);
                const newContactDisplayNameLink = contactDisplayNameLink.cloneNode(true);
                contactAvatarAndName.replaceChild(newContactDisplayNameLink, contactDisplayNameLink);
                document.getElementById('contactDisplayName').textContent = friend.display_name;
                document.getElementById('contactAvatar').src = friend.avatar;

                newContactAvatarLink.addEventListener('click', function (event) {
                  navigate(event, `/userprofile/${friend.user_id}`);
                });
                newContactDisplayNameLink.addEventListener('click', function (event) {
                  navigate(event, `/userprofile/${friend.user_id}`);
                });

                currentChatId.value = friend.user_id;

                // update gameInvitePopup with friend.user_id
                const gameInvitePopup = document.getElementById('gameInvitePopup');
                const gameInviteForm = gameInvitePopup.querySelector('form');
                // console.log('gameInviteForm:', gameInviteForm);
                gameInviteForm.id = `chat-invite-play-${friend.user_id}`;
                gameInviteForm.action = `/invite_to_play/${friend.user_id}/`;
                const newGameInviteForm = gameInviteForm.cloneNode(true);
                gameInvitePopup.replaceChild(newGameInviteForm, gameInviteForm);
                listenForm(newGameInviteForm);

                // Add block switch
                blockSwitchContainer.style.display = 'block';
                const blockSwitch = blockSwitchContainer.querySelector('input');
                const blockSwitchDiv = blockSwitchContainer.querySelector('#blockSwitchDiv');
                blockSwitch.setAttribute('data-user-id', friend.user_id);
                blockSwitch.setAttribute('id', `blockSwitch-${friend.user_id}`);
                // Cloning and replacing the blockSwitch before adding event listener to avoid duplicates
                const newBlockSwitch = blockSwitch.cloneNode(true);
                blockSwitchDiv.replaceChild(newBlockSwitch, blockSwitch);
                newBlockSwitch.addEventListener('change', function () {
                  blockFriend(friend.user_id);
                });
                checkIfBlocked(friend.user_id).then((isBlocked) => {
                  console.log('isBlocked:', isBlocked);
                  newBlockSwitch.checked = isBlocked;
                  messageInput.placeholder = isBlocked
                    ? 'You cannot send messages to blocked users'
                    : 'Type a message to send';
                });

                // Get all the messages between the user and the selected friend
                const messageData = {
                  type: 'chat',
                  subtype: 'get_conversation',
                  sender_id: userID,
                  receiver_id: friend.user_id,
                };
                sendMessagesBySocket(messageData, mainRoomSocket);
              });
            }
            // // addOnlineStatusBadge on friends from contact list
            // sendMessagesBySocket({ 'type': 'get_connected_friends', 'sender_id': userID, }, mainRoomSocket);
          });
        });

        // Update unread messages count
        const unreadMessagesData = {
          type: 'chat',
          subtype: 'delete_unread_messages',
          user_id: userID,
        };
        sendMessagesBySocket(unreadMessagesData, mainRoomSocket);
      })
      .catch((error) => console.error('Error fetching friends:', error));
  });

  // Send message
  function sendChatMessage() {
    const selectedContact = document.querySelector('.list-group-item.selected-contact');
    const blockSwitch = document.querySelector('input[data-user-id]');

    if (!selectedContact) {
      console.error('No contact selected');
      messageInput.placeholder = 'Select a contact to send a message';
      return;
    } else if (!messageInput.value) {
      messageInput.placeholder = 'Type a message to send';
      console.error('No message to send');
      return;
    } else if (blockSwitch.checked) {
      messageInput.placeholder = 'You cannot send messages to blocked users';
      console.error('Cannot send messages to blocked users');
      return;
    }

    const selectedFriend = friendsData.find(
      (friend) => friend.user_id == selectedContact.dataset.contactId
    );
    const message = messageInput.value;
    const receiverId = selectedFriend.user_id;
    const receiverDisplayName = selectedFriend.display_name;
    const receiverAvatar = selectedFriend.avatar;
    const data = {
      type: 'chat',
      subtype: 'chat_message',
      sender_id: userID,
      receiver_id: receiverId,
      receiver_display_name: receiverDisplayName,
      receiver_avatar: receiverAvatar,
      message: message,
    };

    addSentChatMessage(message);
    sendMessagesBySocket(data, mainRoomSocket);
    console.log('data:', data);
    messageInput.value = '';
  }

  sendButton.addEventListener('click', sendChatMessage);

  messageInput.addEventListener('keydown', function (event) {
    if (event.key === 'Enter') {
      event.preventDefault();
      sendChatMessage();
    }
  });
}


function checkUnreadMessages() {
  const data = {
    'type': 'chat',
    'subtype': 'check_unread_messages',
    'user_id': userID,
  };
  sendMessagesBySocket(data, mainRoomSocket);
}

function handleChatMessages(data) {
  if (data.subtype === 'innit_listening') {
    innit_listening();
    console.log('chat listen init');
  }
  else if (data.subtype === 'chat_message') {
    const currentChatId = document.getElementById('currentChatId');
    if (currentChatId.value == data.sender_id)
      addRecvChatMessage(data);
    checkUnreadMessages();
  }
  else if (data.subtype === 'unread_messages') {
    console.log('parseSocketMessage > data.subtype:', data.subtype);
    addUnreadMessages(data);
  } else if (data.subtype === 'load_conversation') {
    loadConversation(data);
    checkUnreadMessages();
  }

}

function loadConversation(data) {
  console.log('loadConversation > data:', data);
  const conversation = document.getElementById('conversation');
  conversation.innerHTML = '';
  data.conversation.forEach(message => {
    if (message.sender_id == data.sender_id)
      addSentChatMessage(message.message);
    else
      addRecvChatMessage(message);
  });
}

function addSentChatMessage(message) {
  const chatMessages = document.getElementById('conversation');
  const messageElement = document.createElement('div');
  messageElement.classList.add('d-flex', 'flex-row', 'justify-content-end', 'mb-1');

  const messageContent = document.createElement('p');
  messageContent.classList.add('small', 'p-2', 'me-3', 'mb-0', 'rounded-3', 'bg-dark', 'text-white');
  messageContent.textContent = message;

  messageElement.appendChild(messageContent);
  chatMessages.appendChild(messageElement);
}

function addRecvChatMessage(data) {
  const chatMessages = document.getElementById('conversation');
  const messageElement = document.createElement('div');
  messageElement.classList.add('d-flex', 'flex-row', 'justify-content-start', 'mb-1');

  const messageContent = document.createElement('p');
  messageContent.classList.add('small', 'p-2', 'me-3', 'mb-0', 'rounded-3', 'bg-body-tertiary');
  messageContent.style.color = 'black';
  messageContent.textContent = data.message;

  messageElement.appendChild(messageContent);
  chatMessages.appendChild(messageElement);

  // Update unread messages count
  const unreadMessagesData = {
    type: 'chat',
    subtype: 'delete_unread_messages',
    user_id: data.sender_id,
  };
  sendMessagesBySocket(unreadMessagesData, mainRoomSocket);
}

function addUnreadMessages(data) {
  const unreadChatsCount = document.getElementById('unreadChatscount');
  unreadChatsCount.textContent = data.unread_messages_count;
}

function toggleGameInvitePopup() {
  const gameInvitePopup = document.getElementById('gameInvitePopup');
  if (gameInvitePopup.style.display === 'block')
    gameInvitePopup.style.display = 'none';
  else
    gameInvitePopup.style.display = 'block';
}
