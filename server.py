from flask import Flask, request, jsonify
import sqlite3
import os
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
# Ensure the path is correct
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE = os.path.join(BASE_DIR, "users.db") 

def init_db():
    conn = None
    try:
        conn = sqlite3.connect(DATABASE)
        cur = conn.cursor()
        # Removed the 'email' column to match your latest structure
        cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
            )
        """)
        conn.commit()
    finally:
        if conn:
            conn.close()

def get_db():
    return sqlite3.connect(DATABASE)

# Endpoint to check if a username is already taken
@app.route("/check_username", methods=["POST"])
def check_username():
    # Use request.json for simplicity
    data = request.json 
    username = data.get("username")
    
    if not username:
        return jsonify({"error": "No username provided to check"}), 400
    
    conn = None
    try:
        conn = get_db()
        cur = conn.cursor()
        # CRITICAL FIX: Add trailing comma to make it a tuple (username,)
        cur.execute("SELECT 1 FROM users WHERE username = ?", (username,))
        
        exists = cur.fetchone() is not None
        
        # Return a proper JSON response to the client
        return jsonify({"exists": exists}), 200
        
    except sqlite3.Error as e:
        print(f"Database error... {e}")
        return jsonify({"error": "Database error during check"}), 500
    
    finally:
        if conn:
            conn.close()

@app.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    conn = None
    
    if not username or not password:
        return jsonify({"error": "Missing username or password"}), 400

    hashed_password = generate_password_hash(password)

    try:
        conn = get_db()
        cur = conn.cursor()
        
        cur.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_password))
        
        conn.commit()

        return jsonify({"message": "User registered successfully"}), 201
        
    except sqlite3.IntegrityError:
        # This handles the case if two clients try to register the same UNIQUE username concurrently
        return jsonify({"error": "Username already exists (Integrity Error)"}), 409
    
    except Exception as e:
        print(f"Registration failed: {e}")
        return jsonify({"error": "An unexpected error occurred"}), 500
        
    finally:
        if conn:
            conn.close()
    
if __name__ == "__main__":
    init_db()
    # It's better to use 0.0.0.0 if running in a container, but 127.0.0.1 is fine for local testing
    app.run(debug=True)