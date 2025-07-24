import React, { useState } from 'react';
import './Chatbot.css';

const Chatbot = () => {
    const [messages, setMessages] = useState([]);
    const [userMessage, setUserMessage] = useState('');

    const handleSendMessage = () => {
        if (userMessage.trim()) {
            const newMessages = [
                ...messages,
                { sender: 'user', text: userMessage },
                { sender: 'bot', text: "Thank you for your message! I'm processing your query." }
            ];
            setMessages(newMessages);
            setUserMessage('');
        }
    };

    return (
        <div className="chatbot-container">
            <header className="chatbot-header">
                <h1>Tarotoo Psychic Chat</h1>
            </header>
            <div className="chatbox">
                {messages.map((message, index) => (
                    <div
                        key={index}
                        className={`chat-message ${message.sender}`}
                    >
                        {message.text}
                    </div>
                ))}
            </div>
            <div className="chat-input">
                <input
                    type="text"
                    placeholder="Type your message..."
                    value={userMessage}
                    onChange={(e) => setUserMessage(e.target.value)}
                />
                <button onClick={handleSendMessage}>Send</button>
            </div>
        </div>
    );
};

export default Chatbot;
