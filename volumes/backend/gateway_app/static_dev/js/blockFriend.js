
async function checkIfImBlocked (friendId) {
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
		console.log('checkIfImBlocked > data:', data);
		console.log('checkIfImBlocked > data.im_blocked:', data.im_blocked);
		return data.im_blocked;
	} catch (error) {
		console.error('Error checking if blocked:', error);
		return false;
	}
}

// Check if the friend is blocked by the user
async function checkIfBlocked (friendId) {
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
		console.log('checkIfBlocked > data:', data);
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
	console.log('blockSwitch:', blockSwitch);
	const userId = friendId;
	const checked = blockSwitch.checked;
	console.log('checked:', checked);
	if (checked) {
		blockSwitch.nextElementSibling.style.color = 'red';
		const request = new Request(`/blockFriend/${userId}/`, {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json',
				'X-CSRFToken': getCookie('csrftoken'),
			},
		});
		try {
			const response = await fetch(request);
			if (!response.ok) {
				throw new Error('HTTP error, status = ' + response.status);
			}
			const data = await response.json();
			console.log('data:', data);
			// Mostrar el modal en caso de éxito
			if (data.status === 'success') {
				//Recargar solo la parte necesaria y mostrar el modal
			}
		} catch (error) {
			console.error('Error:', error);
		}
	}
	else {
		blockSwitch.nextElementSibling.style.color = 'black';
		const request = new Request(`/unblockFriend/${userId}/`, {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json',
				'X-CSRFToken': getCookie('csrftoken'),
			},
		});
		try {
			const response = await fetch(request);
			if (!response.ok) {
				throw new Error('HTTP error, status = ' + response.status);
			}
			const data = await response.json();
			console.log('data:', data);
			// Mostrar el modal en caso de éxito
			if (data.status === 'success') {
				sessionStorage.setItem('afterUnblock', 'true');
				sessionStorage.setItem('afterUnblockMessage', 'Friend unblocked successfully.');
				location.reload();
			}
		} catch (error) {
			console.error('Error:', error);
		}
	}
}
