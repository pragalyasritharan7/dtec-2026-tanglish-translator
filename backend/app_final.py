"""
DTEC 2026 Hackathon — Tanglish to Tamil Translator
Flask Backend FINAL — Casual spoken Tamil output
"""

import os
import re
import time
import logging
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

# ── Accurate manual word map ───────────────────────────────────────────────
WORD_MAP = {
    "vanakkam": "வணக்கம்", "naan": "நான்", "nee": "நீ",
    "avan": "அவன்", "aval": "அவள்", "avanga": "அவங்க",
    "enna": "என்ன", "epdi": "எப்படி", "eppadi": "எப்படி",
    "irukkinga": "இருக்கீங்க", "irukkeenga": "இருக்கீங்க",
    "irukken": "இருக்கேன்", "irukkaan": "இருக்கான்",
    "irukkaa": "இருக்கா", "iruku": "இருக்கு",
    "porom": "போறோம்", "pogiren": "போகிறேன்",
    "varen": "வாரேன்", "paaru": "பாரு",
    "romba": "ரொம்ப", "konjam": "கொஞ்சம்",
    "sollu": "சொல்லு", "theriyum": "தெரியும்",
    "theriyaadu": "தெரியாது", "theriyala": "தெரியல",
    "saapidu": "சாப்பிடு", "vaa": "வா", "po": "போ",
    "paesu": "பேசு", "iniku": "இன்னிக்கு",
    "inniku": "இன்னிக்கு", "naalaiku": "நாளைக்கு",
    "nalla": "நல்ல", "nallaa": "நல்லா", "ketta": "கெட்ட",
    "periya": "பெரிய", "chinna": "சின்ன",
    "veetu": "வீட்டு", "veedu": "வீடு",
    "yaar": "யார்", "enge": "எங்கே", "yenga": "எங்க",
    "inge": "இங்கே", "anga": "அங்க",
    "seri": "சரி", "sari": "சரி",
    "illa": "இல்ல", "illai": "இல்லை",
    "aama": "ஆமா", "aamam": "ஆமாம்",
    "adhu": "அது", "idhu": "இது", "edhu": "எது",
    "oru": "ஒரு", "rendu": "ரெண்டு",
    "neram": "நேரம்", "naal": "நாள்",
    "pannunga": "பண்ணுங்க", "pannuren": "பண்றேன்",
    "thamizh": "தமிழ்", "tamil": "தமிழ்",
    "amma": "அம்மா", "appa": "அப்பா",
    "akka": "அக்கா", "thambi": "தம்பி",
    "thangachi": "தங்கச்சி", "anna": "அண்ணா",
    "nanban": "நண்பன்", "nanbi": "நண்பி",
    "kadhal": "காதல்", "paattu": "பாட்டு",
    "padam": "படம்", "velai": "வேலை",
    "semma": "சேம்மா", "super": "சூப்பர்",
    "unga": "உங்க", "enga": "எங்க",
    "neenga": "நீங்க", "avanga": "அவங்க",
    "enaku": "எனக்கு", "unaku": "உனக்கு",
    "avanu": "அவனுக்கு", "avaluku": "அவளுக்கு",
    "patha": "பாத்த", "sonnen": "சொன்னேன்",
    "keten": "கேட்டேன்", "vanden": "வந்தேன்",
    "ponen": "போனேன்", "sapitten": "சாப்பிட்டேன்",
    "intha": "இந்த", "antha": "அந்த",
    "indha": "இந்த", "andha": "அந்த",
    "ithu": "இது", "athu": "அது",
    "apdi": "அப்படி", "appadi": "அப்படி",
    "ippadi": "இப்படி", "ipdi": "இப்படி",
    "adhaan": "அதான்", "idhaane": "இதானே",
    "paakalam": "பாக்கலாம்", "pogalam": "போகலாம்",
    "vaalam": "வரலாம்", "saapidalam": "சாப்பிடலாம்",
    "pesalam": "பேசலாம்", "kelalam": "கேக்கலாம்",
    "vaanam": "வானம்", "mazhai": "மழை",
    "veyyil": "வெயில்", "kaalai": "காலை",
    "maalam": "மாலை", "iravu": "இரவு",
    "pagal": "பகல்", "sutham": "சுத்தம்",
    "azhagu": "அழகு", "valippu": "வலிப்பு",
    "kashtam": "கஷ்டம்", "sukham": "சுகம்",
    "santhosham": "சந்தோஷம்", "dukkam": "துக்கம்",
    "கோபம்": "கோபம்", "aasai": "ஆசை",
    "ok": "சரி", "okay": "சரி",
    "thanks": "நன்றி", "thank": "நன்றி",
    "sorry": "மன்னிக்கவும்",
    "hi": "வணக்கம்", "hello": "வணக்கம்",
    "bye": "போய்வருகிறேன்",
    "ku": "க்கு", "la": "ல", "le": "ல",
    "oda": "ஓட", "kita": "கிட்ட",
    "kitta": "கிட்ட", "pakkam": "பக்கம்",
    "mela": "மேல", "kela": "கீழ",
    "munna": "முன்ன", "pinna": "பின்ன",
    "hot": "சூடா", "cold": "குளிரா",
    "noia": "நோய", "valikuthu": "வலிக்குது",
    "thalaivali": "தலைவலி", "vayiru": "வயிறு",
}

