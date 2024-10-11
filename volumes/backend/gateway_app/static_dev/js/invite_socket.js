let inviteFriendSocket; // Make the websocket accessible globally

isFocused = false;

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

	  if (!response.ok && response.status == 400) {
		// window.location.replace('/edit_profile');
		// displayMessageInModal('No file selected');
	  }

	  else if (!response.ok) {
		console.error('HTTP error - status:', response.status);
		throw new Error(`HTTP error - status: ${response.status}`);
	  }

	  // // Handle the response data
	  // if (data.status != 'error' && data.message) {
		// console.log('data.message: ', data.message);
		// window.location.replace('/');
	  // } else
		// document.querySelector('main').innerHTML = data.html;
	  if (!data?.html?.includes('class="errorlist nonfield')) {
	  	displayMessageInModal(data.message);
      if (data.message === 'Invitation sent!') {
        console.warn('Send invitation to ', data.username);
        // send invitation to the user
        sendFriendRequest(data.username, data.user_id);
      }

	  }
	  // if (uploadFileNotEmpty() == false) {
	  //   alert("No file selected");
	  //   window.location.replace('/edit_profile');
	  // }

	  handleFormSubmission();
	  // loadAdditionalJs(window.location.pathname);

	} catch (error) {
	  console.error('Form submission error:', error);
	  document.querySelector('main').innerHTML =
		  '<h1>Form submission error</h1>';
	}
  });
}

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
  dropdown.style.overflowY = 'auto';
  dropdown.style.overflowX = 'hidden';
  dropdown.style.maxHeight = '200px';
  dropdown.style.border = '4px solid #fff';
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

function onModalClose(modal)
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
function listenFriendInvitation(modal, form) {
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
    onModalClose(modal);
    
  });
  if (form)
    listenSubmit(form);
}

