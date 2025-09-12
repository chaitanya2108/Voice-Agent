from flask import Flask, render_template, request, jsonify, send_file
from io import BytesIO
from flask_cors import CORS
from chatbot_service import chatbot_service
from config import Config
import base64
import os
import pyttsx3
import io
import wave
import tempfile
from google import genai
from google.genai import types

# Create Flask application instance
app = Flask(__name__)

# Enable CORS for API endpoints
CORS(app)

# Configuration
app.config['SECRET_KEY'] = Config.SECRET_KEY

# Initialize TTS engine
print("Initializing TTS engine...")
tts_engine = pyttsx3.init()
# Set properties for better quality
tts_engine.setProperty('rate', 150)  # Speed of speech
tts_engine.setProperty('volume', 0.9)  # Volume level (0.0 to 1.0)
print("TTS engine initialized successfully!")

# Routes
@app.route('/')
def index():
    """Home page route"""
    return render_template('index.html')

@app.route('/api/hello')
def hello_api():
    """Simple API endpoint"""
    return jsonify({'message': 'Hello from Flask API!'})

@app.route('/api/echo', methods=['POST'])
def echo_api():
    """Echo API endpoint that returns the received data"""
    data = request.get_json()
    return jsonify({'echo': data, 'status': 'success'})

# Chat API endpoints
@app.route('/chat')
def chat_page():
    """Chat page route"""
    return render_template('chat.html')

@app.route('/api/chat', methods=['POST'])
def chat_api():
    """Chat API endpoint for sending messages to the AI"""
    try:
        data = request.get_json()
        message = data.get('message', '').strip()
        session_id = data.get('session_id', 'default')

        if not message:
            return jsonify({
                'response': 'Please enter a message.',
                'status': 'error'
            }), 400

        # Get response from chatbot service
        result = chatbot_service.get_response(message, session_id)

        return jsonify(result)

    except Exception as e:
        return jsonify({
            'response': 'Sorry, I encountered an error. Please try again.',
            'status': 'error',
            'error': str(e)
        }), 500

@app.route('/api/chat/starter', methods=['GET'])
def chat_starter():
    """Get a random conversation starter"""
    try:
        starter = chatbot_service.get_random_conversation_starter()
        return jsonify({
            'starter': starter,
            'status': 'success'
        })
    except Exception as e:
        return jsonify({
            'starter': 'Hey there! What would you like to chat about today? 😊',
            'status': 'error',
            'error': str(e)
        })

@app.route('/api/chat/clear', methods=['POST'])
def clear_chat():
    """Clear conversation history for a session"""
    try:
        data = request.get_json()
        session_id = data.get('session_id', 'default')

        success = chatbot_service.clear_conversation(session_id)

        return jsonify({
            'status': 'success' if success else 'error',
            'message': 'Conversation cleared' if success else 'Failed to clear conversation'
        })

    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500

@app.route('/api/chat/history', methods=['GET'])
def chat_history():
    """Get conversation history for a session"""
    try:
        session_id = request.args.get('session_id', 'default')
        history = chatbot_service.get_conversation_history(session_id)

        return jsonify({
            'history': history,
            'status': 'success'
        })

    except Exception as e:
        return jsonify({
            'history': [],
            'status': 'error',
            'error': str(e)
        }), 500

# Voice TTS endpoints
@app.route('/voice')
def voice_page():
    """Voice test page"""
    return render_template('voice.html')

@app.route('/gemini-tts')
def gemini_tts_page():
    """Google Gemini TTS test page"""
    return render_template('gemini_tts.html')

@app.route('/system-tts')
def system_tts_page():
    """System TTS test page"""
    return render_template('system_tts.html')

@app.route('/api/voice/tts', methods=['POST'])
def tts_api():
    """Generate TTS audio using pyttsx3"""
    try:
        data = request.get_json() or {}
        text = (data.get('text') or '').strip()
        voice_name = (data.get('voice_name') or 'default').strip()

        if not text:
            return jsonify({'status': 'error', 'error': 'Text is required'}), 400

        # Generate audio using pyttsx3
        # Create a temporary file to store the audio
        import tempfile
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
            temp_path = temp_file.name

        # Save audio to temporary file
        tts_engine.save_to_file(text, temp_path)
        tts_engine.runAndWait()

        # Read the generated audio file
        with open(temp_path, 'rb') as audio_file:
            audio_data = audio_file.read()

        # Clean up temporary file
        os.unlink(temp_path)

        # Create WAV file in memory
        wav_io = BytesIO(audio_data)
        wav_io.seek(0)

        return send_file(wav_io, mimetype='audio/wav', as_attachment=False, download_name='tts.wav')

    except Exception as e:
        return jsonify({'status': 'error', 'error': str(e)}), 500