def preprocess(text: str) -> str:
    """Replace known Tanglish words with Tamil Unicode."""
    words = re.findall(r"[\w']+|[.,!?;]", text)
    result = []
    for word in words:
        clean = re.sub(r"[^\w]", "", word.lower())
        if clean in WORD_MAP:
            result.append(WORD_MAP[clean])
        else:
            result.append(word)
    return " ".join(result)

# ── Final system prompt ────────────────────────────────────────────────────
SYSTEM_PROMPT = """You are a Tamil language expert specializing in casual spoken Tamil (பேச்சு தமிழ்).

You will receive text that is a MIX of:
- Already translated Tamil Unicode words
- Some remaining Tanglish (Roman script Tamil) words

YOUR JOB:
1. Translate any remaining Tanglish words to Tamil Unicode
2. Make the sentence sound like NATURAL CASUAL SPOKEN Tamil — NOT formal/literary Tamil
3. Keep proper nouns, brand names, and English words as-is
4. Return ONLY the final Tamil text — no explanations

CRITICAL RULES FOR CASUAL TAMIL:
- Use இருக்கீங்க NOT இருக்கிறீர்கள்
- Use போறேன் NOT போகிறேன்
- Use வாரேன் NOT வருகிறேன்
- Use என்ன NOT என்னை (casual)
- Use நல்லா NOT நன்றாக
- Use ரொம்ப NOT மிகவும்
- Use கொஞ்சம் NOT சிறிது
- Casual questions end with ஆ? NOT ஆகுமா?
- Keep the natural rhythm of everyday Tamil speech

EXAMPLES:
Input: வணக்கம் eppadi இருக்கீங்க
Output: வணக்கம், எப்படி இருக்கீங்க?

Input: நான் school போறேன் naalaiku
Output: நான் school-க்கு நாளைக்கு போறேன்

Input: இன்னிக்கு weather ரொம்ப hot aa iruku
Output: இன்னிக்கு வானிலை ரொம்ப சூடா இருக்கு"""


def translate_pipeline(text: str) -> str:
    step1 = preprocess(text)
    logger.info("After word map: %s", step1)

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user",   "content": step1},
        ],
        max_tokens=1024,
        temperature=0.1,
    )
    return response.choices[0].message.content.strip()


@app.get("/health")
def health():
    return jsonify({"status": "ok", "service": "tanglish-translator"})


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
        return jsonify({"tamil": result, "input_chars": len(text), "output_chars": len(result)})
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
            errors.append(f"Item {i}: failed")
            results.append("")
    return jsonify({"results": results, "errors": errors})


if __name__ == "__main__":
    if not os.environ.get("GROQ_API_KEY"):
        raise RuntimeError("GROQ_API_KEY not set!")
    app.run(debug=True, port=8000, host="0.0.0.0")
