// Load content based on current path
async function loadContent(path) {
  // console.log('loadContent');
  let url = (path === '/') ? path : `${path}/`;

  //if url ends by //, remove the last /
  console.log('url: ', url);
  if (url.endsWith('//')) {
    url = url.slice(0, -1);
  }

  // Check go back arrow has been clicked
  if (url === '/back') {
    console.log('Go back arrow clicked');
  }

  // console.log('url: ', url);
  // Fetch content from Django and inject into main
  try {
    let request = new Request(url, {
      headers: { 'X-Requested-With': 'XMLHttpRequest' },
      credentials: 'include',
    });
    // console.log('loadContent > request: ', request);

    const response = await fetch(request);

    // console.log('loadContent > response: ', response);
    if (!response.ok) {
      throw new Error(`HTTP error - status: ${response.status}`);
    }
    const data = await response.json();

    console.log('loadContent > data: ', data);

    if (data.type && data.message && (data.type === 'logout_successful')) {
      sessionStorage.setItem('afterLogout', 'true');
      sessionStorage.setItem('afterLogoutMessage', data.message);
      // disconnect main room socket
      handleRefresh("logout");
      closeMainRoomSocket();
      console.log('loadContent > logout_successful');
    }
    else {
      document.querySelector('main').innerHTML = data.html;
    }
    console.log('loadContent > main updated');

    displayMessageInModal(data.message);
    handleFormSubmission();
  } catch (error) {
    console.error('Error loading content:', error);
    document.querySelector('main').innerHTML = '<h1>Error loading content</h1>';
  }
}

// function isUserLoggedIn() {
//   console.log(
//     'isUserLoggedIn > sessionStorage.getItem(afterLogin): ',
//     sessionStorage.getItem('afterLogin'));
//   return sessionStorage.getItem('afterLogin') === 'true';
// }

// Handle navigation
function navigate(e, path) {
  e.preventDefault();

  // Push the new state into the browser's history
  window.history.pushState({}, '', path);

  loadContent(path);
}


// Listen for popstate events (Back/Forward buttons)
window.onpopstate = () => {
  loadContent(window.location.pathname);
};

// Initialise the correct content on page load
// window.onload = () => {
//   console.log('onload');
//   // loadContent(window.location.pathname);
//   handleFormSubmission();
// };

// async function getProfileData() {
//   try {
//     let request = new Request('/profile/', {
//       headers: {'X-Requested-With': 'XMLHttpRequest'},
//       credentials: 'include',
//     });

//     const response = await fetch(request);
//     if (!response.ok) {
//       throw new Error(`HTTP error - status: ${response.status}`);
//     }
//     const data = await response.json();
//     console.log('getProfileData > data: ', data);
//     return data;
//   } catch (error) {
//     console.error('Error getting profile data:', error);
//     return null;
//   }
// }

document.addEventListener('DOMContentLoaded', () => {
  console.log('Session Storage listener > DOMContentLoaded');

  // The message should be set in sessionStorage before the page is reloaded
  // because the message needs to be translated

  if (sessionStorage.getItem('afterLogin') === 'true') {
    let message = sessionStorage.getItem('afterLoginMessage');
    displayMessageInModal(message);
    sessionStorage.removeItem('afterLogin');
    sessionStorage.removeItem('afterLoginMessage');

  } else if (sessionStorage.getItem('afterLogout') === 'true') {
    let message = sessionStorage.getItem('afterLogoutMessage');
    displayMessageInModal(message);
    sessionStorage.removeItem('afterLogout');
    sessionStorage.removeItem('afterLogoutMessage');

  } else if (sessionStorage.getItem('afterSignup') === 'true') {
    let message = sessionStorage.getItem('afterSignupMessage');
    displayMessageInModal(message);
    sessionStorage.removeItem('afterSignup');
    sessionStorage.removeItem('afterSignupMessage');

  } else if (sessionStorage.getItem('afterProfileUpdate') === 'true') {
    let message = sessionStorage.getItem('afterProfileUpdateMessage');
    displayMessageInModal(message);
    sessionStorage.removeItem('afterProfileUpdate');
    sessionStorage.removeItem('afterProfileUpdateMessage');

  } else if (sessionStorage.getItem('afterAvatarUpdate') === 'true') {
    // let message = 'Avatar updated';
    let message = sessionStorage.getItem('afterAvatarUpdateMessage');
    displayMessageInModal(message);
    sessionStorage.removeItem('afterAvatarUpdate');
    sessionStorage.removeItem('afterAvatarUpdateMessage');

  } else if (sessionStorage.getItem('afterBlock') === 'true') {
    let message = sessionStorage.getItem('afterBlockMessage');
    displayMessageInModal(message);
    sessionStorage.removeItem('afterBlock');
    sessionStorage.removeItem('afterBlockMessage');

  } else if (sessionStorage.getItem('afterUnblock') === 'true') {
    let message = sessionStorage.getItem('afterUnblockMessage');
    displayMessageInModal(message);
    sessionStorage.removeItem('afterUnblock');
    sessionStorage.removeItem('afterUnblockMessage');
  }
});


// Display modal after redirect

function changeLanguage(lang) {
  console.log('CHANGELANGUAGE > lang: ', lang);

  const formData = new FormData();
  formData.append('language', lang);
  // Redirects the user back to the current page after changing the language
  formData.append('next', window.location.pathname);

  fetch(`/i18n/setlang/`, {
    method: 'POST',
    headers: {
      'X-CSRFToken': getCookie('csrftoken'),
      'X-Requested-With': 'XMLHttpRequest'
    },
    credentials: 'include',
    body: formData,
  })
    .then(response => {
      if (response.ok) {
        window.location.reload();
      } else {
        console.error('Error changing language:', response.statusText);
      }
    })
    .catch(error => console.error('Fetch error:', error));
}