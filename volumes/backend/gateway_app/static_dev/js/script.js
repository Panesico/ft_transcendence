function listenForm(form) {
  // console.log('form: ', form);
  console.log('form: ', form);
  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    // console.log('Form submitted', e);

    const formData = new FormData(form);
    let url = form.action;

    const jsonObject = {};
    formData.forEach((value, key) => {
      jsonObject[key] = value;
    });
    // console.log('formData: ', formData);
    try {
      // console.log('url: ', url);
      let request = new Request(url, {
        method: 'POST',
        headers: {
          'X-Requested-With': 'XMLHttpRequest',
          'Content-Type': 'application/json',
          'X-CSRFToken': getCookie('csrftoken')
        },
        credentials: 'include',
        body: JSON.stringify(jsonObject)
      });
      // console.log('handleFormSubmission > request: ', request);
      const response = await fetch(request);
      const data = await response.json();

      console.log('handleFormSubmission > response: ', response);

      if (!response.ok && !data.html.includes('class="errorlist nonfield')) {
        throw new Error(`HTTP error - status: ${response.status}`);
      }

      // console.log('data: ', data);
      if (data.status != 'error' && data.message && !data.html) {
        console.log('data.message: ', data.message);
        if (data.message === 'Login successful') {
          sessionStorage.setItem('afterLogin', 'true');
        } else if (data.message === 'Sign up successful') {
          sessionStorage.setItem('afterSignup', 'true');
        }
        window.location.replace('/');
      } else
        document.querySelector('main').innerHTML = data.html;

      if (!data?.html?.includes('class="errorlist nonfield')) {
        if (data.message != 'starting Semi-Final 1')
          showMessage(data.message);
        else
          announceGame(
              document.querySelector('h1').textContent,
              `${document.getElementById('namePlayer1').textContent} vs ${
                  document.getElementById('namePlayer2').textContent}`);
      }
    } catch (error) {
      console.error('Form submission error:', error);
      document.querySelector('main').innerHTML =
          '<h1>Form submission error</h1>';
    }
  });
}

function listenFormUpload(form) {
  console.log('listenFormUpload: ', form);
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
          body: formData  // FormData handles the file and other fields automatically
        });

        // Send the request and wait a response
        const response = await fetch(request);
        const data = await response.json();

        console.log('handleFormSubmission > response: ', response);

        if (!response.ok) {
          console.error('HTTP error - status:', response.status);
          throw new Error(`HTTP error - status: ${response.status}`);
        }

        // Handle the response data
        if (data.status != 'error' && data.message) {
          console.log('data.message: ', data.message);
          window.location.replace('/');
        }
        else
          document.querySelector('main').innerHTML = data.html;
        if (!data?.html?.includes('class="errorlist nonfield')) {
          showMessage(data);
        }
        loadAdditionalJs(window.location.pathname);

      } catch (error) {
        console.error('Form submission error:', error);
        document.querySelector('main').innerHTML = '<h1>Form submission error</h1>';
      }
    });
}

// Intercept form submissions for AJAX processing
async function handleFormSubmission() {
  const form = document.querySelector('form');
  const formUpload = document.getElementById('file-upload')
  const formGeneral = document.getElementById('type-general')
  const formSecurity = document.getElementById('type-security')
  const formInviteFriend = document.getElementById('inviteFriendModal')

  if (formInviteFriend) {
    listenFriendInvitation(formInviteFriend);
    console.log('formInviteFriend: ', formInviteFriend);
  }
  else if (formUpload) {
    listenFormUpload(formUpload);
  }
  else if (form) {
    console.log('form: ', form);
    listenForm(form);
  }
  
  if (formGeneral) {
    console.log('formGeneral: ', formGeneral);
    listenForm(formGeneral);
  }

  if (formSecurity) {
    console.log('formSecurity: ', formSecurity);
    listenForm(formSecurity);
  }

}

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
    // console.log('data: ', data);
    if (data.message && (data.message === 'Logged out successfully')) {
      sessionStorage.setItem('afterLogout', 'true');
      window.location.replace('/');
    } else
      document.querySelector('main').innerHTML = data.html;

    showMessage(data.message);
    handleFormSubmission();
  } catch (error) {
    console.error('Error loading content:', error);
    document.querySelector('main').innerHTML = '<h1>Error loading content</h1>';
  }
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
window.onload = () => {
  // console.log('onload');
  // loadContent(window.location.pathname);
  handleFormSubmission();
};

// Display modal after redirect
document.addEventListener('DOMContentLoaded', () => {
  // console.log(
  //     'sessionStorage.getItem(\'afterLogin\'): ',
  //     sessionStorage.getItem('afterLogin'));
  if (sessionStorage.getItem('afterLogin') === 'true') {
    let message = 'Login successful';
    showMessage(message);
    sessionStorage.removeItem('afterLogin');
  } else if (sessionStorage.getItem('afterLogout') === 'true') {
    let message = 'Logged out successfully';
    showMessage(message);
    sessionStorage.removeItem('afterLogout');
  } else if (sessionStorage.getItem('afterSignup') === 'true') {
    let message = 'Signup successful';
    showMessage(message);
    sessionStorage.removeItem('afterSignup');
  }
});

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