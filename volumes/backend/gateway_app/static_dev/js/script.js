// Load content based on current path
async function loadContent(path) {
  // console.log('loadContent');
  let url = (path === '/') ? path : `${path}/`;

  // console.log('url: ', url);
  // Fetch content from Django and inject into main
  try {
    let request = new Request(url, {
      headers: {'X-Requested-With': 'XMLHttpRequest'},
      credentials: 'include',
    });
    // console.log('loadContent > request: ', request);

    const response = await fetch(request);

    // console.log('loadContent > response: ', response);
    if (!response.ok) {
      throw new Error(`HTTP error - status: ${response.status}`);
    }
    const data = await response.json();
    if (data.message && (data.message === 'Logged out successfully')) {
      sessionStorage.setItem('afterLogout', 'true');
      window.location.replace('/');
    } else
      document.querySelector('main').innerHTML = data.html;

    displayMessageInModal(data.message);
    displayMessageInModal(data.message);
    handleFormSubmission();
  } catch (error) {
    console.error('Error loading content:', error);
    document.querySelector('main').innerHTML = '<h1>Error loading content</h1>';
  }
}

function isUserLoggedIn() {
  console.log(
      'isUserLoggedIn > sessionStorage.getItem(afterLogin): ',
      sessionStorage.getItem('afterLogin'));
  return sessionStorage.getItem('afterLogin') === 'true';
}

// Handle navigation
function navigate(e, path) {
  e.preventDefault();

  // Push the new state into the browser's history
  if (path === '/api/auth/logout') {
    window.history.pushState({}, '', '/');
  } else
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
  console.log('DOMContentLoaded');
  if (sessionStorage.getItem('afterLogin') === 'true') {
    let message = 'Login successful';
    displayMessageInModal(message);
    sessionStorage.removeItem('afterLogin');
  } else if (sessionStorage.getItem('afterLogout') === 'true') {
    let message = 'Logged out successfully';
    displayMessageInModal(message);
    sessionStorage.removeItem('afterLogout');
  } else if (sessionStorage.getItem('afterSignup') === 'true') {
    let message = 'Signup successful';
    displayMessageInModal(message);
    sessionStorage.removeItem('afterSignup');
  } else if (sessionStorage.getItem('afterProfileUpdate') === 'true') {
    let message = 'Profile updated';
    displayMessageInModal(message);
    sessionStorage.removeItem('afterProfileUpdate');
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