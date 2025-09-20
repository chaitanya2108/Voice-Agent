# Voice-Agent: Restaurant AI Assistant with TTS & POS Integration

An intelligent restaurant chatbot powered by Google Gemini AI, featuring text-to-speech capabilities and Clover POS integration for seamless order management and customer service.

## Features

### 🤖 AI-Powered Restaurant Assistant

- **Google Gemini Integration**: Advanced conversational AI for restaurant customer service
- **Restaurant-Specific Training**: Customized for menu assistance, order taking, and customer inquiries
- **Context-Aware Responses**: Maintains conversation history and restaurant context

### 🎤 Text-to-Speech (TTS) Capabilities

- **Google Gemini TTS**: High-quality voice synthesis with multiple speaker options
- **System TTS**: Fallback using pyttsx3 for local voice generation
- **Real-time Audio**: Instant voice playback for AI responses
- **Multi-Voice Support**: Choose from different voice personalities

### 💳 Clover POS Integration

- **OAuth 2.0 Authentication**: Secure connection to Clover POS systems
- **Order Management**: Direct integration with restaurant POS for order processing
- **Payment Processing**: Seamless payment handling through Clover
- **Merchant Information**: Access to restaurant data and menu items

### 🍽️ Restaurant Features

- **Menu Assistance**: Detailed information about dishes, ingredients, and allergens
- **Order Taking**: Natural language order processing
- **Customer Service**: Handle reservations, special requests, and inquiries
- **Multi-language Support**: Ready for international restaurant operations

### 🎨 Modern Web Interface

- **Responsive Design**: Bootstrap 5 powered UI that works on all devices
- **Real-time Chat**: Instant messaging interface with typing indicators
- **Voice Controls**: Toggle TTS on/off, select voice preferences
- **Status Indicators**: Visual feedback for POS connection and system status

## Project Structure

```
Voice-Agent/
├── app.py                    # Main Flask application with all routes
├── chatbot_service.py        # AI chatbot logic and restaurant context
├── clover_service.py         # Clover POS API integration service
├── config.py                 # Configuration management and environment variables
├── restaurant_data.py        # Restaurant menu and data definitions
├── requirements.txt          # Python dependencies
├── .env                      # Environment variables (create this)
├── .gitignore               # Git ignore rules
├── README.md                # This documentation
├── templates/               # HTML templates
│   ├── base.html            # Base template with navigation
│   ├── index.html           # Home page
│   ├── chat.html            # Main chatbot interface
│   ├── voice.html           # Voice testing page
│   ├── 404.html             # 404 error page
│   └── 500.html             # 500 error page
└── static/                  # Static files
    ├── css/
    │   └── style.css        # Custom styles and responsive design
    └── js/
        ├── main.js          # General JavaScript functionality
        ├── chat.js          # Chatbot interface logic
        └── voice.js         # Voice testing functionality
```

## Setup Instructions

### 1. Clone and Navigate to Project

```bash
git clone <your-repo-url>
cd Voice-Agent
```

### 2. Create Virtual Environment (Recommended)

```bash
python -m venv venv
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### 3. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 4. Environment Configuration

Create a `.env` file in the project root with the following variables:

```env
# Google Gemini API
GEMINI_API_KEY=your_gemini_api_key_here

# Clover POS API (for restaurant integration)
CLOVER_APP_ID=your_clover_app_id
CLOVER_APP_SECRET=your_clover_app_secret
```

**Getting API Keys:**

- **Gemini API**: Get your key from [Google AI Studio](https://makersuite.google.com/app/apikey)
- **Clover POS**: Register your app at [Clover Developer Portal](https://developer.clover.com/)

### 5. Run the Application

```bash
python app.py
```

The application will be available at: `http://localhost:5000`

### 6. Development Mode

The app runs in debug mode by default, which means:

- Auto-reload on code changes
- Detailed error messages
- Debug toolbar (if installed)

## Application Pages

### 🏠 Home Page (`/`)

- Project overview and navigation
- Quick access to all features
- System status indicators

### 💬 Chat Interface (`/chat`)

- Main restaurant chatbot interface
- Real-time conversation with AI
- Voice synthesis toggle and controls
- Clover POS connection status
- Order management capabilities

### 🎤 Voice Testing Pages

- **Gemini TTS** (`/gemini-tts`): Test Google Gemini text-to-speech with multiple voices
- **System TTS** (`/system-tts`): Test local system text-to-speech
- **Original Voice** (`/voice`): Legacy voice testing interface

## API Endpoints

### Chat & AI

- `POST /api/chat` - Send message to AI chatbot
- `GET /api/chat/starter` - Get random conversation starter
- `POST /api/chat/clear` - Clear chat history
- `GET /api/chat/history` - Get chat history
- `POST /api/chat/tts` - Generate TTS for chat responses

### Text-to-Speech

- `POST /api/gemini/tts` - Generate audio using Google Gemini TTS
- `POST /api/system/tts` - Generate audio using system TTS

### Clover POS Integration

- `GET /oauth` - Initiate Clover OAuth flow
- `GET /oauth/authorize` - OAuth authorization with merchant ID
- `GET /oauth/callback` - Handle OAuth callback
- `GET /api/clover/status` - Check POS connection status
- `POST /api/clover/disconnect` - Disconnect from Clover POS

### Utility

- `GET /api/hello` - Basic health check
- `POST /api/echo` - Echo test endpoint

## Usage Examples

### Restaurant Order Taking

```
Customer: "I'd like to order a large pepperoni pizza"
AI: "Great choice! A large pepperoni pizza is $18.99. Would you like any sides or drinks with that?"
```

### Menu Information

```
Customer: "What's in the Caesar salad?"
AI: "Our Caesar salad includes fresh romaine lettuce, parmesan cheese, croutons, and our house-made Caesar dressing. It's $12.99 and contains dairy and gluten."
```

### Voice Integration

- Toggle TTS on/off in the chat interface
- Choose from multiple voice personalities
- Real-time audio playback for all AI responses

### POS Integration

- Connect to Clover POS system via OAuth
- Process orders directly through the POS
- Handle payments and order management

## Customization

### Restaurant Data

Edit `restaurant_data.py` to customize:

- Menu items and prices
- Restaurant information
- Allergen information
- Order processing logic

### AI Personality

Modify `chatbot_service.py` to adjust:

- Response tone and style
- Restaurant-specific knowledge
- Order taking procedures
- Customer service protocols

### Voice Settings

Configure TTS options in:

- Voice selection dropdown
- Audio quality settings
- Playback controls

## Production Deployment

For production deployment:

1. **Environment Setup**:

   - Set `debug=False` in `app.py`
   - Use production environment variables
   - Configure secure HTTPS

2. **Server Configuration**:

   - Use a production WSGI server like Gunicorn
   - Set up reverse proxy with Nginx
   - Configure SSL certificates

3. **Database Integration**:

   - Add SQLAlchemy for persistent data
   - Store chat history and orders
   - Implement user management

4. **Security**:
   - Implement proper authentication
   - Secure API endpoints
   - Validate all inputs

## Troubleshooting

### Common Issues

**TTS Not Working**:

- Check Gemini API key configuration
- Verify internet connection
- Check browser audio permissions

**Clover POS Connection Failed**:

- Verify Clover app credentials
- Check OAuth redirect URLs
- Ensure merchant ID is correct

**Chat Not Responding**:

- Check Gemini API key
- Verify internet connection
- Check Flask application logs

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is open source and available under the MIT License.

## Support

For issues and questions:

- Check the troubleshooting section above
- Review the API documentation
- Open an issue on GitHub
