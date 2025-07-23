import sqlite3
import json
from logger_config import setup_logger

logger = setup_logger(__name__)

def init_db():
    try:
        conn = sqlite3.connect('chat_history.db')
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS chat_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT UNIQUE,
                user_id TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS chat_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT,
                message TEXT,
                FOREIGN KEY (session_id) REFERENCES chat_sessions (session_id)
            )
        ''')
        conn.commit()
        conn.close()
        logger.info("Database initialized successfully.")
    except sqlite3.Error as e:
        logger.error(f"Database initialization error: {e}")

def save_chat_history(session_id, user_id, history):
    try:
        conn = sqlite3.connect('chat_history.db')
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM chat_sessions WHERE session_id = ?", (session_id,))
        if not cursor.fetchone():
            cursor.execute("INSERT INTO chat_sessions (session_id, user_id) VALUES (?, ?)", (session_id, user_id))

        cursor.execute("DELETE FROM chat_history WHERE session_id = ?", (session_id,))

        for message in history:
            cursor.execute("INSERT INTO chat_history (session_id, message) VALUES (?, ?)", (session_id, json.dumps(message)))

        conn.commit()
        conn.close()
        logger.info(f"Chat history saved for session {session_id}")
    except sqlite3.Error as e:
        logger.error(f"Error saving chat history for session {session_id}: {e}")

def get_chat_history(session_id):
    try:
        conn = sqlite3.connect('chat_history.db')
        cursor = conn.cursor()
        cursor.execute("SELECT message FROM chat_history WHERE session_id = ?", (session_id,))
        rows = cursor.fetchall()
        conn.close()

        if rows:
            logger.info(f"Chat history retrieved for session {session_id}")
            return [json.loads(row[0]) for row in rows]
        else:
            logger.info(f"No chat history found for session {session_id}")
            return []

    except sqlite3.Error as e:
        logger.error(f"Error retrieving chat history for session {session_id}: {e}")
        return []

def get_user_sessions(user_id):
    try:
        conn = sqlite3.connect('chat_history.db')
        cursor = conn.cursor()
        cursor.execute("SELECT session_id, created_at FROM chat_sessions WHERE user_id = ? ORDER BY created_at DESC", (user_id,))
        sessions = cursor.fetchall()
        conn.close()

        if sessions:
            logger.info(f"Retrieved {len(sessions)} sessions for user {user_id}")
            return sessions
        else:
            logger.info(f"No sessions found for user {user_id}")
            return []

    except sqlite3.Error as e:
        logger.error(f"Error retrieving sessions for user {user_id}: {e}")
        return []

def get_last_session_id(user_id):
    try:
        conn = sqlite3.connect('chat_history.db')
        cursor = conn.cursor()
        cursor.execute("SELECT session_id FROM chat_sessions WHERE user_id = ? ORDER BY created_at DESC LIMIT 1", (user_id,))
        session = cursor.fetchone()
        conn.close()

        if session:
            logger.info(f"Last session ID for user {user_id} is {session[0]}")
            return session[0]
        else:
            logger.info(f"No previous session found for user {user_id}")
            return None

    except sqlite3.Error as e:
        logger.error(f"Error retrieving last session ID for user {user_id}: {e}")
        return None
