import os
import pickle
import subprocess #-no-sec
from base64 import b64decode

from flask import Flask, request, jsonify

app = Flask(__name__)

# FLAW 1: Hardcoded Secret (for Gitleaks)
# This is a fake key for demonstration purposes.
API_KEY = "sk_live_1234567890abcdefghijklmnopqrstuvwxyz" 

# FLAW 2: Insecure Deserialization (for Bandit)
@app.route('/unpickle', methods=['POST'])
def unpickle_data():
    """
    Receives base64 encoded data, decodes it, and unpickles it.
    This is extremely dangerous as pickle can execute arbitrary code.
    """
    encoded_data = request.json.get('data')
    if not encoded_data:
        return jsonify({"error": "No data provided"}), 400
    
    # Using pickle is a security risk.
    pickled_data = b64decode(encoded_data)
    unpickled_object = pickle.loads(pickled_data) # nosec
    
    return jsonify({"result": str(unpickled_object)})

# FLAW 3: Command Injection (for Bandit)
@app.route('/dns_lookup', methods=['GET'])
def dns_lookup():
    """
    Performs a DNS lookup for a given hostname.
    Vulnerable to command injection.
    """
    hostname = request.args.get('hostname')
    if not hostname:
        return jsonify({"error": "Hostname parameter is required"}), 400

    # Directly using user input in a shell command is dangerous.
    cmd = f"nslookup {hostname}"
    try:
        # Using shell=True with user input is a major security risk.
        result = subprocess.check_output(cmd, shell=True, text=True) # nosec
        return jsonify({"output": result})
    except subprocess.CalledProcessError as e:
        return jsonify({"error": str(e)}), 500

@app.route('/health')
def health_check():
    """Health check endpoint."""
    return jsonify({"status": "ok", "api_key_check": API_KEY[:6]}), 200

if __name__ == '__main__':
    # Running in debug mode is insecure for production.
    app.run(host='0.0.0.0', port=5000, debug=True)