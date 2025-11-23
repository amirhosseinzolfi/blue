#!/bin/bash

# AI Chatbot Platform - Startup Script
# This script helps you start different components of the chatbot platform

echo "🤖 AI Chatbot Platform Startup Script"
echo "======================================"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Please run: python3 main.py install"
    exit 1
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Function to start API backend
start_api() {
    echo "🚀 Starting API backend on port 8001..."
    cd backend/api
    python api.py &
    API_PID=$!
    cd ../..
    echo "✅ API backend started (PID: $API_PID)"
}

# Function to start Chainlit
start_chainlit() {
    echo "🚀 Starting Chainlit interface on port 8000..."
    cd frontend/chainlit
    chainlit run app.py --port 8000 &
    CHAINLIT_PID=$!
    cd ../..
    echo "✅ Chainlit interface started (PID: $CHAINLIT_PID)"
}

# Function to start Telegram bot
start_telegram() {
    echo "🚀 Starting Telegram bot..."
    cd frontend/telegram
    python bot.py &
    TELEGRAM_PID=$!
    cd ../..
    echo "✅ Telegram bot started (PID: $TELEGRAM_PID)"
}

# Function to start Web interface
start_web() {
    echo "🚀 Starting Web interface on port 8002..."
    cd frontend/web
    python server.py &
    WEB_PID=$!
    cd ../..
    echo "✅ Web interface started (PID: $WEB_PID)"
}

# Function to stop all services
stop_all() {
    echo "🛑 Stopping all services..."
    
    if [ ! -z "$API_PID" ]; then
        kill $API_PID 2>/dev/null && echo "✅ API backend stopped"
    fi
    
    if [ ! -z "$CHAINLIT_PID" ]; then
        kill $CHAINLIT_PID 2>/dev/null && echo "✅ Chainlit interface stopped"
    fi
    
    if [ ! -z "$TELEGRAM_PID" ]; then
        kill $TELEGRAM_PID 2>/dev/null && echo "✅ Telegram bot stopped"
    fi
    
    if [ ! -z "$WEB_PID" ]; then
        kill $WEB_PID 2>/dev/null && echo "✅ Web interface stopped"
    fi
    
    # Kill any remaining processes
    pkill -f "chainlit run"
    pkill -f "uvicorn"
    pkill -f "python.*bot.py"
    
    echo "🏁 All services stopped"
}

# Trap SIGINT and SIGTERM to stop all services
trap stop_all SIGINT SIGTERM

# Parse command line arguments
case "${1:-all}" in
    "api")
        start_api
        echo "💡 API is running. Access API docs at: http://localhost:8001/docs"
        wait $API_PID
        ;;
    "chainlit")
        start_api
        sleep 2
        start_chainlit
        echo "💡 Chainlit is running. Access at: http://localhost:8000"
        wait $CHAINLIT_PID
        ;;
    "telegram")
        start_api
        sleep 2
        start_telegram
        echo "💡 Telegram bot is running. Message your bot to start chatting!"
        wait $TELEGRAM_PID
        ;;
    "web")
        start_api
        sleep 2
        start_web
        echo "💡 Web interface is running. Access at: http://localhost:8002"
        wait $WEB_PID
        ;;
    "all")
        echo "🚀 Starting all services..."
        start_api
        sleep 3
        start_chainlit
        sleep 2
        start_telegram
        sleep 2
        start_web
        
        echo ""
        echo "🎉 All services are running!"
        echo "📱 Access points:"
        echo "   • API Documentation: http://localhost:8001/docs"
        echo "   • Chainlit Interface: http://localhost:8000"
        echo "   • Web Interface: http://localhost:8002"
        echo "   • Telegram Bot: Message your configured bot"
        echo ""
        echo "⏹️  Press Ctrl+C to stop all services"
        
        # Wait for all processes
        wait
        ;;
    "stop")
        echo "🛑 Stopping any running services..."
        pkill -f "chainlit run"
        pkill -f "uvicorn"
        pkill -f "python.*bot.py"
        pkill -f "python.*api.py"
        echo "✅ Services stopped"
        ;;
    *)
        echo "Usage: $0 {api|chainlit|telegram|web|all|stop}"
        echo ""
        echo "Options:"
        echo "  api      - Start only the API backend"
        echo "  chainlit - Start API + Chainlit interface"
        echo "  telegram - Start API + Telegram bot"
        echo "  web      - Start API + Web interface"
        echo "  all      - Start all services (default)"
        echo "  stop     - Stop all running services"
        echo ""
        echo "Examples:"
        echo "  $0           # Start all services"
        echo "  $0 chainlit  # Start only Chainlit interface"
        echo "  $0 stop      # Stop all services"
        exit 1
        ;;
esac
