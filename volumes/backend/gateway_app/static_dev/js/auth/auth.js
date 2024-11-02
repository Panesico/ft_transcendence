// TODO -- It doesnt work I think...
function deleteCookie(name) {
    document.cookie = name + '=; Max-Age=-99999999; path=/;';
}

// TODO -- Client secret changes over a certain period, making it unsuable.
// Your 42 OAuth settings from Django variables

// Function to handle OAuth code once available
function handleOAuthCode(oauth_callback_url) {
    const oauthCode = getCookie('oauth_code');
    if (oauthCode) {
        console.log("OAuth code found in cookie:", oauthCode);
        // Delete the OAuth code cookie after retrieving it
        deleteCookie('oauth_code');

        // Send the code to the server to exchange for an access token
        fetch(oauth_callback_url, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": getCookie('csrftoken')
				
            },
            body: JSON.stringify({ code: oauthCode })
        }).then(response => {
            if (response.ok) {
                window.location.href = "/";
            } else {
                console.error("OAuth authentication failed");
            }
        }).catch(error => {
            console.error("Error during OAuth authentication:", error);
        });
    }
}

// When the user clicks the "Login with 42" button
function loginButton42() {
	const configElement = document.getElementById('config42login');
	const CLIENT_ID = configElement.getAttribute('data-client-id');
	const REDIRECT_URI = configElement.getAttribute('data-redirect-uri');
	const STATE = Math.random().toString(36).substring(7); // Generate random state to prevent CSRF attacks
	const oauth_callback_url = configElement.getAttribute('oauth-view-url');
    const authUrl = `https://api.intra.42.fr/oauth/authorize?client_id=${CLIENT_ID}&redirect_uri=${encodeURIComponent(REDIRECT_URI)}&response_type=code&scope=public&state=${STATE}`;
    const width = 600;
    const height = 600;
    const left = (window.innerWidth / 2) - (width / 2);
    const top = (window.innerHeight / 2) - (height / 2);
    const authWindow = window.open(authUrl, "42OAuthLogin", `width=${width},height=${height},top=${top},left=${left},menubar=no,toolbar=no,location=no,status=no,scrollbars=no,resizable=no`);

    // Polling for OAuth code every second after the popup is opened
    const intervalId = setInterval(function() {
        // Check for the OAuth code in cookies
        const oauthCode = getCookie('oauth_code');
        if (oauthCode) {
            clearInterval(intervalId); // Stop polling once we get the OAuth code
            authWindow.close(); // Close the popup

            // Handle the OAuth code (send to server, etc.)
            handleOAuthCode(oauth_callback_url);
        }
    }, 1000); // Check every 1 second
};

function enable2FA() {
    fetch('/enable2FA/', {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCookie('csrftoken'),
            'Content-Type': 'application/json'
        },
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            const twoFaButton = document.getElementById('2fa-button');
            twoFaButton.innerHTML = 'Disable 2FA';
            twoFaButton.classList.remove('btn-primary');
            twoFaButton.classList.add('btn-danger');
            twoFaButton.setAttribute('onclick', 'disable2FA()');

            // Display QR code and OTP confirmation input
            const qrCodeDiv = document.getElementById('2fa-qr-code');
            qrCodeDiv.innerHTML = `<img src="${data.qr_code}" alt="QR Code for 2FA" />`;
            qrCodeDiv.insertAdjacentHTML('beforeend', `
                <p class="text-success">Scan the QR code, then enter the OTP below to confirm.</p>
                <input type="text" id="otp-code" placeholder="Enter OTP" class="form-control mt-2" />
                <button class="btn btn-success mt-2" onclick="confirm2FA()">Confirm 2FA</button>
            `);
        } else {
            document.getElementById('2fa-qr-code').innerHTML = `<p class="text-danger">${data.message || 'Failed to enable 2FA'}</p>`;
        }
    })
    .catch(error => {
        console.error('Error:', error);
        document.getElementById('2fa-qr-code').innerHTML = '<p class="text-danger">Failed to enable 2FA. Please try again later.</p>';
    });
}

function confirm2FA() {
    const otpCode = document.getElementById('otp-code').value;
    
    fetch('/confirm2FA/', {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCookie('csrftoken'),
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ otp_code: otpCode })
    })
    .then(response => response.json())
    .then(data => {
        const qrCodeDiv = document.getElementById('2fa-qr-code');
        if (data.status === 'success') {
            qrCodeDiv.innerHTML = '<p class="text-success">2FA confirmed successfully!</p>';
        } else {
            qrCodeDiv.innerHTML = `<p class="text-danger">${data.message || 'Failed to confirm 2FA'}</p>`;
        }
    })
    .catch(error => {
        console.error('Error:', error);
        document.getElementById('2fa-qr-code').innerHTML = '<p class="text-danger">Failed to confirm 2FA. Please try again later.</p>';
    });
}

function verify2FA() {
    // Get the OTP code entered by the user
    const otpCode = document.getElementById('otp_code').value;

    // Retrieve the user ID from the hidden div
    const userId = document.getElementById('config2FA').getAttribute('user-id-2fa');

    // Make a POST request to the URL with the appended user ID
    fetch(`/verify2FA/${userId}/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCookie('csrftoken'),
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ otp_code: otpCode })
    })
    .then(response => response.json())
    .then(data => {
        const messageDiv = document.getElementById('2fa-message');

        // Check response status and provide feedback to the user
        if (data.status === 'success') {
            messageDiv.innerHTML = '<p class="text-success">2FA verified successfully!</p>';
            // Redirect or update the UI as needed after successful verification
            window.location.replace('/');
        } else {
            messageDiv.innerHTML = `<p class="text-danger">${data.message || 'Invalid OTP code'}</p>`;
        }
    })
    .catch(error => {
        console.error('Error:', error);
        const messageDiv = document.getElementById('2fa-message');
        messageDiv.innerHTML = '<p class="text-danger">Verification failed. Please try again later.</p>';
    });
}

function disable2FA() {
    fetch('/disable2FA/', {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCookie('csrftoken'),
            'Content-Type': 'application/json'
        },
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            const twoFaButton = document.getElementById('2fa-button');
            twoFaButton.innerHTML = 'Enable 2FA';
            twoFaButton.classList.remove('btn-danger');
            twoFaButton.classList.add('btn-primary');
            twoFaButton.setAttribute('onclick', 'enable2FA()');
            document.getElementById('2fa-qr-code').innerHTML = '<p class="text-success">2FA disabled successfully</p>';
        } else if (data.error) {
            document.getElementById('2fa-qr-code').innerHTML = `<p class="text-danger">${data.error}</p>`;
        }
    })
    .catch(error => {
        console.error('Error:', error);
        document.getElementById('2fa-qr-code').innerHTML = '<p class="text-danger">Failed to disable 2FA. Please try again later.</p>';
    });
}
