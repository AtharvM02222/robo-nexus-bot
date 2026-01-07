"""
Keep Replit bot alive with a simple web server
This prevents Replit from sleeping the bot
"""
from flask import Flask
from threading import Thread
import logging

# Suppress Flask logs
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

app = Flask('')

@app.route('/')
def home():
    return """
    <html>
        <head><title>Robo Nexus Birthday Bot</title></head>
        <body style="font-family: Arial; text-align: center; padding: 50px;">
            <h1>🤖 Robo Nexus Birthday Bot</h1>
            <p>✅ Bot is running and healthy!</p>
            <p>🎂 Managing birthdays for the Robo Nexus community</p>
            <p>⏰ Daily birthday checks at 9:00 AM</p>
            <hr>
            <p><small>Hosted on Replit | Made for Robo Nexus Discord Server</small></p>
        </body>
    </html>
    """

@app.route('/health')
def health():
    return {"status": "healthy", "bot": "Robo Nexus Birthday Bot"}

def run():
    app.run(host='0.0.0.0', port=8080, debug=False)

def keep_alive():
    t = Thread(target=run)
    t.daemon = True
    t.start()
    print("🌐 Keep-alive server started on port 8080")