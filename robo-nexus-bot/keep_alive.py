"""
Keep Alive Server for Replit
Runs a simple Flask web server to keep the bot alive on Replit's free tier
"""
from flask import Flask
from threading import Thread
import logging

logger = logging.getLogger(__name__)

app = Flask('')

@app.route('/')
def home():
    """Health check endpoint"""
    return """
    <html>
        <head>
            <title>Robo Nexus Birthday Bot</title>
            <style>
                body { 
                    font-family: Arial, sans-serif; 
                    text-align: center; 
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    margin: 0;
                    padding: 50px;
                }
                .container {
                    background: rgba(255,255,255,0.1);
                    padding: 30px;
                    border-radius: 15px;
                    backdrop-filter: blur(10px);
                    max-width: 500px;
                    margin: 0 auto;
                }
                h1 { color: #FFD700; }
                .status { 
                    background: #28a745; 
                    padding: 10px 20px; 
                    border-radius: 25px; 
                    display: inline-block;
                    margin: 20px 0;
                }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🎂 Robo Nexus Birthday Bot</h1>
                <div class="status">✅ Bot is Online!</div>
                <p>🤖 The birthday bot is running and monitoring for celebrations!</p>
                <p>🎉 Ready to make every birthday special in Robo Nexus</p>
                <hr style="margin: 30px 0; border: 1px solid rgba(255,255,255,0.3);">
                <small>Keep-alive server for Replit hosting</small>
            </div>
        </body>
    </html>
    """

@app.route('/health')
def health():
    """Simple health check for monitoring services"""
    return {"status": "healthy", "bot": "robo-nexus-birthday-bot", "message": "Bot is running"}

@app.route('/ping')
def ping():
    """Simple ping endpoint"""
    return "pong"

def run():
    """Run the Flask server"""
    try:
        app.run(host='0.0.0.0', port=8080, debug=False, use_reloader=False)
    except Exception as e:
        logger.error(f"Keep-alive server error: {e}")

def keep_alive():
    """Start the keep-alive server in a separate thread"""
    try:
        t = Thread(target=run)
        t.daemon = True
        t.start()
        logger.info("Keep-alive server started on port 8080")
        print("🌐 Keep-alive server started - bot will stay awake on Replit!")
    except Exception as e:
        logger.error(f"Failed to start keep-alive server: {e}")
        print(f"⚠️ Keep-alive server failed to start: {e}")