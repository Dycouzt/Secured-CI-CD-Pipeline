# app/app.py - Fixed Bandit vulnerabilities.

import os
import sqlite3
from flask import Flask, request, jsonify

app = Flask(__name__)

# VULNERABILITY 1: Hardcoded Secret (for Gitleaks)
# This fake AWS key will be caught by Gitleaks in our CI pipeline.
AWS_ACCESS_KEY_ID = os.environ.get("AWS_ACCESS_KEY_ID", None)
AWS_SECRET_ACCESS_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY", None)

# In a real app, this should be loaded from a secrets manager or environment variable.
# For this demo, we use a non-sensitive placeholder.
app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY", "a-dev-secret-that-is-not-a-real-key")

# FIXED: SQL Injection vulnerability - Now using parameterized queries
@app.route('/users')
def get_user():
    """
    Retrieves a user from the database.
    NOW SECURE: Using parameterized queries to prevent SQL injection.
    """
    username = request.args.get('username')
    db_path = "/tmp/test.db"

    # Initialize a temporary database for demonstration
    if not os.path.exists(db_path):
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("CREATE TABLE users (id INTEGER PRIMARY KEY, username TEXT, email TEXT)")
        cursor.execute("INSERT INTO users (username, email) VALUES ('admin', 'admin@example.com')")
        conn.commit()
        conn.close()

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # FIXED: Using parameterized query instead of string formatting
    query = "SELECT username, email FROM users WHERE username = ?"
    try:
        cursor.execute(query, (username,))
        user = cursor.fetchone()
    except sqlite3.Error as e:
        return jsonify({"error": f"Database error: {e}"}), 500
    finally:
        conn.close()

    if user:
        return jsonify({"username": user[0], "email": user[1]})
    else:
        return jsonify({"error": "User not found"}), 404

@app.route('/health')
def health_check():
    """Health check endpoint."""
    return jsonify({"status": "ok"}), 200

if __name__ == '__main__':
    # FIXED: Debug mode disabled for production security
    # Debug mode is now controlled by environment variable
    debug_mode = os.environ.get("FLASK_DEBUG", "False").lower() == "true"
    app.run(host='0.0.0.0', port=5000, debug=debug_mode)