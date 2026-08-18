# Structured Format Prompting Comparison App

## Project Overview
This Flask web application demonstrates the power of **Structured Format Prompting** using the Google Gemini API. It allows users to input a simple, free-text prompt and visually compares the raw output with a structured, format-engineered output side-by-side. 

This project is built as a complete, polished college assignment demonstrating professional software engineering practices, authentication, and modern UI/UX design.

## Features
- **User Authentication**: Secure Sign Up and Login system using `Werkzeug` password hashing and Flask sessions.
- **SQLite Database**: Auto-initialized database for managing user accounts.
- **Side-by-Side Comparison**: Independently fetches responses for both a standard prompt and a dynamically augmented structured prompt.
- **Markdown Rendering**: Beautifully formats Gemini responses including tables, lists, and code blocks using Python's `markdown` library.
- **Modern UI**: A responsive, visually appealing interface featuring glassmorphism elements, soft shadows, smooth animations, and a structured layout.

## Technologies Used
- **Backend**: Python 3, Flask, SQLite3
- **Frontend**: HTML5, CSS3 (Vanilla), JavaScript (Vanilla)
- **AI Integration**: Google Gemini API (`google-generativeai`)
- **Other Libraries**: `python-dotenv`, `markdown`, `Werkzeug`

## Folder Structure
```text
StructuredPromptProject/
│
├── app.py                 # Main Flask application and route definitions
├── config.py              # Configuration loading and environment variables
├── database.py            # SQLite database initialization and helper functions
├── auth.py                # Authentication blueprint (Login/Signup routes)
├── gemini_helper.py       # Functions to interact with the Gemini API
├── requirements.txt       # Project dependencies
├── README.md              # Project documentation
├── .env.example           # Example environment variables file
│
├── instance/
│      app.db              # Automatically generated SQLite database
│
├── templates/
│      base.html           # Master HTML layout
│      landing.html        # Introduction and landing page
│      login.html          # User login page
│      signup.html         # User registration page
│      dashboard.html      # Main dashboard with prompt comparison UI
│
└── static/
       style.css           # Global stylesheets with modern UI properties
       script.js           # Frontend logic for API calls and loading states
```

## Installation and Setup

### 1. Create a Virtual Environment
```bash
python -m venv venv
```

### 2. Activate the Virtual Environment
- **Windows**:
  ```bash
  venv\Scripts\activate
  ```
- **macOS / Linux**:
  ```bash
  source venv/bin/activate
  ```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Copy `.env.example` to `.env` and fill in your keys.
```bash
cp .env.example .env
```
Update `.env`:
```env
GEMINI_API_KEY=your_actual_gemini_api_key_here
SECRET_KEY=your_secure_flask_secret_key
```

### 5. Run the Application
```bash
python app.py
```
The application will automatically initialize the database on startup. Open your browser and navigate to `http://127.0.0.1:5000`.

## Application Flow
1. **Landing Page**: Explains Structured Format Prompting.
2. **Registration**: Create a new user account (with validation).
3. **Login**: Access your account to reach the dashboard.
4. **Dashboard**: Enter any free-text prompt (e.g., "Explain Artificial Intelligence").
5. **Comparison**: Click "Compare". The backend creates a standard prompt and a structurally augmented prompt, sends both to Gemini, and displays the formatted responses side-by-side.
6. **Logout**: Safely end the session.

## Future Enhancements
- Save previous prompt comparisons in the database for users to revisit.
- Allow users to customize the structured format parameters via the UI.
- Support for exporting comparisons to PDF or Markdown files.
