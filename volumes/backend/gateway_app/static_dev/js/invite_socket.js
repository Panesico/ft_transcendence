let inviteFriendSocket; // Make the websocket accessible globally

isFocused = false;

function update_dropdown(matching_usernames)
{
  const usernameInput = document.getElementById('usernameInput');
  const dropdown = document.getElementById('suggestions-list');  // The dropdown element (create this in HTML)

  // Clear any previous suggestions
  dropdown.innerHTML = '';

  if (matching_usernames.length === 0) {
    //dropdown.classList.remove('show');
    dropdown.style.display = 'none';
    return;
  }

  dropdown.style.display = 'block';
  dropdown.style.overflow = 'auto';
  dropdown.style.maxHeight = '200px';
  matching_usernames.forEach(username => {
    const suggestionItem = document.createElement('div');
    suggestionItem.classList.add('suggestion-item');
    suggestionItem.textContent = username;

    // Click handler to fill the input field with the selected suggestion
    suggestionItem.addEventListener('click', () => {
      usernameInput.value = username;
      dropdown.style.display = 'none';
    });

   
    dropdown.appendChild(suggestionItem);
  });

  // Optionally close the dropdown when clicking outside
  // document.addEventListener('click', (event) => {
  //   if (!suggestionsList.contains(event.target) && event.target !== usernameInput) {
  //       suggestionsList.style.display = 'none';
  //   }
  // });

}
function onModalOpen(userID) {
  console.log('Modal is open');

  /* WebSocket */
  inviteFriendSocket = new WebSocket('wss://localhost:8443/wss/inviteafriend/');
  // const inviteFriendSocket = new WebSocket('/wss/gamecalc/');

  inviteFriendSocket.onopen = function(e) {
    console.log('inviteFriendSocket socket connected');
    inviteFriendSocket.send(JSON.stringify({type: 'start', 'userID': userID}));
  };

  inviteFriendSocket.onmessage = function(e) {
    const data = JSON.parse(e.data);
    const message = data['message'];
    const type = data['type'];
    console.log('Received message from socket: ', message);
    
    if (type === 'suggestions') {
      matching_usernames = data['suggestions'];
      console.log('Matching usernames:', matching_usernames);
      update_dropdown(matching_usernames);
    }
  };

  inviteFriendSocket.onclose = function(e) {
    console.warn('inviteFriendSocket socket closed unexpectedly');
  };

  // Ensure inviteFriendSocket is defined before calling send
  if (inviteFriendSocket) {
    console.log('inviteFriendSocket.readyState:', inviteFriendSocket.readyState);
  }
  else {
    console.error('inviteFriendSocket is not defined');
  }
// if (inviteFriendSocket && inviteFriendSocket.readyState === WebSocket.OPEN) {
//   inviteFriendSocket.send(JSON.stringify({'query': 'test'}));
// } else {
//   console.error('WebSocket is not open or not defined.');
// }
}

function onModalClose()
{
  const formInviteFriend = document.getElementById('type-invite-friend');

  // Reset the form
  if (formInviteFriend) {
    formInviteFriend.reset();
    console.log('Invite Friend form has been reset');
  } else {
    console.warn('Invite Friend form not found');
  }

  // Close the WebSocket
  if (inviteFriendSocket && inviteFriendSocket.readyState === WebSocket.OPEN) {
    inviteFriendSocket.close();
    console.log('Modal is closed and WebSocket is closed');
  } else {
    console.warn('WebSocket is not open or already closed');
  }
  
}
function listenFriendInvitation(modal) {
  console.log('inviteFrienModal');
  let inputField = document.getElementById('username_input');
  let userID = document.getElementById('userID').value;

  console.warn('User ID:', userID);
  if (userID === '' || userID === undefined) {
    console.error('User ID is not defined');
    // exit ===> handle error
  }  

  modal.addEventListener('show.bs.modal', () => {
    onModalOpen(userID);
    
  })

  // Listen for focus on the input field
  modal.addEventListener('focus', () => {
    isFocused = false;  // Mark input as not focused
    console.log("Input lost focus");
  });

  // Listen for blur (when user leaves the input field)
  modal.addEventListener('blur', () => {
    isFocused = true;  // Mark input as focused
    console.log("Input is focused");
    
  });

  // Event listen for key press
  console.log('inputField.addEventListene:');
  window.addEventListener('keydown', (e) => {
    // get the key pressed
  if (isFocused)
    {
      const pressedKey = e.key;
      console.log(`Key pressed: ${pressedKey}`);
      inviteFriendSocket.send(JSON.stringify({type: 'input', 'key': pressedKey}));
    }
  });

  modal.addEventListener('hidden.bs.modal', () => {
    onModalClose();

});
}