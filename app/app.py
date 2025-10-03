# app/app.py
import os
import sqlite3
from flask import Flask, request, jsonify

app = Flask(__name__)

# VULNERABILITY 1: Hardcoded Secret (for Gitleaks)
# This fake AWS key will be caught by Gitleaks in our CI pipeline.
# FAKE_AWS_ACCESS_KEY_ID = "AKIAIOSFODNN7EXAMPLE" # This is a common example, let's make one up
FAKE_AWS_KEY = "AKIAJS33XPER4S7EXAMPLE" # This will be flagged by Gitleaks.

# In a real app, this should be loaded from a secrets manager or environment variable.
# For this demo, we use a non-sensitive placeholder.
app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY", "a-dev-secret-that-is-not-a-real-key")

# VULNERABILITY 2: SQL Injection (for Bandit).
# This function is intentionally vulnerable to SQL injection.
@app.route('/users')
def get_user():
    """
    Retrieves a user from the database.
    This is vulnerable to SQL Injection.
    Example of a malicious request: /users?username=' OR 1=1 --
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

    # This is the vulnerable line. Never format SQL queries with f-strings or string concatenation.
    # Use parameterized queries instead.
    query = f"SELECT username, email FROM users WHERE username = '{username}'"
    try:
        cursor.execute(query)
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
    # VULNERABILITY 3: Debug Mode Enabled (for Bandit)
    # Running in debug mode in production is a security risk.
    app.run(host='0.0.0.0', port=5000, debug=True)