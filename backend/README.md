# Tanglish → Tamil Translator
### DTEC 2026 Hackathon — Team Project

Converts Tanglish (Tamil written in Roman script) into proper Tamil Unicode,
powered by Claude AI via a secure Flask backend.

---

## Project Structure

```
tanglish-backend/
├── app.py                  ← Flask backend (secure API gateway)
├── requirements.txt        ← Python dependencies
├── .env.example            ← Copy to .env and add your API key
├── .gitignore              ← Keeps .env out of GitHub
└── TanglishTranslator.jsx  ← React frontend (copy into your React project)
```

---

## Backend Setup (Flask)

### 1. Install Python dependencies

```bash
cd tanglish-backend
python -m venv venv

# Mac / Linux
source venv/bin/activate

# Windows
venv\Scripts\activate

pip install -r requirements.txt
```

### 2. Add your API key

```bash
cp .env.example .env
# Open .env and paste your Anthropic API key
```

Get your key at: https://console.anthropic.com

### 3. Run the Flask server

```bash
python app.py
# Server starts at http://localhost:5000
```

---

## Frontend Setup (React)

```bash
npx create-react-app tanglish-frontend
cd tanglish-frontend

# Copy TanglishTranslator.jsx into src/
cp ../tanglish-backend/TanglishTranslator.jsx src/

# Update src/App.js to use the component:
# import TanglishTranslator from './TanglishTranslator';
# export default function App() { return <TanglishTranslator />; }

npm start
# Frontend runs at http://localhost:3000
```

---

## API Endpoints

### `GET /health`
Check if the server is running.
```json
{ "status": "ok", "service": "tanglish-translator" }
```

### `POST /translate`
Translate a single Tanglish text.
```json
// Request
{ "text": "Vanakkam, eppadi irukkinga?" }

// Response
{ "tamil": "வணக்கம், எப்படி இருக்கீங்க?", "input_chars": 28, "output_chars": 26 }
```

### `POST /translate/batch`
Translate up to 10 texts at once (useful for teachers).
```json
// Request
{ "texts": ["Vanakkam", "Naan school ku porom"] }

// Response
{ "results": ["வணக்கம்", "நான் பள்ளிக்கு போறோம்"], "errors": [] }
```

---

## Features

- ✅ API key secured on server — never exposed to browser
- ✅ Rate limiting (30 requests/minute per IP)
- ✅ Input validation (max 2000 chars)
- ✅ Batch translation endpoint
- ✅ Full error handling with user-friendly messages
- ✅ Translation history in the UI
- ✅ CORS configured for local dev

---

## Production Deployment

Run with Gunicorn (more stable than Flask dev server):
```bash
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

Update the `CORS` origins in `app.py` with your actual domain before deploying.

---

## Team — DTEC 2026
Built for the DTEC 2026 Hackathon in partnership with Vaani – Tamil Spell Checker.
