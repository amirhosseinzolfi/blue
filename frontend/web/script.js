// AI Chatbot Web Interface JavaScript

class ChatbotWebInterface {
    constructor() {
        this.apiUrl = 'http://localhost:8001';
        this.sessionId = null;
        this.isConnected = false;
        this.settings = {
            apiUrl: 'http://localhost:8001',
            systemPrompt: '',
            autoSave: true,
            showTimestamps: false
        };
        
        this.init();
    }
    
    init() {
        this.loadSettings();
        this.bindEvents();
        this.initializeSession();
        this.checkConnection();
    }
    
    loadSettings() {
        const saved = localStorage.getItem('chatbot-settings');
        if (saved) {
            this.settings = { ...this.settings, ...JSON.parse(saved) };
        }
        this.apiUrl = this.settings.apiUrl;
    }
    
    saveSettings() {
        localStorage.setItem('chatbot-settings', JSON.stringify(this.settings));
    }
    
    bindEvents() {
        // Message input
        const messageInput = document.getElementById('messageInput');
        const sendBtn = document.getElementById('sendBtn');
        
        messageInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });
        
        sendBtn.addEventListener('click', () => this.sendMessage());
        
        // Header controls
        document.getElementById('newSessionBtn').addEventListener('click', () => this.newSession());
        document.getElementById('settingsBtn').addEventListener('click', () => this.openSettings());
        
        // Sidebar toggle
        document.getElementById('toggleSidebar').addEventListener('click', () => this.toggleSidebar());
        
        // Clear chat
        document.getElementById('clearBtn').addEventListener('click', () => this.clearChat());
        
        // Settings modal
        document.getElementById('closeSettings').addEventListener('click', () => this.closeSettings());
        document.getElementById('saveSettings').addEventListener('click', () => this.saveSettingsModal());
        document.getElementById('resetSettings').addEventListener('click', () => this.resetSettings());
        
        // Modal backdrop click
        document.getElementById('settingsModal').addEventListener('click', (e) => {
            if (e.target.id === 'settingsModal') {
                this.closeSettings();
            }
        });
    }
    
    async checkConnection() {
        try {
            const response = await fetch(`${this.apiUrl}/health`);
            if (response.ok) {
                this.setConnectionStatus(true);
            } else {
                this.setConnectionStatus(false);
            }
        } catch (error) {
            this.setConnectionStatus(false);
        }
    }
    
    setConnectionStatus(connected) {
        this.isConnected = connected;
        const statusElement = document.getElementById('connectionStatus');
        
        if (connected) {
            statusElement.className = 'connection-status connected';
            statusElement.innerHTML = '<i class="fas fa-circle"></i><span>Connected</span>';
        } else {
            statusElement.className = 'connection-status disconnected';
            statusElement.innerHTML = '<i class="fas fa-circle"></i><span>Disconnected</span>';
        }
    }
    
    async initializeSession() {
        try {
            const response = await fetch(`${this.apiUrl}/session/create`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    system_prompt: this.settings.systemPrompt || undefined
                })
            });
            
            if (response.ok) {
                const data = await response.json();
                this.sessionId = data.session_id;
                this.updateSessionInfo();
                this.setConnectionStatus(true);
            } else {
                throw new Error('Failed to create session');
            }
        } catch (error) {
            console.error('Failed to initialize session:', error);
            this.setConnectionStatus(false);
        }
    }
    
    async newSession() {
        await this.initializeSession();
        this.clearChatMessages();
        this.addWelcomeMessage();
        this.updateChatHistory();
    }
    
    clearChatMessages() {
        const chatMessages = document.getElementById('chatMessages');
        chatMessages.innerHTML = '';
    }
    
    addWelcomeMessage() {
        const chatMessages = document.getElementById('chatMessages');
        const welcomeHTML = `
            <div class="welcome-message">
                <div class="message-avatar bot-avatar">
                    <i class="fas fa-robot"></i>
                </div>
                <div class="message-content">
                    <h2>Welcome to AI Chatbot! 🤖</h2>
                    <p>I'm your AI assistant powered by LangGraph with tool capabilities.</p>
                    <div class="capabilities">
                        <div class="capability">
                            <i class="fas fa-comments"></i>
                            <span>Natural conversations</span>
                        </div>
                        <div class="capability">
                            <i class="fas fa-calculator"></i>
                            <span>Mathematical calculations</span>
                        </div>
                        <div class="capability">
                            <i class="fas fa-clock"></i>
                            <span>Current time & date</span>
                        </div>
                        <div class="capability">
                            <i class="fas fa-search"></i>
                            <span>Conversation history search</span>
                        </div>
                    </div>
                    <p>How can I help you today?</p>
                </div>
            </div>
        `;
        chatMessages.innerHTML = welcomeHTML;
    }
    
    async sendMessage() {
        const messageInput = document.getElementById('messageInput');
        const message = messageInput.value.trim();
        
        if (!message || !this.sessionId) return;
        
        // Clear input
        messageInput.value = '';
        
        // Add user message to chat
        this.addMessageToChat(message, 'user');
        
        // Show typing indicator
        this.showTypingIndicator();
        
        try {
            const response = await fetch(`${this.apiUrl}/chat`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    message: message,
                    session_id: this.sessionId
                })
            });
            
            if (response.ok) {
                const data = await response.json();
                this.hideTypingIndicator();
                this.addMessageToChat(data.response, 'bot');
                this.updateChatHistory();
                this.updateSessionInfo();
            } else {
                throw new Error('Failed to send message');
            }
        } catch (error) {
            this.hideTypingIndicator();
            this.addMessageToChat('Sorry, I encountered an error. Please try again.', 'bot');
            console.error('Error sending message:', error);
        }
    }
    
    addMessageToChat(content, role) {
        const chatMessages = document.getElementById('chatMessages');
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${role}-message`;
        
        const timestamp = this.settings.showTimestamps ? 
            `<div class="message-timestamp">${new Date().toLocaleTimeString()}</div>` : '';
        
        const avatar = role === 'user' ? 
            '<i class="fas fa-user"></i>' : 
            '<i class="fas fa-robot"></i>';
        
        messageDiv.innerHTML = `
            <div class="message-avatar ${role}-avatar">
                ${avatar}
            </div>
            <div class="message-content">
                ${this.formatMessage(content)}
                ${timestamp}
            </div>
        `;
        
        chatMessages.appendChild(messageDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
    
    formatMessage(content) {
        // Simple formatting for code blocks, links, etc.
        content = content.replace(/```([\s\S]*?)```/g, '<pre><code>$1</code></pre>');
        content = content.replace(/`([^`]+)`/g, '<code>$1</code>');
        content = content.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
        content = content.replace(/\*(.*?)\*/g, '<em>$1</em>');
        content = content.replace(/\n/g, '<br>');
        
        return content;
    }
    
    showTypingIndicator() {
        document.getElementById('typingIndicator').style.display = 'block';
        const chatMessages = document.getElementById('chatMessages');
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
    
    hideTypingIndicator() {
        document.getElementById('typingIndicator').style.display = 'none';
    }
    
    async updateChatHistory() {
        if (!this.sessionId) return;
        
        try {
            const response = await fetch(`${this.apiUrl}/history/${this.sessionId}`);
            if (response.ok) {
                const data = await response.json();
                this.displayChatHistory(data.messages);
            }
        } catch (error) {
            console.error('Error fetching chat history:', error);
        }
    }
    
    displayChatHistory(messages) {
        const historyContainer = document.getElementById('chatHistory');
        
        if (!messages || messages.length === 0) {
            historyContainer.innerHTML = `
                <div class="history-placeholder">
                    <i class="fas fa-comment-dots"></i>
                    <p>No messages yet</p>
                </div>
            `;
            return;
        }
        
        const historyHTML = messages.slice(-10).map(msg => {
            const icon = msg.role === 'user' ? 'fas fa-user' : 'fas fa-robot';
            const preview = msg.content.length > 50 ? 
                msg.content.substring(0, 50) + '...' : 
                msg.content;
            
            return `
                <div class="history-item">
                    <div class="history-header">
                        <i class="${icon}"></i>
                        <span class="history-role">${msg.role}</span>
                    </div>
                    <div class="history-content">${preview}</div>
                </div>
            `;
        }).join('');
        
        historyContainer.innerHTML = historyHTML;
    }
    
    async updateSessionInfo() {
        if (!this.sessionId) return;
        
        try {
            const response = await fetch(`${this.apiUrl}/session/${this.sessionId}`);
            if (response.ok) {
                const data = await response.json();
                
                document.getElementById('sessionIdDisplay').textContent = 
                    data.session_id.substring(0, 20) + '...';
                document.getElementById('messageCount').textContent = 
                    data.messages_count || 0;
            }
        } catch (error) {
            console.error('Error fetching session info:', error);
        }
    }
    
    clearChat() {
        if (confirm('Are you sure you want to clear the chat? This will start a new session.')) {
            this.newSession();
        }
    }
    
    toggleSidebar() {
        const sidebar = document.getElementById('sidebar');
        sidebar.classList.toggle('open');
    }
    
    openSettings() {
        // Populate settings form
        document.getElementById('apiUrl').value = this.settings.apiUrl;
        document.getElementById('systemPrompt').value = this.settings.systemPrompt;
        document.getElementById('autoSave').checked = this.settings.autoSave;
        document.getElementById('showTimestamps').checked = this.settings.showTimestamps;
        
        document.getElementById('settingsModal').style.display = 'block';
    }
    
    closeSettings() {
        document.getElementById('settingsModal').style.display = 'none';
    }
    
    saveSettingsModal() {
        // Get values from form
        this.settings.apiUrl = document.getElementById('apiUrl').value;
        this.settings.systemPrompt = document.getElementById('systemPrompt').value;
        this.settings.autoSave = document.getElementById('autoSave').checked;
        this.settings.showTimestamps = document.getElementById('showTimestamps').checked;
        
        // Update API URL
        this.apiUrl = this.settings.apiUrl;
        
        // Save to localStorage
        this.saveSettings();
        
        // Close modal
        this.closeSettings();
        
        // Show success message
        this.addMessageToChat('Settings saved successfully!', 'bot');
        
        // Check new connection
        this.checkConnection();
    }
    
    resetSettings() {
        this.settings = {
            apiUrl: 'http://localhost:8001',
            systemPrompt: '',
            autoSave: true,
            showTimestamps: false
        };
        
        // Update form
        document.getElementById('apiUrl').value = this.settings.apiUrl;
        document.getElementById('systemPrompt').value = this.settings.systemPrompt;
        document.getElementById('autoSave').checked = this.settings.autoSave;
        document.getElementById('showTimestamps').checked = this.settings.showTimestamps;
    }
}

// Initialize the chatbot interface when the page loads
document.addEventListener('DOMContentLoaded', () => {
    window.chatbot = new ChatbotWebInterface();
});

// Keyboard shortcuts
document.addEventListener('keydown', (e) => {
    // Ctrl+Enter for new session
    if (e.ctrlKey && e.key === 'Enter') {
        window.chatbot.newSession();
    }
    
    // Escape to close modals
    if (e.key === 'Escape') {
        window.chatbot.closeSettings();
    }
});

// Handle page visibility change
document.addEventListener('visibilitychange', () => {
    if (!document.hidden && window.chatbot) {
        // Check connection when page becomes visible
        setTimeout(() => {
            window.chatbot.checkConnection();
        }, 1000);
    }
});
