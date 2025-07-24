import sqlite3

# Create database with all required tables
conn = sqlite3.connect('chainlit.db')
cursor = conn.cursor()

# Create users table
cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    id TEXT PRIMARY KEY,
    identifier TEXT UNIQUE NOT NULL,
    createdAt TEXT NOT NULL,
    metadata TEXT
)
''')

# Create threads table
cursor.execute('''
CREATE TABLE IF NOT EXISTS threads (
    id TEXT PRIMARY KEY,
    createdAt TEXT NOT NULL
)
''')

# Create steps table
cursor.execute('''
CREATE TABLE IF NOT EXISTS steps (
    id TEXT PRIMARY KEY,
    threadId TEXT NOT NULL,
    parentId TEXT,
    createdAt TEXT NOT NULL,
    start TEXT,
    end TEXT,
    output TEXT,
    name TEXT,
    type TEXT,
    streaming BOOLEAN,
    isError BOOLEAN,
    waitForAnswer BOOLEAN,
    input TEXT,
    showInput TEXT,
    defaultOpen BOOLEAN,
    metadata TEXT,
    generation TEXT,
    FOREIGN KEY (threadId) REFERENCES threads (id)
)
''')

conn.commit()
conn.close()
print("Database created successfully with all required tables")