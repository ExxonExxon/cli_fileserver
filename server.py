from flask import Flask, request, jsonify
import sqlite3
import os
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
# Ensure the path is correct
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE = os.path.join(BASE_DIR, "data.db")


def init_db():
    try:
        conn = sqlite3.connect(DATABASE)
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
            )
        """)

        conn.commit()
    finally:
        if conn:
            conn.close()


def get_db():
    return sqlite3.connect(DATABASE)


@app.route("/check_username", methods=["POST"])
def check_username():
    data = request.json
    username = data.get("username")

    if not username:
        return jsonify({"error": "No username provided to check"}), 400

    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute("SELECT 1 FROM users WHERE username = ?", (username,))

        exists = cur.fetchone() is not None

        return jsonify({"exists": exists}), 200

    except sqlite3.Error as e:
        print(f"Database error... {e}")
        return jsonify({"error": "Database error during check"}), 500

    finally:
        if conn:
            conn.close


@app.route("/check_email", methods=["POST"])
def check_email():
    data = request.json
    email = data.get("email")

    if not email:
        return jsonify({"error": "No email provided to check"}), 400

    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute("SELECT 1 FROM users WHERE email = ?", (email,))

        exists = cur.fetchone() is not None

        return jsonify({"exists": exists}), 200

    except sqlite3.Error as e:
        print(f"Database error... {e}")
        return jsonify({"error": "Database error during check"}), 500

    finally:
        if conn:
            conn.close


@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()

    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"error": "Missing username or password"}), 400

    try:
        conn = get_db()
        cur = conn.cursor()

        cur.execute(
            "SELECT password FROM users WHERE username = ?", (username,))

        user = cur.fetchone()

        if user:
            stored_password_hash = user[0]

            if check_password_hash(stored_password_hash, password):
                return jsonify({"message": "Successful Login"
                                }), 200
            else:
                return jsonify({"error": "Invalid username or password"}), 401
        else:
            return jsonify({"error": "Invalid username or password"}), 401

    except Exception as e:
        print(f"Login failed: {e}")
        return jsonify(
            {"error": "An unexpected error occurred during login"}
        ), 500

    finally:
        if conn:
            conn.close()


@app.route("/register", methods=["POST"])
def register():
    data = request.get_json()

    username = data.get("username")
    email = data.get("email")
    password = data.get("password")
    

    if not username or not password or not email:
        return jsonify({"error": "Missing username, password or email"}), 400

    hashed_password = generate_password_hash(password)

    try:
        conn = get_db()
        cur = conn.cursor()

        cur.execute("INSERT INTO users (username, password, email) VALUES (?, ?, ?)",
            (username, hashed_password, email))

        conn.commit()

        return jsonify({"message": "User registered successfully"}), 201

    except sqlite3.IntegrityError:
        return jsonify({"error": "(Integrity Error)"}), 409

    except Exception as e:
        print(f"Registration failed: {e}")

        return jsonify({"error": "An unexpected error occurred"}), 500

    finally:
        if conn:
            conn.close()


if __name__ == "__main__":
    init_db()
    app.run(debug=True)
