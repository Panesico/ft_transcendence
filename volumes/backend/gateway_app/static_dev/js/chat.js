document.addEventListener('DOMContentLoaded', function() {
	let friendsData = [];
	chatButton = document.getElementById('chatButton');
	// Listen for the chat button click
	chatButton.addEventListener('click', function() {
		request = new Request('/getFriends/', {
			method: 'GET',
			headers: {
				'X-CSRFToken': getCookie('csrftoken')
			},
			credentials: 'include'
		});
		// Fetch the friends
		fetch(request)
			.then(response => response.json())
			.then(data => {
				const contactSelect = document.getElementById('contactSelect');
				console.log('data:', data);
				friendsData = data.friends;

				friendsData.forEach(friend => {
					const option = document.createElement('option');
					option.value = friend.user_id;
					option.textContent = friend.display_name;
					contactSelect.appendChild(option);
				});
			})
			.catch(error => console.error('Error fetching friends:', error));
		// Change avatar and display name
		contactSelect = document.getElementById('contactSelect');
		const contactAvatar = document.getElementById('contactAvatar');
		const contactDisplayName = document.getElementById('contactDisplayName');
		contactSelect.addEventListener('change', function() {
			const selectedOption = contactSelect.options[contactSelect.selectedIndex];
			const selectedFriend = friendsData.find(friend => friend.user_id == selectedOption.value);

			if (selectedFriend) {
				contactAvatar.src = selectedFriend.avatar;
				contactDisplayName.textContent = selectedFriend.display_name;
			}
		}
		);
	});
});