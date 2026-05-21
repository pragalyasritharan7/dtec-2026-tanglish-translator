"""
DTEC 2026 Hackathon — Tanglish to Tamil Translator
Flask Backend — Secure API Gateway
"""

import os
import time
import logging
from functools import wraps
from collections import defaultdict

from flask import Flask, request, jsonify
from flask_cors import CORS
import anthropic
from dotenv import load_dotenv

load_dotenv()

# ── Logging ────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)

# ── App setup ──────────────────────────────────────────────────────────────
app = Flask(__name__)

# Allow requests from your React dev server and production domain
CORS(app, origins=[
    "http://localhost:3000",
    "http://localhost:5173",
    "https://your-production-domain.com",   # update before deploying
])

# ── Anthropic client ───────────────────────────────────────────────────────
client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

# ── Simple in-memory rate limiter ──────────────────────────────────────────
# 30 requests per IP per minute
RATE_LIMIT = 30
RATE_WINDOW = 60   # seconds

_rate_store: dict[str, list[float]] = defaultdict(list)

def is_rate_limited(ip: str) -> bool:
    now = time.time()
    window_start = now - RATE_WINDOW
    calls = [t for t in _rate_store[ip] if t > window_start]
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

# ── System prompt ──────────────────────────────────────────────────────────
SYSTEM_PROMPT = """You are an expert Tamil linguist and translator specialising in Tanglish — Tamil words written using Roman/English script.

Your task: Convert Tanglish text into proper Tamil Unicode script.

Rules:
1. Output ONLY the Tamil Unicode translation — no English, no explanations, no markdown.
2. Preserve the original meaning, tone, and register (formal vs casual).
3. If a word is a proper noun (name, brand, place) keep it in English or transliterate naturally.
4. Handle common Tanglish spelling variations:
   - zh / l / r confusion  (e.g. "Tamil" vs "Thamizh")
   - aa / a vowel length    (e.g. "paaru" → பாரு)
   - Double consonants      (e.g. "romba" → ரொம்ப)
5. Produce natural, fluent Tamil — not word-for-word transliteration.
6. If the input contains mixed Tanglish and English, translate only the Tanglish parts and keep English words as-is.
"""

# ── Routes ─────────────────────────────────────────────────────────────────

@app.get("/health")
def health():
    """Simple health check — useful for deployment monitors."""
    return jsonify({"status": "ok", "service": "tanglish-translator"})


@app.post("/translate")
@rate_limit
def translate():
    """
    POST /translate
    Body: { "text": "Vanakkam, eppadi irukkinga?" }
    Returns: { "tamil": "வணக்கம், எப்படி இருக்கீங்க?" }
    """
    data = request.get_json(silent=True)

    # ── Validate input ──
    if not data or "text" not in data:
        return jsonify({"error": "Request body must include a 'text' field."}), 400

    text = data["text"].strip()

    if not text:
        return jsonify({"error": "Text cannot be empty."}), 400

    if len(text) > 2000:
        return jsonify({"error": "Text too long. Maximum 2000 characters."}), 400

    # ── Call Claude ──
    try:
        logger.info("Translating %d chars from IP %s",
                    len(text),
                    request.headers.get("X-Forwarded-For", request.remote_addr))

        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1024,
            system=SYSTEM_PROMPT,
            messages=[
                {"role": "user", "content": f"Translate this Tanglish to Tamil Unicode:\n\n{text}"}
            ],
        )

        tamil_output = message.content[0].text.strip()

        logger.info("Translation complete — %d chars output", len(tamil_output))

        return jsonify({
            "tamil": tamil_output,
            "input_chars": len(text),
            "output_chars": len(tamil_output),
        })

    except anthropic.AuthenticationError:
        logger.error("Invalid Anthropic API key")
        return jsonify({"error": "Server configuration error. Contact admin."}), 500

    except anthropic.RateLimitError:
        logger.warning("Anthropic rate limit hit")
        return jsonify({"error": "Translation service is busy. Try again shortly."}), 503

    except anthropic.APIError as e:
        logger.error("Anthropic API error: %s", e)
        return jsonify({"error": "Translation failed. Please try again."}), 502

    except Exception as e:
        logger.exception("Unexpected error: %s", e)
        return jsonify({"error": "An unexpected error occurred."}), 500


@app.post("/translate/batch")
@rate_limit
def translate_batch():
    """
    POST /translate/batch
    Body: { "texts": ["text1", "text2", ...] }   — max 10 items
    Returns: { "results": ["tamil1", "tamil2", ...] }

    Useful for teachers translating multiple questions at once.
    """
    data = request.get_json(silent=True)

    if not data or "texts" not in data:
        return jsonify({"error": "Request body must include a 'texts' array."}), 400

    texts = data["texts"]

    if not isinstance(texts, list) or len(texts) == 0:
        return jsonify({"error": "'texts' must be a non-empty array."}), 400

    if len(texts) > 10:
        return jsonify({"error": "Maximum 10 texts per batch request."}), 400

    results = []
    errors  = []

    for i, text in enumerate(texts):
        text = str(text).strip()
        if not text:
            results.append("")
            continue
        if len(text) > 2000:
            errors.append(f"Item {i}: too long (max 2000 chars)")
            results.append("")
            continue
        try:
            message = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=1024,
                system=SYSTEM_PROMPT,
                messages=[
                    {"role": "user", "content": f"Translate this Tanglish to Tamil Unicode:\n\n{text}"}
                ],
            )
            results.append(message.content[0].text.strip())
        except Exception as e:
            logger.error("Batch item %d failed: %s", i, e)
            errors.append(f"Item {i}: translation failed")
            results.append("")

    return jsonify({"results": results, "errors": errors})


# ── Entry point ────────────────────────────────────────────────────────────
if __name__ == "__main__":
    if not os.environ.get("ANTHROPIC_API_KEY"):
        raise RuntimeError("ANTHROPIC_API_KEY environment variable is not set!")
    app.run(debug=True, port=5000)
