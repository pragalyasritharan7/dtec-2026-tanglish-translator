# 🌐 Tanglish to Tamil AI Translator
> **DTEC 2026 Hackathon Team Project** | Developed in partnership with *Vaani Tamil Spell Checker*

An intelligent web platform that translates conversational Tanglish (Tamil phonetically typed in Roman script) into clean, standard Tamil Unicode script with OCR and Text-to-Speech support.

---

## ✨ Key Features
- 🔄 **Real-Time AI Transliteration:** Converts complex Tanglish sentences into accurate Tamil Unicode text via an LLM backend.
- 📸 **Handwritten & Image OCR:** Upload pictures of handwritten Tamil/Tanglish text and extract translated script automatically.
- 🔊 **Text-to-Speech (TTS):** Listen to the translated Tamil output directly from the interface.
- ⚡ **Batch Processing:** Handles multi-line or bulk educational text translation.
- 🛡️ **Secure Flask API Gateway:** Protects API keys server-side with CORS enforcement and IP rate limiting (30 requests/min).
- 🎨 **Responsive React UI:** Interactive translation history and one-click copy functionality.

---

## 🏗️ Project Architecture
```
dtec-2026-tanglish-translator/
├── backend/          # Flask REST API, LLM integration, OCR & TTS engines
│   ├── app_perfect.py
│   ├── requirements.txt
│   └── README.md
└── frontend/         # React SPA interface
    ├── src/
    │   └── TanglishTranslator_v5.jsx
    └── package.json
```

---

## 🚀 Quick Setup & Installation

### 1. Backend Service
```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate
# Linux / macOS
source venv/bin/activate

pip install -r requirements.txt
python app_perfect.py
```
*Backend runs on `http://localhost:5000`*

### 2. Frontend Application
```bash
cd frontend
npm install
npm start
```
*Frontend runs on `http://localhost:3000`*

---

## 📡 API Endpoints

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/health` | Server heartbeat check |
| `POST` | `/translate` | Translates a single Tanglish text string |
| `POST` | `/translate/batch` | Bulk translation for batch processing |

---

## 👥 Hackathon Team
Built with passion for the **DTEC 2026 Hackathon** in collaboration with **Vaani Tamil Spell Checker**.
