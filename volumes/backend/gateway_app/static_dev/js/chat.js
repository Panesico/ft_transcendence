document.addEventListener('DOMContentLoaded', function() {
	chatButton = document.getElementById('chatButton');
	chatButton.addEventListener('click', function() {
		request = new Request('/api/my_friends/', {
			method: 'GET',
			headers: {
				'X-CSRFToken': getCookie('csrftoken')
			},
			credentials: 'include'
		});
		fetch('/api/get_friends/')  // Asegúrate de que esta URL coincida con la URL de tu API
			.then(response => response.json())
			.then(data => {
				const contactSelect = document.getElementById('contactSelect');
				data.forEach(friend => {
					const option = document.createElement('option');
					option.value = friend.id;
					option.textContent = friend.name;
					contactSelect.appendChild(option);
				});
			})
			.catch(error => console.error('Error fetching friends:', error));
	});
});