@app.route('/api/gemini/tts', methods=['POST'])
def gemini_tts_api():
    """Generate TTS audio using Google Gemini TTS API"""
    try:
        data = request.get_json() or {}
        text = (data.get('text') or '').strip()
        speaker1_name = (data.get('speaker1_name') or 'Speaker1').strip()
        speaker1_voice = (data.get('speaker1_voice') or 'Kore').strip()
        speaker2_name = (data.get('speaker2_name') or 'Speaker2').strip()
        speaker2_voice = (data.get('speaker2_voice') or 'Puck').strip()

        if not text:
            return jsonify({'status': 'error', 'error': 'Text is required'}), 400

        # Check if API key is configured
        if not Config.GEMINI_API_KEY:
            return jsonify({'status': 'error', 'error': 'GEMINI_API_KEY is not configured'}), 500


        # Initialize Gemini client
        try:
            client = genai.Client(api_key=Config.GEMINI_API_KEY)
        except Exception as e:
            return jsonify({'status': 'error', 'error': f'Failed to initialize Gemini client: {e}'}), 500

        # Generate content with multi-speaker TTS
        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash-preview-tts",
                contents=text,
                config=types.GenerateContentConfig(
                    response_modalities=["AUDIO"],
                    speech_config=types.SpeechConfig(
                        multi_speaker_voice_config=types.MultiSpeakerVoiceConfig(
                            speaker_voice_configs=[
                                types.SpeakerVoiceConfig(
                                    speaker=speaker1_name,
                                    voice_config=types.VoiceConfig(
                                        prebuilt_voice_config=types.PrebuiltVoiceConfig(
                                            voice_name=speaker1_voice,
                                        )
                                    )
                                ),
                                types.SpeakerVoiceConfig(
                                    speaker=speaker2_name,
                                    voice_config=types.VoiceConfig(
                                        prebuilt_voice_config=types.PrebuiltVoiceConfig(
                                            voice_name=speaker2_voice,
                                        )
                                    )
                                ),
                            ]
                        )
                    )
                )
            )
        except Exception as e:
            return jsonify({'status': 'error', 'error': f'Gemini API request failed: {e}'}), 500

        # Extract audio data
        try:
            if not response:
                return jsonify({'status': 'error', 'error': 'No response from Gemini API'}), 500

            if not hasattr(response, 'candidates') or not response.candidates:
                return jsonify({'status': 'error', 'error': 'No candidates in Gemini response'}), 500

            candidate = response.candidates[0]
            if not hasattr(candidate, 'content') or not candidate.content:
                return jsonify({'status': 'error', 'error': 'No content in Gemini response candidate'}), 500

            content = candidate.content
            if not hasattr(content, 'parts') or not content.parts:
                return jsonify({'status': 'error', 'error': 'No parts in Gemini response content'}), 500

            part = content.parts[0]
            if not hasattr(part, 'inline_data') or not part.inline_data:
                return jsonify({'status': 'error', 'error': 'No inline data in Gemini response part'}), 500

            audio_data = part.inline_data.data
            if not audio_data:
                return jsonify({'status': 'error', 'error': 'No audio data in Gemini response'}), 500

        except Exception as e:
            return jsonify({'status': 'error', 'error': f'Invalid Gemini TTS response: {e}'}), 500

        # Convert raw PCM data to WAV format
        # The audio data is 16-bit PCM at 24kHz, we need to add WAV headers
        sample_rate = 24000
        sample_width = 2  # 16-bit = 2 bytes per sample
        channels = 1  # Mono

        # Create WAV file in memory
        wav_io = BytesIO()

        # Write WAV header
        wav_io.write(b'RIFF')
        wav_io.write((36 + len(audio_data)).to_bytes(4, 'little'))  # File size - 8
        wav_io.write(b'WAVE')
        wav_io.write(b'fmt ')
        wav_io.write((16).to_bytes(4, 'little'))  # fmt chunk size
        wav_io.write((1).to_bytes(2, 'little'))   # Audio format (PCM)
        wav_io.write(channels.to_bytes(2, 'little'))  # Number of channels
        wav_io.write(sample_rate.to_bytes(4, 'little'))  # Sample rate
        wav_io.write((sample_rate * channels * sample_width).to_bytes(4, 'little'))  # Byte rate
        wav_io.write((channels * sample_width).to_bytes(2, 'little'))  # Block align
        wav_io.write((sample_width * 8).to_bytes(2, 'little'))  # Bits per sample
        wav_io.write(b'data')
        wav_io.write(len(audio_data).to_bytes(4, 'little'))  # Data size
        wav_io.write(audio_data)  # Audio data

        wav_io.seek(0)
        return send_file(wav_io, mimetype='audio/wav', as_attachment=False, download_name='gemini_tts.wav')

    except Exception as e:
        return jsonify({'status': 'error', 'error': str(e)}), 500

