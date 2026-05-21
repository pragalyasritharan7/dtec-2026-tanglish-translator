import { useState, useRef } from "react";

const STYLES = `
  @import url('https://fonts.googleapis.com/css2?family=Lora:ital,wght@0,400;0,600;1,400&family=JetBrains+Mono:wght@400;500&display=swap');
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body { background: #0d0d0d; min-height: 100vh; font-family: 'Lora', serif; }
  .app { min-height: 100vh; background: #0d0d0d; color: #f0ebe0; display: flex; flex-direction: column; }
  .accent-line { position: fixed; top: 0; left: 0; right: 0; height: 3px; background: linear-gradient(90deg, #c8854a, #e8b97a, #c8854a); z-index: 100; }
  header { position: relative; z-index: 10; padding: 40px 40px 28px; border-bottom: 1px solid rgba(200,133,74,0.15); }
  .header-inner { max-width: 900px; margin: 0 auto; display: flex; align-items: flex-end; justify-content: space-between; flex-wrap: wrap; gap: 16px; }
  .logo-ta { font-size: 13px; letter-spacing: 0.2em; color: #c8854a; text-transform: uppercase; margin-bottom: 6px; }
  .logo-title { font-size: 28px; font-weight: 600; color: #f0ebe0; }
  .logo-sub { font-size: 13px; color: rgba(240,235,224,0.4); margin-top: 4px; font-style: italic; }
  .badge { background: rgba(200,133,74,0.12); border: 1px solid rgba(200,133,74,0.3); border-radius: 4px; padding: 6px 14px; font-size: 11px; letter-spacing: 0.15em; color: #c8854a; text-transform: uppercase; font-family: 'JetBrains Mono', monospace; }
  main { flex: 1; padding: 32px 40px 60px; max-width: 900px; margin: 0 auto; width: 100%; }

  .mode-tabs { display: flex; gap: 8px; margin-bottom: 20px; }
  .mode-tab { background: rgba(240,235,224,0.04); border: 1px solid rgba(240,235,224,0.1); border-radius: 6px; padding: 8px 18px; font-size: 13px; color: rgba(240,235,224,0.5); cursor: pointer; font-family: 'JetBrains Mono', monospace; letter-spacing: 0.05em; transition: all 0.2s; }
  .mode-tab.active { background: rgba(200,133,74,0.12); border-color: rgba(200,133,74,0.4); color: #e8b97a; }

  .translator-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 0; border: 1px solid rgba(200,133,74,0.2); border-radius: 12px; overflow: hidden; background: #141414; margin-bottom: 20px; }
  .panel { display: flex; flex-direction: column; }
  .panel-left { border-right: 1px solid rgba(200,133,74,0.15); }
  .panel-header { padding: 12px 20px; border-bottom: 1px solid rgba(200,133,74,0.1); display: flex; align-items: center; gap: 8px; }
  .panel-lang { font-family: 'JetBrains Mono', monospace; font-size: 11px; letter-spacing: 0.15em; text-transform: uppercase; color: rgba(240,235,224,0.5); }
  .panel-dot { width: 6px; height: 6px; border-radius: 50%; background: #c8854a; flex-shrink: 0; }
  .panel-dot.output { background: #5a9e7a; }
  textarea { flex: 1; min-height: 200px; background: transparent; border: none; outline: none; resize: none; padding: 18px 20px; font-family: 'Lora', serif; font-size: 16px; line-height: 1.7; color: #f0ebe0; caret-color: #c8854a; }
  textarea::placeholder { color: rgba(240,235,224,0.2); font-style: italic; }
  .output-panel { flex: 1; min-height: 200px; padding: 18px 20px; font-size: 16px; line-height: 1.7; }
  .output-placeholder { color: rgba(240,235,224,0.2); font-style: italic; }
  .tamil-text { color: #e8d5b0; font-size: 18px; line-height: 1.8; animation: fadeIn 0.5s ease; }
  @keyframes fadeIn { from { opacity: 0; transform: translateY(6px); } to { opacity: 1; transform: translateY(0); } }
  .translating-state { display: flex; align-items: center; gap: 10px; color: rgba(240,235,224,0.4); font-style: italic; font-size: 14px; }
  .dots span { display: inline-block; width: 4px; height: 4px; border-radius: 50%; background: #c8854a; margin: 0 2px; animation: bounce 1.2s infinite; }
  .dots span:nth-child(2) { animation-delay: 0.2s; }
  .dots span:nth-child(3) { animation-delay: 0.4s; }
  @keyframes bounce { 0%,80%,100% { transform: translateY(0); opacity: 0.4; } 40% { transform: translateY(-5px); opacity: 1; } }
  .panel-footer { padding: 8px 20px; border-top: 1px solid rgba(200,133,74,0.1); display: flex; align-items: center; justify-content: space-between; min-height: 40px; }
  .char-count { font-family: 'JetBrains Mono', monospace; font-size: 11px; color: rgba(240,235,224,0.25); }
  .action-btn { background: none; border: none; cursor: pointer; font-size: 11px; letter-spacing: 0.08em; text-transform: uppercase; color: rgba(240,235,224,0.3); font-family: 'JetBrains Mono', monospace; padding: 4px 6px; transition: color 0.2s; border-radius: 4px; }
  .action-btn:hover { color: rgba(240,235,224,0.7); }
  .action-btn.active { color: #5a9e7a; }
  .action-btn.speaking { color: #c8854a; }
  .translate-btn { width: 100%; background: #c8854a; border: none; border-radius: 8px; padding: 14px; color: #0d0d0d; font-weight: 600; font-family: 'Lora', serif; font-size: 15px; cursor: pointer; transition: background 0.2s, transform 0.1s; }
  .translate-btn:hover:not(:disabled) { background: #e8a060; }
  .translate-btn:active:not(:disabled) { transform: scale(0.98); }
  .translate-btn:disabled { background: rgba(200,133,74,0.3); cursor: not-allowed; color: rgba(13,13,13,0.5); }

  .upload-zone { min-height: 200px; display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 12px; cursor: pointer; transition: background 0.2s; padding: 20px; }
  .upload-zone:hover { background: rgba(200,133,74,0.04); }
  .upload-zone.dragging { background: rgba(200,133,74,0.08); border-color: rgba(200,133,74,0.4); }
  .upload-icon { font-size: 32px; color: rgba(240,235,224,0.2); }
  .upload-text { font-size: 14px; color: rgba(240,235,224,0.3); text-align: center; font-style: italic; }
  .upload-sub { font-size: 12px; color: rgba(240,235,224,0.2); font-family: 'JetBrains Mono', monospace; }
  .preview-img { max-width: 100%; max-height: 180px; border-radius: 6px; object-fit: contain; }
  .extracted-label { font-family: 'JetBrains Mono', monospace; font-size: 10px; letter-spacing: 0.15em; text-transform: uppercase; color: rgba(240,235,224,0.3); margin-bottom: 4px; }
  .extracted-text { font-size: 14px; color: rgba(240,235,224,0.5); font-style: italic; padding: 8px 12px; background: rgba(240,235,224,0.04); border-radius: 6px; margin-bottom: 12px; }

  .examples-section { margin-top: 28px; }
  .examples-label { font-family: 'JetBrains Mono', monospace; font-size: 11px; letter-spacing: 0.2em; text-transform: uppercase; color: rgba(240,235,224,0.3); margin-bottom: 10px; }
  .examples-grid { display: flex; flex-wrap: wrap; gap: 8px; }
  .example-chip { background: rgba(240,235,224,0.04); border: 1px solid rgba(240,235,224,0.1); border-radius: 6px; padding: 7px 14px; font-size: 13px; color: rgba(240,235,224,0.5); cursor: pointer; font-style: italic; transition: all 0.2s; }
  .example-chip:hover { background: rgba(200,133,74,0.08); border-color: rgba(200,133,74,0.3); color: #e8b97a; }
  .error-msg { background: rgba(200,60,60,0.1); border: 1px solid rgba(200,60,60,0.3); border-radius: 8px; padding: 10px 14px; font-size: 13px; color: #e88080; margin-bottom: 14px; font-family: 'JetBrains Mono', monospace; }
  .history-section { margin-top: 32px; border-top: 1px solid rgba(200,133,74,0.1); padding-top: 20px; }
  .history-item { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; padding: 10px 0; border-bottom: 1px solid rgba(240,235,224,0.05); font-size: 13px; cursor: pointer; }
  .history-item:hover { opacity: 0.8; }
  .history-tanglish { color: rgba(240,235,224,0.4); font-style: italic; }
  .history-tamil { color: #e8d5b0; }
  .info-strip { margin-top: 36px; border-top: 1px solid rgba(200,133,74,0.1); padding-top: 20px; display: grid; grid-template-columns: repeat(3,1fr); gap: 20px; }
  .info-title { font-family: 'JetBrains Mono', monospace; font-size: 10px; letter-spacing: 0.2em; text-transform: uppercase; color: #c8854a; margin-bottom: 5px; }
  .info-body { font-size: 13px; color: rgba(240,235,224,0.4); line-height: 1.6; }
  @media (max-width: 620px) {
    .translator-grid { grid-template-columns: 1fr; }
    .panel-left { border-right: none; border-bottom: 1px solid rgba(200,133,74,0.15); }
    main { padding: 20px 16px 48px; }
    header { padding: 28px 16px 20px; }
    .info-strip, .history-item { grid-template-columns: 1fr; gap: 8px; }
    .mode-tabs { flex-wrap: wrap; }
  }
`;

