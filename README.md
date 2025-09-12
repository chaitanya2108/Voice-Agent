# Flask Voice-Agent Project

A basic Flask application setup with modern web interface and API endpoints.

## Features

- ✅ Flask web framework
- ✅ Bootstrap 5 for responsive UI
- ✅ Template inheritance with Jinja2
- ✅ RESTful API endpoints
- ✅ Error handling (404, 500)
- ✅ Static file serving (CSS, JS)
- ✅ Modern, clean interface

## Project Structure

```
Voice-Agent/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── README.md             # This file
├── templates/            # HTML templates
│   ├── base.html         # Base template
│   ├── index.html        # Home page
│   ├── 404.html          # 404 error page
│   └── 500.html          # 500 error page
└── static/               # Static files
    ├── css/
    │   └── style.css     # Custom styles
    └── js/
        └── main.js       # JavaScript functionality
```

## Setup Instructions

### 1. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 2. Run the Application

```bash
python app.py
```

The application will be available at: `http://localhost:5000`

### 3. Development Mode

The app runs in debug mode by default, which means:

- Auto-reload on code changes
- Detailed error messages
- Debug toolbar (if installed)

## API Endpoints

### GET /api/hello

Returns a simple hello message.

**Response:**

```json
{
  "message": "Hello from Flask API!"
}
```

### POST /api/echo

Echoes back the JSON data sent in the request.

**Request Body:**

```json
{
  "message": "Hello World",
  "data": "any data"
}
```

**Response:**

```json
{
  "echo": {
    "message": "Hello World",
    "data": "any data"
  },
  "status": "success"
}
```

## Customization

### Adding New Routes

Add new routes in `app.py`:

```python
@app.route('/your-route')
def your_function():
    return render_template('your_template.html')
```

### Adding New Templates

Create new HTML files in the `templates/` directory and extend `base.html`:

```html
{% extends "base.html" %} {% block title %}Your Page Title{% endblock %} {%
block content %}
<!-- Your content here -->
{% endblock %}
```

### Adding Static Files

Place CSS files in `static/css/` and JavaScript files in `static/js/`.

## Production Deployment

For production deployment:

1. Set `debug=False` in `app.py`
2. Use a production WSGI server like Gunicorn
3. Set up proper environment variables for configuration
4. Use a reverse proxy like Nginx

## Next Steps

This is a basic Flask setup. You can extend it by adding:

- Database integration (SQLAlchemy)
- User authentication
- More complex API endpoints
- WebSocket support
- Voice processing capabilities (for your voice-agent project)

## License

This project is open source and available under the MIT License.
