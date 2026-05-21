"""
DTEC 2026 Hackathon — Tanglish to Tamil Translator
Flask Backend FINAL v2 — Google Input Tools + Groq AI pipeline
Step 1: Google Input Tools (letter-perfect transliteration)
Step 2: Groq AI (grammar + sentence flow fix)
"""

import os
import re
import time
import json
import logging
import urllib.request
import urllib.parse
from functools import wraps
from collections import defaultdict

from flask import Flask, request, jsonify
from flask_cors import CORS
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app, origins=["http://localhost:3000", "http://localhost:5173"])

client = Groq(api_key=os.environ["GROQ_API_KEY"])

# ── Rate limiter ───────────────────────────────────────────────────────────
RATE_LIMIT  = 30
RATE_WINDOW = 60
_rate_store: dict[str, list[float]] = defaultdict(list)

def is_rate_limited(ip: str) -> bool:
    now = time.time()
    calls = [t for t in _rate_store[ip] if t > now - RATE_WINDOW]
    _rate_store[ip] = calls
    if len(calls) >= RATE_LIMIT:
        return True
    _rate_store[ip].append(now)
    return False

def rate_limit(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        ip = request.headers.get("X-Forwarded-For", request.remote_addr)
        if is_rate_limited(ip):
            return jsonify({"error": "Too many requests. Please wait a moment."}), 429
        return f(*args, **kwargs)
    return wrapper

# ── Google Input Tools transliteration ────────────────────────────────────
def google_transliterate_word(word: str) -> str:
    """Transliterate a single Tanglish word to Tamil using Google Input Tools."""
    try:
        encoded = urllib.parse.quote(word)
        url = f"https://inputtools.google.com/request?text={encoded}&itc=ta-t-i0-und&num=1"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=5) as r:
            data = json.loads(r.read())
            if data[0] == "SUCCESS" and data[1]:
                return data[1][0][1][0]
    except Exception as e:
        logger.warning("Google transliterate failed for '%s': %s", word, e)
    return word  # Return original if failed

def google_transliterate_text(text: str) -> str:
    """
    Transliterate full Tanglish text word by word using Google Input Tools.
    Keeps English proper nouns and punctuation as-is.
    """
    # Split into words and punctuation
    tokens = re.findall(r"[\w']+|[.,!?;:\-\n]", text)
    result = []

    for token in tokens:
        # Skip punctuation
        if not token[0].isalpha():
            result.append(token)
            continue

        # Skip proper nouns (capitalized words like names, places)
        if token[0].isupper() and len(token) > 1:
            result.append(token)
            continue

        # Skip pure English words (common ones)
        english_words = {
            "school", "college", "office", "phone", "mobile", "internet",
            "facebook", "whatsapp", "youtube", "google", "app", "bus",
            "train", "car", "bike", "ok", "okay", "yes", "no", "hi",
            "hello", "bye", "thanks", "sorry", "please", "sir", "madam",
        }
        if token.lower() in english_words:
            result.append(token)
            continue

        # Transliterate using Google
        tamil = google_transliterate_word(token.lower())
        result.append(tamil)

    return " ".join(result)

# ── Groq AI grammar fixer ──────────────────────────────────────────────────
GRAMMAR_PROMPT = """You are a Tamil language expert specializing in casual spoken Tamil (பேச்சு தமிழ்).

You will receive text that is mostly Tamil Unicode with possibly some remaining Tanglish words.

YOUR JOB:
1. Fix any remaining untranslated Tanglish words to Tamil Unicode
2. Fix grammar to make it sound like NATURAL CASUAL SPOKEN Tamil
3. Fix spacing and punctuation
4. Keep English words (school, college, bus, etc.) as-is
5. Return ONLY the corrected Tamil text — no explanations

CRITICAL — Use casual Tamil NOT formal Tamil:
- இருக்கீங்க (NOT இருக்கிறீர்கள்)
- போறேன் (NOT போகிறேன்)
- வாரேன் (NOT வருகிறேன்)
- நல்லா (NOT நன்றாக)
- ரொம்ப (NOT மிகவும்)
- என்ன (NOT என்னை in casual context)

EXAMPLES:
Input: வணக்கம் எப்படி இருக்கீங்க
Output: வணக்கம், எப்படி இருக்கீங்க?

Input: நான் school போறேன் நாளைக்கு
Output: நான் நாளைக்கு school-க்கு போறேன்

Input: இன்னிக்கு வானிலை ரொம்ப சூடா இருக்கு
Output: இன்னிக்கு வானிலை ரொம்ப சூடா இருக்கு"""


def translate_pipeline(text: str) -> str:
    """Two-step pipeline: Google transliteration + Groq grammar fix."""

    # Step 1 — Google Input Tools (accurate word-level transliteration)
    step1 = google_transliterate_text(text)
    logger.info("After Google transliteration: %s → %s", text, step1)

    # Step 2 — Groq AI fixes grammar and sentence flow
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": GRAMMAR_PROMPT},
            {"role": "user",   "content": step1},
        ],
        max_tokens=1024,
        temperature=0.1,
    )
    result = response.choices[0].message.content.strip()
    logger.info("Final output: %s", result)
    return result


# ── Routes ─────────────────────────────────────────────────────────────────

@app.get("/health")
def health():
    return jsonify({
        "status": "ok",
        "service": "tanglish-translator",
        "pipeline": "Google Input Tools + Groq AI",
    })


@app.post("/translate")
@rate_limit
def translate():
    data = request.get_json(silent=True)
    if not data or "text" not in data:
        return jsonify({"error": "Request body must include a 'text' field."}), 400

    text = data["text"].strip()
    if not text:
        return jsonify({"error": "Text cannot be empty."}), 400
    if len(text) > 2000:
        return jsonify({"error": "Text too long. Maximum 2000 characters."}), 400

    try:
        logger.info("Translating: %s", text)
        result = translate_pipeline(text)
        return jsonify({
            "tamil":        result,
            "input_chars":  len(text),
            "output_chars": len(result),
        })
    except Exception as e:
        logger.exception("Error: %s", e)
        return jsonify({"error": "Translation failed. Please try again."}), 500


@app.post("/translate/batch")
@rate_limit
def translate_batch():
    data = request.get_json(silent=True)
    if not data or "texts" not in data:
        return jsonify({"error": "Request body must include a 'texts' array."}), 400

    texts = data["texts"]
    if not isinstance(texts, list) or len(texts) == 0:
        return jsonify({"error": "'texts' must be a non-empty array."}), 400
    if len(texts) > 10:
        return jsonify({"error": "Maximum 10 texts per batch."}), 400

    results, errors = [], []
    for i, text in enumerate(texts):
        text = str(text).strip()
        if not text:
            results.append("")
            continue
        try:
            results.append(translate_pipeline(text))
        except Exception as e:
            logger.error("Batch item %d failed: %s", i, e)
            errors.append(f"Item {i}: failed")
            results.append("")

    return jsonify({"results": results, "errors": errors})


if __name__ == "__main__":
    if not os.environ.get("GROQ_API_KEY"):
        raise RuntimeError("GROQ_API_KEY not set!")
    app.run(debug=True, port=8000, host="0.0.0.0")
