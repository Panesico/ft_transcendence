document.addEventListener('DOMContentLoaded', function() {
	let friendsData = [];
	const userID = document.getElementById('userID').value;
	console.log('chat.js userID:', userID);
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
				//Clean the select
				contactSelect.innerHTML = '';

				// Add default option
				const defaultOption = document.createElement('option');
				defaultOption.selected = true;
				defaultOption.textContent = gettext("Choose...");
				contactSelect.appendChild(defaultOption);

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
		// Send message
		messageInput = document.getElementById('messageInput');
		sendButton = document.getElementById('sendButton');
		sendButton.addEventListener('click', function() {
			const selectedOption = contactSelect.options[contactSelect.selectedIndex];
			const selectedFriend = friendsData.find(friend => friend.user_id == selectedOption.value);
			const message = messageInput.value;
			const receiverId = selectedFriend.user_id;
			const receiverDisplayName = selectedFriend.display_name;
			const receiverAvatar = selectedFriend.avatar;
			const data = {
				'type': 'chat_message',
				'sender_id': userID,
				'receiver_id': receiverId,
				'receiver_display_name': receiverDisplayName,
				'receiver_avatar': receiverAvatar,
				'message': message,
			};
			addSentChatMessage(message);
			sendMessagesBySocket(data, mainRoomSocket);
			console.log('data:', data);
			messageInput.value = '';
		});
	});
});

function addSentChatMessage(message)
{
	const chatMessages = document.getElementById('sendChatMessages');
	const messageElement = document.createElement('div');
	messageElement.innerHTML = `
		<p class="small p-2 me-3 mb-1 rounded-3 bg-dark text-white">
		${message}
		</p>
	`;
	chatMessages.appendChild(messageElement);
}

function addRecvChatMessage(data)
{
	const chatMessages = document.getElementById('recvChatMessages');
	const message = document.createElement('div');
	message.innerHTML = `
		 <p class="small p-2 ms-3 mb-1 rounded-3 bg-body-tertiary" style="color: black">
		 ${data.message}
		 </p>
	`;
	chatMessages.appendChild(message);
}