@app.route('/api/system/tts', methods=['POST'])
def system_tts_api():
    """Generate TTS audio using system TTS (pyttsx3) with custom settings"""
    try:
        data = request.get_json() or {}
        text = (data.get('text') or '').strip()
        rate = data.get('rate', 150)
        volume = data.get('volume', 0.9)

        if not text:
            return jsonify({'status': 'error', 'error': 'Text is required'}), 400

        # Create a temporary file to store the audio
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
            temp_path = temp_file.name

        # Configure TTS engine with custom settings
        tts_engine.setProperty('rate', rate)
        tts_engine.setProperty('volume', volume)

        # Save audio to temporary file
        tts_engine.save_to_file(text, temp_path)
        tts_engine.runAndWait()

        # Read the generated audio file
        with open(temp_path, 'rb') as audio_file:
            audio_data = audio_file.read()

        # Clean up temporary file
        os.unlink(temp_path)

        # Create WAV file in memory
        wav_io = BytesIO(audio_data)
        wav_io.seek(0)

        return send_file(wav_io, mimetype='audio/wav', as_attachment=False, download_name='system_tts.wav')

    except Exception as e:
        return jsonify({'status': 'error', 'error': str(e)}), 500

@app.route('/api/chat/tts', methods=['POST'])
def chat_tts_api():
    """Generate TTS audio for chat responses using Gemini TTS"""
    try:
        data = request.get_json() or {}
        text = (data.get('text') or '').strip()
        voice_name = (data.get('voice_name') or 'Kore').strip()

        if not text:
            return jsonify({'status': 'error', 'error': 'Text is required'}), 400

        # Check if API key is configured
        if not Config.GEMINI_API_KEY:
            return jsonify({'status': 'error', 'error': 'GEMINI_API_KEY is not configured'}), 500

        # Initialize Gemini client
        try:
            client = genai.Client(api_key=Config.GEMINI_API_KEY)
        except Exception as e:
            return jsonify({'status': 'error', 'error': f'Failed to initialize Gemini client: {e}'}), 500

        # Generate content with single-speaker TTS
        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash-preview-tts",
                contents=text,
                config=types.GenerateContentConfig(
                    response_modalities=["AUDIO"],
                    speech_config=types.SpeechConfig(
                        voice_config=types.VoiceConfig(
                            prebuilt_voice_config=types.PrebuiltVoiceConfig(
                                voice_name=voice_name,
                            )
                        )
                    )
                )
            )
        except Exception as e:
            return jsonify({'status': 'error', 'error': f'Gemini API request failed: {e}'}), 500

        # Extract audio data
        try:
            if not response:
                return jsonify({'status': 'error', 'error': 'No response from Gemini API'}), 500

            if not hasattr(response, 'candidates') or not response.candidates:
                return jsonify({'status': 'error', 'error': 'No candidates in Gemini response'}), 500

            candidate = response.candidates[0]
            if not hasattr(candidate, 'content') or not candidate.content:
                return jsonify({'status': 'error', 'error': 'No content in Gemini response candidate'}), 500

            content = candidate.content
            if not hasattr(content, 'parts') or not content.parts:
                return jsonify({'status': 'error', 'error': 'No parts in Gemini response content'}), 500

            part = content.parts[0]
            if not hasattr(part, 'inline_data') or not part.inline_data:
                return jsonify({'status': 'error', 'error': 'No inline data in Gemini response part'}), 500

            audio_data = part.inline_data.data
            if not audio_data:
                return jsonify({'status': 'error', 'error': 'No audio data in Gemini response'}), 500

        except Exception as e:
            return jsonify({'status': 'error', 'error': f'Invalid Gemini TTS response: {e}'}), 500

        # Convert raw PCM data to WAV format
        sample_rate = 24000
        sample_width = 2  # 16-bit = 2 bytes per sample
        channels = 1  # Mono

        # Create WAV file in memory
        wav_io = BytesIO()

        # Write WAV header
        wav_io.write(b'RIFF')
        wav_io.write((36 + len(audio_data)).to_bytes(4, 'little'))  # File size - 8
        wav_io.write(b'WAVE')
        wav_io.write(b'fmt ')
        wav_io.write((16).to_bytes(4, 'little'))  # fmt chunk size
        wav_io.write((1).to_bytes(2, 'little'))   # Audio format (PCM)
        wav_io.write(channels.to_bytes(2, 'little'))  # Number of channels
        wav_io.write(sample_rate.to_bytes(4, 'little'))  # Sample rate
        wav_io.write((sample_rate * channels * sample_width).to_bytes(4, 'little'))  # Byte rate
        wav_io.write((channels * sample_width).to_bytes(2, 'little'))  # Block align
        wav_io.write((sample_width * 8).to_bytes(2, 'little'))  # Bits per sample
        wav_io.write(b'data')
        wav_io.write(len(audio_data).to_bytes(4, 'little'))  # Data size
        wav_io.write(audio_data)  # Audio data

        wav_io.seek(0)
        return send_file(wav_io, mimetype='audio/wav', as_attachment=False, download_name='chat_response.wav')

    except Exception as e:
        return jsonify({'status': 'error', 'error': str(e)}), 500

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('500.html'), 500

if __name__ == '__main__':
    # Run the application
    app.run(debug=True, host='0.0.0.0', port=5000)
