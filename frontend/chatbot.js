// Chatbot State
let conversationHistory = [];
let currentAssessmentId = null;

// DOM Elements
const chatToggle = document.getElementById('chat-toggle');
const chatPanel = document.getElementById('chat-panel');
const chatClose = document.getElementById('chat-close');
const chatMessages = document.getElementById('chat-messages');
const chatInputField = document.getElementById('chat-input-field');
const chatSendBtn = document.getElementById('chat-send');

// Toggle Chat Panel
chatToggle.addEventListener('click', () => {
    chatPanel.classList.remove('hidden');
    chatInputField.focus();

    // Show welcome message if first time
    if (conversationHistory.length === 0) {
        showWelcomeMessage();
    }
});

chatClose.addEventListener('click', () => {
    chatPanel.classList.add('hidden');
});

// Send Message
chatSendBtn.addEventListener('click', sendMessage);
chatInputField.addEventListener('keypress', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
    }
});

async function sendMessage() {
    const message = chatInputField.value.trim();
    if (!message) return;

    // Add user message to UI
    addMessage('user', message);
    conversationHistory.push({ role: 'user', content: message });

    // Clear input
    chatInputField.value = '';
    chatSendBtn.disabled = true;

    // Show typing indicator
    showTypingIndicator();

    try {
        // Call API
        const response = await fetch('/api/v1/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                message: message,
                assessment_id: currentAssessmentId,
                conversation_history: conversationHistory
            })
        });

        if (!response.ok) {
            throw new Error('Chat API failed');
        }

        const data = await response.json();

        // Remove typing indicator
        removeTypingIndicator();

        // Add AI response
        addMessage('ai', data.response);
        conversationHistory.push({ role: 'assistant', content: data.response });

    } catch (error) {
        removeTypingIndicator();
        addMessage('ai', "I'm having trouble connecting right now. Please try again in a moment.");
        console.error('Chat error:', error);
    } finally {
        chatSendBtn.disabled = false;
        chatInputField.focus();
    }
}

function addMessage(sender, text) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `chat-message ${sender}`;

    const avatar = document.createElement('div');
    avatar.className = 'chat-avatar';
    avatar.textContent = sender === 'user' ? '👤' : '🤖';

    const bubble = document.createElement('div');
    bubble.className = 'chat-bubble';
    bubble.textContent = text;

    messageDiv.appendChild(avatar);
    messageDiv.appendChild(bubble);
    chatMessages.appendChild(messageDiv);

    // Scroll to bottom
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function showTypingIndicator() {
    const typingDiv = document.createElement('div');
    typingDiv.className = 'typing-indicator chat-message ai';
    typingDiv.id = 'typing-indicator';

    const avatar = document.createElement('div');
    avatar.className = 'chat-avatar';
    avatar.textContent = '🤖';

    const bubble = document.createElement('div');
    bubble.className = 'chat-bubble';
    bubble.innerHTML = '<div class="typing-dot"></div><div class="typing-dot"></div><div class="typing-dot"></div>';

    typingDiv.appendChild(avatar);
    typingDiv.appendChild(bubble);
    chatMessages.appendChild(typingDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function removeTypingIndicator() {
    const indicator = document.getElementById('typing-indicator');
    if (indicator) {
        indicator.remove();
    }
}

function showWelcomeMessage() {
    const welcomeDiv = document.createElement('div');
    welcomeDiv.className = 'welcome-message';
    welcomeDiv.innerHTML = `
        <h4>👋 Welcome to VITALSCAN Health Assistant!</h4>
        <p>I can help explain your results, answer health questions, and provide personalized advice.</p>
        <p style="margin-top: 0.75rem; font-size: 0.85rem; color: var(--text-muted);">
            ⚠️ <strong>Disclaimer:</strong> I provide general guidance only, not medical diagnosis.
        </p>
    `;
    chatMessages.appendChild(welcomeDiv);
}

// Store assessment ID when results are displayed
function setAssessmentContext(assessmentId) {
    currentAssessmentId = assessmentId;
}

// Export for use in script.js
window.chatbot = {
    setAssessmentContext
};
