// script.js
const fetchedFiles = new Set();

// Show message modal
function showMessage(data) {
  if (data.message) {
    console.log('data.message: ', data.message);
    let messageModal =
        new bootstrap.Modal(document.getElementById('messageModal'));
    messageModal.show();
    document.getElementById('messageContent').innerText = data.message;
  }
}

// Load additional JS based on current path
function loadAdditionalJs(path) {
  let url = '/static/js/';

  if (path === '/game') {
    url += 'pong.js';
    loadJs(url);
  }
  //  else if (path === '/profile') {
  //   url += 'profile.js';
  //   loadJs(url);
  // }

  function loadJs(url) {
    if (url.length > 11 && !document.querySelector(`script[src="${url}"]`)) {
      // console.log(`%cLoading ${url}`, 'color: yellow; font-weight: bold;');
      const script = document.createElement('script');
      script.src = url;
      script.type = 'text/javascript';
      document.body.appendChild(script);
      fetchedFiles.add(url);
    }
  }
}

// Get value of a cookie
function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== '') {
    let cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
      let cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === (name + '=')) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}

/* WebSocket */
const formSocket = new WebSocket('wss://localhost:8443/wss/profileapi/');
// const formSocket = new WebSocket('/wss/gamecalc/');

formSocket.onopen = function(e) {
  console.log('formSocket socket connected');
};

formSocket.onmessage = function(e) {
  const data = JSON.parse(e.data);
  const message = data['message'];
  console.log('Received message from socket: ', message);
};

formSocket.onclose = function(e) {
  console.error('formSocket socket closed unexpectedly');
};

function sendMessage(message) {
  console.log('Sending message to socket: ', message);
  formSocket.send(JSON.stringify({'message': message}));
}

// Intercept form submissions for AJAX processing
async function handleFormSubmission() {
  const form = document.querySelector('form');
  const formUpload = document.getElementById('file-upload')

  if (formUpload) {
    console.log('formUpload: ', formUpload);
    formUpload.addEventListener('submit', async (e) => {
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
        handleFormSubmission();
        loadAdditionalJs(window.location.pathname);

      } catch (error) {
        console.error('Form submission error:', error);
        document.querySelector('main').innerHTML = '<h1>Form submission error</h1>';
      }
    });
  }

  else if (form) {
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
            sendMessage('websocket: data received');
            sessionStorage.setItem('afterLogin', 'true');
          } else if (data.message === 'Sign up successful') {
            sessionStorage.setItem('afterSignup', 'true');
          }
          window.location.replace('/');
        } else
          document.querySelector('main').innerHTML = data.html;

        if (!data?.html?.includes('class="errorlist nonfield')) {
          showMessage(data);
        }
        handleFormSubmission();
        loadAdditionalJs(window.location.pathname);
      } catch (error) {
        console.error('Form submission error:', error);
        document.querySelector('main').innerHTML =
            '<h1>Form submission error</h1>';
      }
    });
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

    showMessage(data);
    handleFormSubmission();
    loadAdditionalJs(path);
  } catch (error) {
    console.error('Error loading content:', error);
    document.querySelector('main').innerHTML = '<h1>Error loading content</h1>';
  }
}

// Handle navigation
function navigate(e, path) {
  e.preventDefault();

  for (const jsFile of fetchedFiles) {
    // console.log(`%cRemoving ${jsFile}`, 'color: red; font-weight: bold;');
    const script = document.querySelector(`script[src="${jsFile}"]`);
    script.remove();
    fetchedFiles.delete(jsFile);
  }

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
  const data = {};
  if (sessionStorage.getItem('afterLogin') === 'true') {
    data.message = 'Login successful';
    showMessage(data);
    sessionStorage.removeItem('afterLogin');
  } else if (sessionStorage.getItem('afterLogout') === 'true') {
    data.message = 'Logged out successfully';
    showMessage(data);
    sessionStorage.removeItem('afterLogout');
  } else if (sessionStorage.getItem('afterSignup') === 'true') {
    data.message = 'Signup successful';
    showMessage(data);
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