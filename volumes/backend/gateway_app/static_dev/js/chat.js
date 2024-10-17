function innit_listening() {
    let friendsData = [];
    const userID = document.getElementById('userID').value;
    console.log('chat.js userID:', userID);
    const chatButton = document.getElementById('chatButton');
    const contactAvatar = document.getElementById('contactAvatar');
    const contactDisplayName = document.getElementById('contactDisplayName');
    const messageInput = document.getElementById('messageInput');
    const sendButton = document.getElementById('sendButton');
    const unreadCount = document.getElementById('unreadChatsCount');

    // Listen for the chat button click
    chatButton.addEventListener('click', function() {
        const request = new Request('/getFriends/', {
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
                const contactList = document.getElementById('contactList');
                console.log('data:', data);
                friendsData = data.friends;

                // Clean the contact list
                contactList.innerHTML = '';

                friendsData.forEach(friend => {
                    const contactItem = document.createElement('a');
                    contactItem.href = '#';
                    contactItem.classList.add('list-group-item', 'list-group-item-action', 'bg-dark', 'text-white');
                    contactItem.dataset.contactId = friend.user_id;
                    contactItem.textContent = friend.display_name;
                    contactList.appendChild(contactItem);

                    // Listen to the click event on the contact item
                    contactItem.addEventListener('click', function(event) {
                        // Remove the 'selected-contact' class from all contacts
                        const contacts = contactList.getElementsByClassName('list-group-item');
                        for (let c of contacts) {
                            c.classList.remove('selected-contact');
                        }
                        // Add the 'selected-contact' class to the clicked contact
                        contactItem.classList.add('selected-contact');

                        // Update the avatar and display name
                        contactAvatar.src = friend.avatar;
                        contactDisplayName.textContent = friend.display_name;
                        
                        // Get all the messages between the user and the selected friend
                        const request = new Request(`/getMessages/${friend.user_id}/`, {
                            method: 'GET',
                            headers: {
                                'X-CSRFToken': getCookie('csrftoken')
                            },
                            credentials: 'include'
                        });
                    });
                });

                // Update unread messages count
            })
            .catch(error => console.error('Error fetching friends:', error));
    });

    // Send message
    sendButton.addEventListener('click', function() {
        const selectedContact = document.querySelector('.list-group-item.selected-contact');
        if (!selectedContact) {
            console.error('No contact selected');
            return;
        }

        const selectedFriend = friendsData.find(friend => friend.user_id == selectedContact.dataset.contactId);
        const message = messageInput.value;
        const receiverId = selectedFriend.user_id;
        const receiverDisplayName = selectedFriend.display_name;
        const receiverAvatar = selectedFriend.avatar;
        const data = {
            'type': 'chat',
            'subtype': 'chat_message',
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
}

function handleChatMessages(data)
{
    if (data.subtype === 'innit_listening') {
        innit_listening();
        console.log('chat listen init');
    }
    else if (data.subtype === 'chat_message')
        addRecvChatMessage(data);
    else if (data.subtype === 'unread_messages') {
        console.log('parseSocketMessage > data.subtype:', data.subtype);
        addUnreadMessages(data);
    }
}

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

function addUnreadMessages(data)
{
	const unreadChatsCount = document.getElementById('unreadChatscount');
	unreadChatsCount.textContent = data.unread_messages_count;
}