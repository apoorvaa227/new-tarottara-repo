document.getElementById('send-button').addEventListener('click', () => {
    const userMessage = document.getElementById('user-message').value.trim();
    if (userMessage) {
        const chatBox = document.querySelector('.chat-box');

        // Add user message
        const userMessageDiv = document.createElement('div');
        userMessageDiv.className = 'chat-message user';
        userMessageDiv.textContent = userMessage;
        chatBox.appendChild(userMessageDiv);

        // Simulate bot response
        const botMessageDiv = document.createElement('div');
        botMessageDiv.className = 'chat-message bot';
        botMessageDiv.textContent = "Thank you for your message! I'm processing your query.";
        chatBox.appendChild(botMessageDiv);

        // Clear input
        document.getElementById('user-message').value = '';

        // Scroll to the bottom
        chatBox.scrollTop = chatBox.scrollHeight;
    }
});
