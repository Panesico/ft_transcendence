async function blockFriend(event) {
	const blockSwitch = document.getElementById('blockSwitch');
	const userId = blockSwitch.getAttribute('data-user-id');
	const checked = blockSwitch.checked;
	console.log('userId:', userId);
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
                displayMessageInModal('Friend blocked successfully.');
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
				displayMessageInModal('Friend unblocked successfully.');
			}
		} catch (error) {
			console.error('Error:', error);
		}
	}
}
