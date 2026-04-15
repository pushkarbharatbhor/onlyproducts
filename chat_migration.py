from db import run_query

# Create chat history table
try:
    run_query("""
        CREATE TABLE IF NOT EXISTS chat_history (
            id SERIAL PRIMARY KEY,
            user_id INT,
            query TEXT NOT NULL,
            response TEXT NOT NULL,
            relevant_products JSON,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    print("Chat history table created successfully.")
except Exception as e:
    print(f"Error creating chat_history table: {e}")

# Create chat sessions table for better organization
try:
    run_query("""
        CREATE TABLE IF NOT EXISTS chat_sessions (
            id SERIAL PRIMARY KEY,
            user_id INT,
            session_name VARCHAR(255),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    print("Chat sessions table created successfully.")
except Exception as e:
    print(f"Error creating chat_sessions table: {e}")
