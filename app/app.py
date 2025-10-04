# app/app.py - Production-Ready Secure Version
import os
import sqlite3
import logging
from flask import Flask, request, jsonify
from werkzeug.exceptions import BadRequest

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Security best practice: Load secrets from environment variables
# In production, use AWS Secrets Manager, HashiCorp Vault, or similar
app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY")
if not app.config['SECRET_KEY']:
    logger.warning("SECRET_KEY not set. Using secure random key.")
    app.config['SECRET_KEY'] = os.urandom(32).hex()

# AWS credentials should be loaded from IAM roles or environment variables
AWS_ACCESS_KEY_ID = os.environ.get("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY")

# Database configuration
DB_PATH = os.environ.get("DATABASE_PATH", "/tmp/test.db")

def init_database():
    """Initialize the database with sample data if it doesn't exist."""
    if not os.path.exists(DB_PATH):
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    email TEXT NOT NULL
                )
            """)
            cursor.execute(
                "INSERT OR IGNORE INTO users (username, email) VALUES (?, ?)",
                ('admin', 'admin@example.com')
            )
            conn.commit()
            logger.info("Database initialized successfully")
        except sqlite3.Error as e:
            logger.error(f"Database initialization error: {e}")
        finally:
            conn.close()

# Initialize database on startup
init_database()

@app.route('/users')
def get_user():
    """
    Retrieves a user from the database.
    SECURE: Uses parameterized queries to prevent SQL injection.
    Implements input validation and error handling.
    """
    username = request.args.get('username')
    
    # Input validation
    if not username:
        logger.warning("Missing username parameter in request")
        raise BadRequest("Username parameter is required")
    
    if len(username) > 255:
        logger.warning(f"Username too long: {len(username)} characters")
        raise BadRequest("Username exceeds maximum length")
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Secure parameterized query
        query = "SELECT username, email FROM users WHERE username = ?"
        cursor.execute(query, (username,))
        user = cursor.fetchone()
        
        if user:
            logger.info(f"User found: {username}")
            return jsonify({
                "username": user[0],
                "email": user[1]
            }), 200
        else:
            logger.info(f"User not found: {username}")
            return jsonify({"error": "User not found"}), 404
            
    except sqlite3.Error as e:
        logger.error(f"Database error: {e}")
        return jsonify({"error": "Internal server error"}), 500
    finally:
        if conn:
            conn.close()

@app.route('/health')
def health_check():
    """Health check endpoint for monitoring and load balancers."""
    return jsonify({
        "status": "healthy",
        "service": "secure-cicd-pipeline"
    }), 200

@app.errorhandler(400)
def bad_request(e):
    """Handle bad request errors."""
    return jsonify({"error": str(e)}), 400

@app.errorhandler(404)
def not_found(e):
    """Handle not found errors."""
    return jsonify({"error": "Resource not found"}), 404

@app.errorhandler(500)
def internal_error(e):
    """Handle internal server errors."""
    logger.error(f"Internal error: {e}")
    return jsonify({"error": "Internal server error"}), 500

if __name__ == '__main__':
    # Security: Debug mode strictly disabled in production
    # Only enable in development via environment variable
    debug_mode = os.environ.get("FLASK_DEBUG", "False").lower() == "true"
    
    if debug_mode:
        logger.warning("Running in DEBUG mode - NOT suitable for production!")
    
    # In production, use Gunicorn or uWSGI instead of Flask's built-in server
    # Example: gunicorn --bind 0.0.0.0:5000 --workers 4 app:app
    app.run(
        host='0.0.0.0',
        port=int(os.environ.get("PORT", 5000)),
        debug=debug_mode
    )