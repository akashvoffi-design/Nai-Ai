from flask import Flask, render_template, request, jsonify
import google.generativeai as genai
import os
import logging
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Suppress unnecessary warnings
os.environ["GRPC_VERBOSITY"] = "ERROR"
os.environ["GLOG_minloglevel"] = "2"
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"

# Configure logging
logging.basicConfig(level=logging.INFO)

app = Flask(__name__)

# Get API Key from environment variable for security
API_KEY = os.getenv("GEMINI_API_KEY", "AIzaSyD_8uvEyVJPIKDAIT5RcHlmvz9EyhApnUo")

if not API_KEY:
    raise ValueError("No Gemini API key found. Please set GEMINI_API_KEY environment variable.")

genai.configure(api_key=API_KEY)

# Store chat sessions (in production, use a proper database)
chat_sessions = {}

def get_chat_session(session_id="default"):
    """Get or create a chat session for a user"""
    if session_id not in chat_sessions:
        model = genai.GenerativeModel("gemini-2.0-flash")
        chat_sessions[session_id] = model.start_chat(history=[])
    return chat_sessions[session_id]

@app.route('/')
def index():
    """Serve the main chat interface"""
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    """Handle chat messages"""
    try:
        data = request.get_json()
        user_message = data.get('message', '').strip()
        
        if not user_message:
            return jsonify({'error': 'Empty message'}), 400
        
        # Get chat session
        chat_session = get_chat_session()
        
        # Send message to Gemini AI
        response = chat_session.send_message(user_message)
        
        return jsonify({
            'response': response.text,
            'status': 'success'
        })
        
    except Exception as e:
        logging.error(f"Error in chat endpoint: {str(e)}")
        return jsonify({
            'error': 'Sorry, I encountered an error processing your message. Please try again.'
        }), 500

@app.route('/clear', methods=['POST'])
def clear_chat():
    """Clear the chat history"""
    try:
        # Clear the chat session by creating a new one
        model = genai.GenerativeModel("gemini-2.0-flash")
        chat_sessions['default'] = model.start_chat(history=[])
        
        return jsonify({'status': 'success'})
        
    except Exception as e:
        logging.error(f"Error clearing chat: {str(e)}")
        return jsonify({'error': 'Failed to clear chat'}), 500

if __name__ == '__main__':
    print("🤖 Starting AI Chat Server...")
    print("📍 Access your chat interface at: http://localhost:5000")
    print("⏹️  Press Ctrl+C to stop the server")
    app.run(debug=True, host='0.0.0.0', port=5000)