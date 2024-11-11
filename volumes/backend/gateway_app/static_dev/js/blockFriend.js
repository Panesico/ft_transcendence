
async function checkIfImBlocked(friendId) {
  try {
    const request = new Request(`/friend_profile/${friendId}/`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCookie('csrftoken'),
        'X-Requested-With': 'XMLHttpRequest'
      },
      credentials: 'include'
    });
    const response = await fetch(request);
    if (!response.ok) {
      throw new Error('Error fetching friend profile');
    }
    const data = await response.json();
    // console.log('checkIfImBlocked > data:', data);
    console.log('checkIfImBlocked > data.im_blocked:', data.im_blocked);
    return data.im_blocked;
  } catch (error) {
    console.error('Error checking if blocked:', error);
    return false;
  }
}

// Check if the friend is blocked by the user
async function checkIfBlocked(friendId) {
  try {
    const request = new Request(`/friend_profile/${friendId}/`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCookie('csrftoken'),
        'X-Requested-With': 'XMLHttpRequest'
      },
      credentials: 'include'
    });
    const response = await fetch(request);
    if (!response.ok) {
      throw new Error('Error fetching friend profile');
    }
    const data = await response.json();
    // console.log('checkIfBlocked > data:', data);
    console.log('checkIfBlocked > data.is_blocked:', data.is_blocked);
    return data.is_blocked;
  } catch (error) {
    console.error('Error checking if blocked:', error);
    return false;
  }
}

async function blockFriend(friendId) {
  console.log('blockFriend > friendId:', friendId);
  const blockSwitch = document.getElementById(`blockSwitch-${friendId}`);
  console.log('blockFriend > blockSwitch:', blockSwitch);

  const checked = blockSwitch.checked;
  console.log('blockFriend > checked:', checked);

  let url;
  if (checked) {
    blockSwitch.nextElementSibling.style.color = 'red';
    url = `/blockFriend/${friendId}/`;
  } else {
    blockSwitch.nextElementSibling.style.color = 'black';
    url = `/unblockFriend/${friendId}/`;
  }

  try {
    const request = new Request(url, {
      method: 'POST',
      headers: {
        'X-Requested-With': 'XMLHttpRequest',
        'Content-Type': 'application/json',
        'X-CSRFToken': getCookie('csrftoken'),
      },
      credentials: 'include',
    });
    const response = await fetch(request);

    if (!response.ok) {
      throw new Error('HTTP error, status = ' + response.status);
    }
    const data = await response.json();
    console.log('blockFriend > data:', data);

    if (data.status === 'success') {
      if (window.location.pathname.includes('my_friends')) {
        document.querySelector('main').innerHTML = data.html;
      }
      if (checked) {
        // displayMessageInModal(afterBlockMsg);
        document.getElementById('contactGameInviteContainer').style.display = 'none';
        document.getElementById('chat-modal-footer').style.display = 'none';
      }
      else {
        // displayMessageInModal(afterUnblockMsg);
        document.getElementById('contactGameInviteContainer').style.display = 'flex';
        document.getElementById('chat-modal-footer').style.display = 'flex';
        document.getElementById('messageInput').value = '';
      }
    }
  } catch (error) {
    console.error('Error:', error);
  }
}