const API_BASE = "http://localhost:8000";

const EXAMPLES = [
  "Vanakkam, eppadi irukkinga?",
  "Naan school ku porom",
  "Ungalukku Tamil theriyuma?",
  "Iniku weather romba hot aa iruku",
  "Nee yaar, enna panra?",
];

export default function TanglishTranslator() {
  const [mode, setMode]       = useState("text");   // "text" | "image"
  const [input, setInput]     = useState("");
  const [output, setOutput]   = useState("");
  const [extracted, setExtracted] = useState("");
  const [imageFile, setImageFile] = useState(null);
  const [imagePreview, setImagePreview] = useState(null);
  const [dragging, setDragging] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError]     = useState("");
  const [copied, setCopied]   = useState(false);
  const [speaking, setSpeaking] = useState(false);
  const [history, setHistory] = useState([]);
  const fileInputRef          = useRef(null);

  // ── Text translation ──────────────────────────────────────────────────
  async function translate() {
    if (!input.trim()) return;
    setLoading(true); setOutput(""); setError(""); stopSpeech();
    try {
      const res  = await fetch(`${API_BASE}/translate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text: input.trim() }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || "Translation failed");
      setOutput(data.tamil);
      setHistory(prev => [{ tanglish: input.trim(), tamil: data.tamil }, ...prev.slice(0, 9)]);
    } catch (err) {
      setError(err.message || "Could not connect to server.");
    } finally {
      setLoading(false);
    }
  }

  // ── Image OCR + translation ───────────────────────────────────────────
  async function translateImage() {
    if (!imageFile) return;
    setLoading(true); setOutput(""); setExtracted(""); setError(""); stopSpeech();
    try {
      const formData = new FormData();
      formData.append("image", imageFile);
      const res  = await fetch(`${API_BASE}/ocr`, { method: "POST", body: formData });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || "OCR failed");
      setExtracted(data.extracted_text);
      setOutput(data.tamil);
      setHistory(prev => [{ tanglish: data.extracted_text, tamil: data.tamil }, ...prev.slice(0, 9)]);
    } catch (err) {
      setError(err.message || "Could not process image.");
    } finally {
      setLoading(false);
    }
  }

  // ── Image handlers ────────────────────────────────────────────────────
  function handleImageSelect(file) {
    if (!file || !file.type.startsWith("image/")) return;
    setImageFile(file);
    setImagePreview(URL.createObjectURL(file));
    setOutput(""); setExtracted(""); setError("");
  }

  function handleDrop(e) {
    e.preventDefault(); setDragging(false);
    handleImageSelect(e.dataTransfer.files[0]);
  }

  // ── Tamil Text-to-Speech ──────────────────────────────────────────────
  function speakTamil() {
    if (!output) return;
    if (speaking) { stopSpeech(); return; }
    const u = new SpeechSynthesisUtterance(output);
    const voices = window.speechSynthesis.getVoices();
    const tamilVoice = voices.find(v => v.lang.startsWith("ta") || v.name.toLowerCase().includes("tamil"));
    if (tamilVoice) u.voice = tamilVoice;
    u.lang = "ta-IN"; u.rate = 0.85;
    u.onstart = () => setSpeaking(true);
    u.onend   = () => setSpeaking(false);
    u.onerror = () => setSpeaking(false);
    window.speechSynthesis.speak(u);
  }

  function stopSpeech() { window.speechSynthesis.cancel(); setSpeaking(false); }

  function copyOutput() {
    if (!output) return;
    navigator.clipboard.writeText(output);
    setCopied(true); setTimeout(() => setCopied(false), 2000);
  }

  function loadExample(ex) { setInput(ex); setOutput(""); setError(""); stopSpeech(); }
  function handleKeyDown(e) { if ((e.ctrlKey || e.metaKey) && e.key === "Enter") translate(); }

  function switchMode(m) {
    setMode(m); setOutput(""); setError(""); setExtracted("");
    stopSpeech();
  }

  return (
    <div className="app">
      <style>{STYLES}</style>
      <div className="accent-line" />

      <header>
        <div className="header-inner">
          <div>
            <div className="logo-ta">தமிழ் · Tamil</div>
            <div className="logo-title">Tanglish → Tamil</div>
            <div className="logo-sub">Powered by Google + Groq AI · DTEC 2026</div>
          </div>
          <div className="badge">Hackathon Build</div>
        </div>
      </header>

      <main>
        {error && <div className="error-msg">⚠ {error}</div>}

        {/* Mode tabs */}
        <div className="mode-tabs">
          <button className={`mode-tab${mode === "text" ? " active" : ""}`} onClick={() => switchMode("text")}>
            ⌨ Type Tanglish
          </button>
          <button className={`mode-tab${mode === "image" ? " active" : ""}`} onClick={() => switchMode("image")}>
            📷 Upload Handwritten Image
          </button>
        </div>

        <div className="translator-grid">
          {/* LEFT PANEL */}
          <div className="panel panel-left">
            <div className="panel-header">
              <div className="panel-dot" />
              <span className="panel-lang">{mode === "text" ? "Tanglish Input" : "Handwritten Image"}</span>
            </div>

            {mode === "text" ? (
              <textarea
                value={input}
                onChange={e => setInput(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder={"Type Tanglish here…\ne.g. Vanakkam, eppadi irukkinga?"}
                spellCheck={false}
              />
            ) : (
              <div
                className={`upload-zone${dragging ? " dragging" : ""}`}
                onClick={() => fileInputRef.current?.click()}
                onDragOver={e => { e.preventDefault(); setDragging(true); }}
                onDragLeave={() => setDragging(false)}
                onDrop={handleDrop}
              >
                <input
                  type="file" ref={fileInputRef} style={{ display: "none" }}
                  accept="image/png,image/jpeg,image/webp"
                  onChange={e => handleImageSelect(e.target.files[0])}
                />
                {imagePreview ? (
                  <img src={imagePreview} alt="Uploaded" className="preview-img" />
                ) : (
                  <>
                    <div className="upload-icon">📷</div>
                    <div className="upload-text">Click or drag & drop a photo of handwritten Tanglish</div>
                    <div className="upload-sub">PNG · JPG · WEBP · max 5MB</div>
                  </>
                )}
              </div>
            )}

            <div className="panel-footer">
              <span className="char-count">
                {mode === "text" ? `${input.length} / 2000` : imageFile ? imageFile.name.slice(0, 20) : ""}
              </span>
              {(mode === "text" && input) || (mode === "image" && imageFile) ? (
                <button className="action-btn" onClick={() => {
                  setInput(""); setOutput(""); setError(""); setImageFile(null);
                  setImagePreview(null); setExtracted(""); stopSpeech();
                }}>Clear</button>
              ) : null}
            </div>
          </div>

          {/* RIGHT PANEL */}
          <div className="panel">
            <div className="panel-header">
              <div className="panel-dot output" />
              <span className="panel-lang">Tamil Output</span>
            </div>
            <div className="output-panel">
              {loading ? (
                <div className="translating-state">
                  <div className="dots"><span /><span /><span /></div>
                  {mode === "image" ? "Reading image & translating…" : "Translating…"}
                </div>
              ) : output ? (
                <>
                  {extracted && (
                    <>
                      <div className="extracted-label">Extracted text</div>
                      <div className="extracted-text">{extracted}</div>
                    </>
                  )}
                  <div className="tamil-text">{output}</div>
                </>
              ) : (
                <div className="output-placeholder">
                  {mode === "image" ? "Upload an image and click Translate →" : "Tamil translation will appear here…"}
                </div>
              )}
            </div>
            <div className="panel-footer">
              <span className="char-count">{output ? `${output.length} chars` : ""}</span>
              <div style={{ display: "flex", gap: "4px" }}>
                {output && <>
                  <button className={`action-btn${speaking ? " speaking" : ""}`} onClick={speakTamil}>
                    {speaking ? "⏹ Stop" : "🔊 Listen"}
                  </button>
                  <button className={`action-btn${copied ? " active" : ""}`} onClick={copyOutput}>
                    {copied ? "✓ Copied" : "Copy"}
                  </button>
                </>}
              </div>
            </div>
          </div>
        </div>

        {/* Translate Button */}
        <button
          className="translate-btn"
          onClick={mode === "text" ? translate : translateImage}
          disabled={loading || (mode === "text" ? !input.trim() : !imageFile)}
        >
          {loading ? (mode === "image" ? "Reading & Translating…" : "Translating…") : "Translate →"}
        </button>

        {/* Examples (text mode only) */}
        {mode === "text" && (
          <div className="examples-section">
            <div className="examples-label">Try an example</div>
            <div className="examples-grid">
              {EXAMPLES.map(ex => (
                <button key={ex} className="example-chip" onClick={() => loadExample(ex)}>{ex}</button>
              ))}
            </div>
          </div>
        )}

        {/* History */}
        {history.length > 0 && (
          <div className="history-section">
            <div className="examples-label">Recent translations</div>
            {history.map((h, i) => (
              <div key={i} className="history-item" onClick={() => { setMode("text"); setInput(h.tanglish); setOutput(h.tamil); }}>
                <div className="history-tanglish">{h.tanglish}</div>
                <div className="history-tamil">{h.tamil}</div>
              </div>
            ))}
          </div>
        )}

        {/* Info */}
        <div className="info-strip">
          <div>
            <div className="info-title">Type or upload</div>
            <div className="info-body">Type Tanglish directly or upload a photo of handwritten Tamil text.</div>
          </div>
          <div>
            <div className="info-title">How it works</div>
            <div className="info-body">Google Input Tools converts words → Groq AI fixes grammar → perfect Tamil Unicode.</div>
          </div>
          <div>
            <div className="info-title">Audio output</div>
            <div className="info-body">Click 🔊 Listen to hear the Tamil translation spoken aloud.</div>
          </div>
        </div>
      </main>
    </div>
  );
}
