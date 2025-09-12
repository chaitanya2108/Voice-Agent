import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Configuration class for the Flask application"""

    # Flask configuration
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-here'

    # Gemini API configuration
    GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')

    # Chat configuration
    MAX_CONVERSATION_HISTORY = 10  # Number of previous messages to keep in context
    CHAT_MODEL_TEMPERATURE = 0.7   # Randomness in responses (0.0 to 1.0)

    @staticmethod
    def validate_config():
        """Validate that required configuration is present"""
        if not Config.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY is required but not found in environment variables")
        return True
