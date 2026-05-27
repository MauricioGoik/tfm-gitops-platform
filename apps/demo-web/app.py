from flask import Flask, jsonify
import os

app = Flask(__name__)

@app.route("/")
def home():
    return """
    <html>
    <body style="font-family: sans-serif; text-align: center; padding: 50px; background: #0d1117; color: #e6edf3;">
        <h1>🚀 AI-Powered GitOps Platform</h1>
        <p>Pipeline GitOps + Security Scanning + AI Agent</p>
        <p style="color: #58a6ff;">TFM — Máster Multicloud & DevOps</p>
    </body>
    </html>
    """

@app.route("/health")
def health():
    return jsonify({"status": "healthy", "version": os.getenv("APP_VERSION", "1.0.0")})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
