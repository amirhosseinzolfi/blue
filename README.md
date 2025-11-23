# AI Chatbot Platform 🤖

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![LangChain](https://img.shields.io/badge/LangChain-0.3+-green.svg)](https://github.com/langchain-ai/langchain)
[![LangGraph](https://img.shields.io/badge/LangGraph-0.5+-orange.svg)](https://github.com/langchain-ai/langgraph)

A comprehensive AI chatbot platform built with **LangGraph** and **LangChain**, featuring multiple frontend interfaces and advanced memory management.

## 📋 Table of Contents

- [Features](#-features)
- [Quick Start](#-quick-start)
- [Installation](#1-installation)
- [Configuration](#2-configuration)
- [Interface Details](#-interface-details)
- [Architecture](#-architecture)
- [Development](#-development)
- [Contributing](#-contributing)
- [License](#-license)

## 🌟 Features

### Core Features
- **🧠 Advanced AI Agent**: Powered by LangGraph with tool-calling capabilities
- **📚 Memory Management**: Intelligent conversation summarization and history management
- **🔧 Tool Integration**: Built-in tools for calculations, time queries, and memory search
- **💾 Persistent Storage**: SQLite-based conversation persistence
- **🔄 Session Management**: Multi-user session handling with unique session IDs

### Frontend Options
1. **🌐 Chainlit Interface**: Modern web UI with authentication and sidebar history
2. **📱 Telegram Bot**: Full-featured Telegram bot integration
3. **💻 Custom Web Interface**: Responsive HTML/CSS/JS interface
4. **🖥️ Terminal Interface**: Command-line interface for development
5. **🔌 REST API**: Standard API for custom integrations

### AI Capabilities
- Natural conversation with context awareness
- Mathematical calculations
- Current time and date queries
- Conversation history search
- Automatic conversation summarization
- Tool calling without OpenAI-specific dependencies

## 🚀 Quick Start

### 1. Installation

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/blue.git
cd blue

# Install dependencies and setup
python3 main.py install
```

### 2. Configuration

Copy the example environment file and configure it:

```bash
cp .env.example config/.env
```

Edit `config/.env` with your settings:

```env
# Telegram Bot Token (get from @BotFather)
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here

# LLM Configuration  
LLM_BASE_URL=http://your-llm-server:port/v1
LLM_MODEL_NAME=your-model-name
LLM_API_KEY=your_api_key_here
LLM_TEMPERATURE=0.5

# Ollama Embeddings
OLLAMA_EMBEDDING_MODEL=nomic-embed-text

# Ports
CHAINLIT_PORT=8000
API_PORT=8001
WEB_UI_PORT=8002
```

**⚠️ Important:** Never commit your `config/.env` file with real credentials!

### 3. Run Your Preferred Interface

```bash
# Chainlit Web Interface (Recommended)
python3 main.py chainlit

# Telegram Bot
python3 main.py telegram

# Custom Web Interface
python3 main.py web

# API Backend Only
python3 main.py api

# Terminal Interface
python3 main.py terminal
```

## 📋 Interface Details

### 🌐 Chainlit Interface

**Port**: 8000 (default)  
**URL**: http://localhost:8000

**Features**:
- Modern, responsive web interface
- Authentication support
- Sidebar with chat history
- Session information display
- Real-time conversation
- Message persistence

**Usage**:
```bash
python3 main.py chainlit
```

### 📱 Telegram Bot

**Token**: Configured in `.env`

**Features**:
- Full Telegram bot integration
- Command support (`/start`, `/help`, `/new`, `/history`, `/info`)
- Session management per user
- Persistent conversations
- Tool calling capabilities

**Commands**:
- `/start` - Start chatting
- `/help` - Show help
- `/new` - New session
- `/history` - Show chat history
- `/info` - Session information

**Usage**:
```bash
python3 main.py telegram
```

### 💻 Custom Web Interface

**Port**: 8002 (default)  
**URL**: http://localhost:8002

**Features**:
- Pure HTML/CSS/JS interface
- Responsive design
- Settings modal
- Chat history sidebar
- Connection status indicator
- Customizable API endpoint

**Usage**:
```bash
python3 main.py web
```

### 🔌 REST API

**Port**: 8001 (default)  
**Docs**: http://localhost:8001/docs

**Endpoints**:
- `POST /chat` - Send message
- `POST /session/create` - Create session
- `GET /session/{id}` - Get session info
- `GET /history/{id}` - Get chat history
- `GET /health` - Health check

**Usage**:
```bash
python3 main.py api
```

## 🔧 Architecture

### Backend Core (`backend/core.py`)
- **LangGraph Agent**: Enhanced version of provided sample
- **Tool Integration**: Calculator, time, memory search
- **Memory Management**: Conversation summarization
- **Session Handling**: Multi-user support
- **Database**: SQLite with LangGraph checkpointer

### API Layer (`backend/api/api.py`)
- **FastAPI Backend**: Standard REST API
- **CORS Support**: Cross-origin requests
- **Error Handling**: Comprehensive error responses
- **Documentation**: Auto-generated API docs

### Frontend Interfaces
- **Chainlit** (`frontend/chainlit/`): Advanced web UI
- **Telegram** (`frontend/telegram/`): Bot integration
- **Web** (`frontend/web/`): Custom HTML interface

## 🛠️ Configuration Options

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `LLM_BASE_URL` | LLM API endpoint | `http://141.98.210.15:15203/v1` |
| `LLM_MODEL_NAME` | Model name | `deep-seek-r1` |
| `LLM_API_KEY` | API key | `324` |
| `LLM_TEMPERATURE` | Temperature setting | `0.5` |
| `OLLAMA_EMBEDDING_MODEL` | Embedding model | `nomic-embed-text` |
| `TELEGRAM_BOT_TOKEN` | Telegram bot token | Required for Telegram |
| `MESSAGES_TO_KEEP_AFTER_SUMMARY` | Messages kept after summarization | `2` |
| `NEW_MESSAGES_THRESHOLD_FOR_SUMMARY` | Messages before summarization | `10` |

### Database Configuration
- **Type**: SQLite
- **Location**: `./data/chatbot_messages.sqlite`
- **Auto-created**: Yes

## 🔍 Available Tools

The AI agent has access to these built-in tools:

1. **🕐 Current Time**: Get current date and time
2. **🧮 Calculator**: Perform mathematical calculations
3. **🔍 Memory Search**: Search conversation history (placeholder)

### Adding Custom Tools

```python
from langchain_core.tools import tool

@tool
def your_custom_tool(input_param: str) -> str:
    """Description of your tool."""
    # Your tool logic here
    return "Tool result"

# Add to tools list in backend/core.py
tools.append(your_custom_tool)
```

## 📊 Memory Management

The system implements intelligent conversation management:

- **Automatic Summarization**: After 10 new messages (configurable)
- **Context Preservation**: Keeps last 2 messages + summary
- **Efficient Storage**: Removes old messages while preserving context
- **Search Capability**: Tool for searching conversation history

## 🔧 Development

### Running in Development Mode

```bash
# API with auto-reload
cd backend/api && python api.py

# Chainlit with reload
cd frontend/chainlit && chainlit run app.py --port 8000

# Telegram bot
cd frontend/telegram && python bot.py

# Web interface
cd frontend/web && python server.py
```

### Project Structure

```
chat/
├── main.py                 # Main entry point
├── config/
│   └── .env               # Configuration
├── backend/
│   ├── core.py            # LangGraph agent core
│   └── api/
│       └── api.py         # FastAPI backend
├── frontend/
│   ├── chainlit/
│   │   └── app.py         # Chainlit interface
│   ├── telegram/
│   │   └── bot.py         # Telegram bot
│   └── web/
│       ├── index.html     # Web interface
│       ├── style.css      # Styling
│       ├── script.js      # JavaScript
│       └── server.py      # Web server
└── data/                  # Database storage
```

## 🚨 Troubleshooting

### Common Issues

1. **Dependencies not installing**
   ```bash
   # Use virtual environment
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. **LLM connection issues**
   - Check `LLM_BASE_URL` in `.env`
   - Verify API key and model name
   - Test connection manually

3. **Telegram bot not responding**
   - Verify `TELEGRAM_BOT_TOKEN` in `.env`
   - Check bot permissions
   - Ensure bot is started with `/start`

4. **Web interface connection issues**
   - Ensure API backend is running on port 8001
   - Check CORS settings
   - Verify web interface settings

### Debug Mode

```bash
# Run with debug output
export PYTHONPATH=. && python -u main.py terminal
```

## 📝 API Documentation

### Send Message
```bash
curl -X POST "http://localhost:8001/chat" \
     -H "Content-Type: application/json" \
     -d '{"message": "Hello!", "session_id": "test-session"}'
```

### Create Session
```bash
curl -X POST "http://localhost:8001/session/create" \
     -H "Content-Type: application/json" \
     -d '{"system_prompt": "You are a helpful assistant"}'
```

### Get History
```bash
curl "http://localhost:8001/history/test-session"
```

## 🤝 Contributing

Contributions are welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🔒 Security

- Never commit `.env` files or credentials to the repository
- Use `.env.example` as a template
- Keep your API keys and tokens secure
- Review the `.gitignore` file to ensure sensitive files are excluded

## 🙏 Acknowledgments

- **LangGraph**: For the powerful agent framework
- **LangChain**: For LLM integration tools
- **Chainlit**: For the beautiful web interface
- **FastAPI**: For the robust API framework
- **python-telegram-bot**: For Telegram integration

---

**🎉 Happy Chatting!** 

For support or questions, please check the troubleshooting section or create an issue.
