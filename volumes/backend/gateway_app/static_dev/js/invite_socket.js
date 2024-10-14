/* ----------INVITE FRIEND SEARCH */
// The file aim is to handle the search for friends to invite

// Make the websocket accessible globally
let inviteFriendSocket;
//Boolean to check if the input field is focused
isFocused = false;

// Function to get the CSRF token
function listenSubmit(form) {
  console.log('form: ', form);
  form.addEventListener('submit', async (e) => {
	e.preventDefault();
	// console.log('Form submitted', e);
	const formData = new FormData(form);
	let url = form.action;

	try {
	  // Create a new request for file upload
	  let request = new Request(url, {
		method: 'POST',
		headers: {
		  'X-Requested-With': 'XMLHttpRequest',  // To identify as AJAX request
		  'X-CSRFToken': getCookie('csrftoken')  // If CSRF token is required
		},
		credentials: 'include',  // Include cookies (if necessary)
		body: formData           // FormData handles the file and other fields
								 // automatically
	  });

	  // Send the request and wait a response
	  const response = await fetch(request);
	  const data = await response.json();

	  console.log('handleFormSubmission > response: ', response);


	  if (!response.ok) {
		console.error('HTTP error - status:', response.status);
		throw new Error(`HTTP error - status: ${response.status}`);
	  }

	  if (!data?.html?.includes('class="errorlist nonfield')) {
	  	displayMessageInModal(data.message);
      if (data.message === 'Invitation sent!') {
        console.warn('Send invitation to ', data.username);
        // send invitation to the user
        sendFriendRequest(data.sender_username, data.sender_id, data.sender_avatar_url,
          data.receiver_username, data.receiver_id
        );
      }

	  }
    console.log('handleFormSubmission > data: ', data);
	  handleFormSubmission();

	} catch (error) {
	  console.error('Form submission error:', error);
	  document.querySelector('main').innerHTML =
		  '<h1>Form submission error</h1>';
	}
  });
}

// Function to upate the dropdown with matching usernames
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

  // Dropdown styling
  dropdown.style.display = 'block';
  dropdown.style.overflowY = 'auto';
  dropdown.style.overflowX = 'hidden';
  dropdown.style.maxHeight = '200px';
  dropdown.style.border = '4px solid #fff';


  // Create a suggestion item for each matching username
  matching_usernames.forEach(username => {
    const suggestionItem = document.createElement('div');
    suggestionItem.classList.add('suggestion-item');
    suggestionItem.textContent = username;

    // Click handler to fill the input field with the selected suggestion
    suggestionItem.addEventListener('click', () => {
      usernameInput.value = username;
      dropdown.style.display = 'none';

      //Click on submit button
      const submitButton = document.getElementById('submit-invite-friend');
      if (submitButton) {
        submitButton.click();
      }
    });

    // Append the suggestion item to the dropdown
    dropdown.appendChild(suggestionItem);
  });

  // Close the dropdown when clicking outside
  document.addEventListener('click', (event) => {
    if (!dropdown.contains(event.target) && event.target !== usernameInput) {
      dropdown.style.display = 'none';
    }
  });

}

// We open the websocket only when the modal is open
function onModalOpen(userID, modal) {
  console.log('Modal is open');

  /* WebSocket */
  inviteFriendSocket = new WebSocket('wss://localhost:8443/wss/inviteafriend/');

  inviteFriendSocket.onopen = function(e) {
    console.log('inviteFriendSocket socket connected');
//    inviteFriendSocket.send(JSON.stringify({type: 'start', 'userID': userID}));
    sendMessagesBySocket({type: 'start', 'userID': userID}, inviteFriendSocket);
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

  modal.addEventListener('hidden.bs.modal', () => {
    onModalClose(modal);
});
}

function onModalClose(modal)
{
  const formInviteFriend = document.getElementById('type-invite-friend');
  console.log('Modal is closed');

  // Reset the form
  if (formInviteFriend) {
    formInviteFriend.reset();
    console.log('Invite Friend form has been reset');
  } else {
    console.warn('Invite Friend form not found');
  }

  // Close properly the websocket
  if (inviteFriendSocket && inviteFriendSocket.readyState === WebSocket.OPEN) {
    inviteFriendSocket.close();
    console.log('Modal is closed and WebSocket is closed');
  } else {
    console.warn('WebSocket is not open or already closed');
  }
  
}

// Function to listen for the friend invitation
function listenFriendInvitation(modal, form) {
  let inputField = document.getElementById('username_input');
  let userID = document.getElementById('userID').value;

  console.warn('User ID:', userID);
  if (userID === '' || userID === undefined) {
    console.error('User ID is not defined');
    // exit ===> handle error
  }  

  // Listen for modal open
  modal.addEventListener('show.bs.modal', () => {
    onModalOpen(userID, modal);
    
  })

  // Listen for focus on the input field
  modal.addEventListener('focus', () => {
    isFocused = false;  // Mark input as not focused
  });

  // Listen for blur (when user leaves the input field)
  modal.addEventListener('blur', () => {
    isFocused = true;  
  });

  // Event listen for key press
  console.log('inputField.addEventListene:');
  window.addEventListener('keydown', (e) => {

  // get the key pressed
  if (isFocused && inviteFriendSocket.readyState === WebSocket.OPEN)
    {
      const pressedKey = e.key;
//      inviteFriendSocket.send(JSON.stringify({type: 'input', 'key': pressedKey}));
      sendMessagesBySocket({type: 'input', 'key': pressedKey}, inviteFriendSocket);
    }
  });

  // Listen for form submission
  if (form)
    listenSubmit(form);
}
