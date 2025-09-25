#!/usr/bin/env python3
"""
Simple Campfire Chatbot Example

This bot listens for webhook messages from Campfire and responds with:
- Echo messages that start with "echo:"
- Current time when asked "what time is it?"
- A joke when someone says "tell me a joke"
- Weather info when asked about weather (mock response)
"""

from flask import Flask, request, jsonify
import requests
import json
from datetime import datetime
import random

app = Flask(__name__)

# Configuration - Update these with your bot's credentials
CAMPFIRE_BOT_ENDPOINTS = {
    # Format: room_id: "http://your-campfire-host/rooms/{room_id}/{bot_key}/messages"
    # You'll get these URLs when you create the bot in Campfire
    1: "http://127.0.0.1:3000/rooms/1/2-g0I52PHuASac/messages",  # Replace with your actual endpoint
    2: "http://127.0.0.1:3000/rooms/2/2-g0I52PHuASac/messages",  # Add more rooms as needed
}

# Jokes for the bot to tell
JOKES = [
    "Why don't scientists trust atoms? Because they make up everything!",
    "I told my wife she was drawing her eyebrows too high. She looked surprised.",
    "Why don't eggs tell jokes? They'd crack each other up!",
    "I'm reading a book about anti-gravity. It's impossible to put down!",
]

def send_message_to_campfire(room_id, message):
    """Send a text message back to Campfire"""
    if room_id not in CAMPFIRE_BOT_ENDPOINTS:
        print(f"Unknown room ID: {room_id}")
        return False

    endpoint = CAMPFIRE_BOT_ENDPOINTS[room_id]

    try:
        response = requests.post(
            endpoint,
            data=message.encode('utf-8'),
            headers={'Content-Type': 'text/plain'},
            timeout=10
        )
        print(f"Sent to Campfire: {response.status_code}")
        return response.status_code == 201
    except requests.RequestException as e:
        print(f"Error sending to Campfire: {e}")
        return False

def process_message(webhook_data):
    """Process incoming message and generate response"""
    user = webhook_data['user']
    room = webhook_data['room']
    message = webhook_data['message']

    user_name = user['name']
    room_id = room['id']
    room_name = room['name']
    message_text = message['body']['plain'].strip().lower()

    print(f"Message from {user_name} in {room_name}: {message_text}")

    # Don't respond to empty messages
    if not message_text:
        return None

    # Echo command
    if message_text.startswith('echo:'):
        echo_text = message['body']['plain'][5:].strip()
        return f"🔊 {echo_text}"

    # Time command
    elif 'what time is it' in message_text or 'time?' in message_text:
        current_time = datetime.now().strftime("%I:%M %p on %B %d, %Y")
        return f"⏰ It's currently {current_time}"

    # Joke command
    elif 'tell me a joke' in message_text or 'joke' in message_text:
        joke = random.choice(JOKES)
        return f"😄 {joke}"

    # Weather command (mock)
    elif 'weather' in message_text:
        return f"🌤️ It's always sunny in the server room! (This is a mock weather response)"

    # Help command
    elif message_text in ['help', 'commands', 'what can you do']:
        return """🤖 **Bot Commands:**
• `echo: <text>` - I'll repeat what you say
• `what time is it?` - Current time
• `tell me a joke` - Random joke
• `weather` - Mock weather info
• `help` - This message"""

    # Greeting
    elif any(greeting in message_text for greeting in ['hello', 'hi', 'hey']):
        return f"👋 Hello {user_name}! Type 'help' to see what I can do."

    # Default response for unrecognized messages
    else:
        return None  # Don't respond to everything

@app.route('/webhook', methods=['POST'])
def webhook():
    """Webhook endpoint that receives messages from Campfire"""
    try:
        # Parse the JSON payload from Campfire
        webhook_data = request.get_json()

        if not webhook_data:
            return "No data received", 400

        # Process the message and get a response
        response_message = process_message(webhook_data)

        # Send response back to Campfire if we have one
        if response_message:
            room_id = webhook_data['room']['id']
            success = send_message_to_campfire(room_id, response_message)

            if success:
                return "Message sent", 200
            else:
                return "Failed to send message", 500
        else:
            return "No response generated", 200

    except Exception as e:
        print(f"Error processing webhook: {e}")
        return f"Error: {str(e)}", 500

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "bot": "Campfire Example Bot"
    })

if __name__ == '__main__':
    print("🤖 Starting Campfire Bot...")
    print("📡 Webhook URL: http://localhost:5000/webhook")
    print("🏥 Health check: http://localhost:5000/health")
    print("\nConfigured room endpoints:")
    for room_id, endpoint in CAMPFIRE_BOT_ENDPOINTS.items():
        print(f"  Room {room_id}: {endpoint}")

    # Run the Flask app
    app.run(host='0.0.0.0', port=5000, debug=True)