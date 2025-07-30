// Retrieve user IDs from the hidden elements
const YOUR_USER_ID = document.getElementById('your-user-id').textContent;
const OTHER_USER_ID = document.getElementById('other-user-id').textContent;

async function fetchMessages() {
  const response = await fetch(`/api/messages/conversation?user_id=${OTHER_USER_ID}`);
  if (!response.ok) {
    alert('Failed to load messages');
    return;
  }
  const messages = await response.json();

  const messagesDiv = document.getElementById('messages');
  messagesDiv.innerHTML = ''; // Clear previous messages
  messages.forEach(msg => {
    const div = document.createElement('div');
    div.classList.add(msg.sender_id === YOUR_USER_ID ? 'message-sent' : 'message-received');
    div.textContent = (msg.sender_id === YOUR_USER_ID ? 'You' : 'Them') + ': ' + msg.content;
    messagesDiv.appendChild(div);
  });
  messagesDiv.scrollTop = messagesDiv.scrollHeight; // Auto scroll to bottom
}

async function sendMessage() {
  const input = document.getElementById('messageInput');
  const content = input.value.trim();
  if (!content) return alert('Please type a message.');

  const response = await fetch('/api/messages', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({receiver_id: OTHER_USER_ID, content})
  });
  if (!response.ok) {
    alert('Failed to send message');
    return;
  }
  input.value = '';
  fetchMessages(); // Refresh the messages after sending
}

document.getElementById('sendBtn').addEventListener('click', sendMessage);

// Load messages on page load and refresh every 5 seconds
fetchMessages();
setInterval(fetchMessages, 5000);
