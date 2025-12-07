"""Main Flask application for AI Voice Assistant."""
import os
import logging
from dotenv import load_dotenv
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO, emit

from services.voice_service import VoiceService
from services.ai_service import AIService
from services.chat_history import ChatHistory

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__, template_folder='../templates', static_folder='../static')
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key-here')

# Enable CORS
CORS(app)

# Initialize WebSocket
socketio = SocketIO(app, cors_allowed_origins="*")

# Initialize services
voice_service = VoiceService()
ai_service = AIService()
chat_history = ChatHistory()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@app.route('/')
def index():
    """Serve the main HTML page."""
    return render_template('index.html')


@app.route('/api/health')
def health_check():
    """Health check endpoint."""
    return jsonify({'status': 'healthy', 'service': 'AI Voice Assistant'})


@socketio.on('connect')
def handle_connect():
    """Handle client connection."""
    logger.info('Client connected')
    emit('connection_response', {'data': 'Connected to AI Voice Assistant'})


@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection."""
    logger.info('Client disconnected')


@socketio.on('audio_stream')
def handle_audio_stream(data):
    """Handle incoming audio stream from client."""
    try:
        # Transcribe audio
        text = voice_service.transcribe_audio(data['audio'])
        logger.info(f'Transcribed: {text}')
        
        # Get AI response
        ai_response = ai_service.get_response(text)
        chat_history.add_message(text, ai_response)
        
        # Convert response to speech
        audio_response = voice_service.text_to_speech(ai_response)
        
        # Send response back to client
        emit('response', {
            'text': ai_response,
            'audio': audio_response,
            'timestamp': chat_history.get_last_timestamp()
        })
        
    except Exception as e:
        logger.error(f'Error processing audio: {str(e)}')
        emit('error', {'message': str(e)})


@app.route('/api/chat', methods=['POST'])
def chat():
    """Handle text-based chat requests."""
    try:
        data = request.json
        user_message = data.get('message', '')
        
        if not user_message:
            return jsonify({'error': 'Message is required'}), 400
        
        # Get AI response
        ai_response = ai_service.get_response(user_message)
        chat_history.add_message(user_message, ai_response)
        
        return jsonify({
            'response': ai_response,
            'timestamp': chat_history.get_last_timestamp()
        })
        
    except Exception as e:
        logger.error(f'Error in chat: {str(e)}')
        return jsonify({'error': str(e)}), 500


@app.route('/api/chat-history')
def get_chat_history():
    """Get chat history."""
    return jsonify(chat_history.get_all_messages())


@app.route('/api/clear-history', methods=['POST'])
def clear_history():
    """Clear chat history."""
    chat_history.clear()
    return jsonify({'message': 'Chat history cleared'})


if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)
