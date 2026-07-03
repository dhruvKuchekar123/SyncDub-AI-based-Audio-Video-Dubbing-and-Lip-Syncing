import React, { useState, useRef, useEffect } from "react";
import axios from "axios";

// ------------------- FUTURISTIC DESIGN SYSTEM -------------------
const styles = `
  @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&family=Inter:wght@300;400;500;600;700&display=swap');

  *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

  :root {
    --bg-dark: #050508;
    --bg-card: rgba(13, 13, 22, 0.7);
    --border-glass: rgba(255, 255, 255, 0.08);
    --accent-violet: #8b5cf6;
    --accent-orange: #f97316;
    --accent-glow: rgba(139, 92, 246, 0.4);
    --text-main: #f8fafc;
    --text-dim: #94a3b8;
    --success: #10b981;
    --font-head: 'Outfit', sans-serif;
    --font-body: 'Inter', sans-serif;
  }

  body {
    background: var(--bg-dark);
    color: var(--text-main);
    font-family: var(--font-body);
    min-height: 100vh;
    overflow-x: hidden;
  }

  .app-container {
    min-height: 100vh;
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 60px 20px;
    position: relative;
    z-index: 1;
  }

  /* BACKGROUND EFFECTS */
  .bg-noise {
    position: fixed;
    inset: 0;
    z-index: 0;
    opacity: 0.04;
    pointer-events: none;
    background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.65' numOctaves='3' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noise)'/%3E%3C/svg%3E");
  }

  .bg-glow-1 {
    position: fixed;
    top: -10%; left: -10%;
    width: 60vw; height: 60vw;
    background: radial-gradient(circle, rgba(139, 92, 246, 0.1) 0%, transparent 70%);
    z-index: 0;
    pointer-events: none;
    animation: rotate 20s linear infinite;
  }

  .bg-glow-2 {
    position: fixed;
    bottom: -10%; right: -10%;
    width: 50vw; height: 50vw;
    background: radial-gradient(circle, rgba(249, 115, 22, 0.07) 0%, transparent 70%);
    z-index: 0;
    pointer-events: none;
  }

  @keyframes rotate { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }

  /* HERO SECTION */
  .hero {
    text-align: center;
    margin-bottom: 60px;
    animation: fadeInDown 0.8s cubic-bezier(0.16, 1, 0.3, 1);
  }

  @keyframes fadeInDown {
    from { opacity: 0; transform: translateY(-20px); }
    to { opacity: 1; transform: translateY(0); }
  }

  .logo-badge {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    background: rgba(139, 92, 246, 0.1);
    border: 1px solid rgba(139, 92, 246, 0.2);
    padding: 6px 16px;
    border-radius: 100px;
    font-size: 12px;
    font-weight: 600;
    letter-spacing: 0.05em;
    color: var(--accent-violet);
    margin-bottom: 24px;
    text-transform: uppercase;
    backdrop-filter: blur(10px);
  }

  .logo-badge span {
    width: 8px; height: 8px;
    background: var(--accent-violet);
    border-radius: 50%;
    box-shadow: 0 0 10px var(--accent-violet);
    animation: pulseGlow 1.5s ease-in-out infinite;
  }

  @keyframes pulseGlow { 0%, 100% { opacity: 0.5; transform: scale(1); } 50% { opacity: 1; transform: scale(1.2); } }

  .hero h1 {
    font-family: var(--font-head);
    font-size: clamp(40px, 8vw, 72px);
    font-weight: 800;
    letter-spacing: -0.04em;
    line-height: 0.95;
    margin-bottom: 16px;
    background: linear-gradient(135deg, #fff 40%, rgba(255,255,255,0.4));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
  }

  .hero h1 span {
    background: linear-gradient(90deg, var(--accent-violet), var(--accent-orange));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
  }

  .hero p {
    font-size: 18px;
    color: var(--text-dim);
    max-width: 500px;
    margin: 0 auto 32px;
    font-weight: 300;
    line-height: 1.6;
  }

  .lang-toggle {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 20px;
    background: rgba(255,255,255,0.03);
    padding: 12px 24px;
    border-radius: 100px;
    border: 1px solid var(--border-glass);
    width: fit-content;
    margin: 0 auto;
    backdrop-filter: blur(8px);
  }

  .lang-tag {
    font-size: 14px;
    font-weight: 600;
    color: var(--text-dim);
    display: flex;
    align-items: center;
    gap: 8px;
  }

  .lang-tag.active { color: var(--text-main); }

  .lang-tag img { width: 18px; border-radius: 2px; }

  .lang-select {
    background: rgba(255,255,255,0.05);
    border: 1px solid var(--border-glass);
    border-radius: 10px;
    color: var(--text-main);
    font-family: var(--font-body);
    font-size: 14px;
    font-weight: 600;
    padding: 6px 10px;
    cursor: pointer;
    outline: none;
  }

  .lang-select option { background: #14141f; color: var(--text-main); }

  .toggle-arrow {
    font-size: 18px;
    color: var(--accent-violet);
    text-shadow: 0 0 10px var(--accent-glow);
    animation: flowRight 2s infinite;
  }

  @keyframes flowRight { 0%, 100% { transform: translateX(0); } 50% { transform: translateX(5px); } }

  /* MAIN CARDS */
  .main-card {
    background: var(--bg-card);
    backdrop-filter: blur(20px);
    border: 1px solid var(--border-glass);
    border-radius: 32px;
    padding: 40px;
    width: 100%;
    max-width: 680px;
    box-shadow: 0 20px 50px rgba(0,0,0,0.3);
    position: relative;
    overflow: hidden;
    animation: fadeInUp 0.8s 0.2s cubic-bezier(0.16, 1, 0.3, 1) both;
  }

  .main-card::before {
    content: '';
    position: absolute;
    top: -50%; left: -50%;
    width: 200%; height: 200%;
    background: conic-gradient(transparent, transparent, transparent, var(--accent-violet));
    animation: borderRotate 8s linear infinite;
    opacity: 0.15;
    z-index: -1;
  }

  @keyframes borderRotate { 100% { transform: rotate(360deg); } }

  @keyframes fadeInUp {
    from { opacity: 0; transform: translateY(30px); }
    to { opacity: 1; transform: translateY(0); }
  }

  /* UPLOAD ZONE */
  .drop-zone {
    border: 2px dashed rgba(255, 255, 255, 0.1);
    border-radius: 24px;
    padding: 60px 20px;
    text-align: center;
    cursor: pointer;
    transition: all 0.4s ease;
    background: rgba(255, 255, 255, 0.02);
    position: relative;
  }

  .drop-zone:hover, .drop-zone.active {
    background: rgba(139, 92, 246, 0.05);
    border-color: var(--accent-violet);
    box-shadow: inset 0 0 20px rgba(139, 92, 246, 0.1);
  }

  .upload-icon-anim {
    width: 80px; height: 80px;
    background: rgba(255, 255, 255, 0.03);
    border: 1px solid var(--border-glass);
    border-radius: 20px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 32px;
    margin: 0 auto 24px;
    color: var(--accent-violet);
    position: relative;
    transition: all 0.4s ease;
  }

  .drop-zone:hover .upload-icon-anim {
    transform: translateY(-5px);
    background: var(--accent-violet);
    color: white;
    box-shadow: 0 10px 20px var(--accent-glow);
  }

  .upload-icon-anim::after {
    content: '';
    position: absolute;
    inset: -10px;
    border-radius: 25px;
    border: 2px solid var(--accent-violet);
    opacity: 0;
    animation: ripple 2s infinite;
  }

  .drop-zone:hover .upload-icon-anim::after { opacity: 1; }

  @keyframes ripple { 
    0% { transform: scale(1); opacity: 0.8; }
    100% { transform: scale(1.3); opacity: 0; }
  }

  .drop-text h2 {
    font-family: var(--font-head);
    font-size: 20px;
    font-weight: 600;
    margin-bottom: 8px;
  }

  .drop-text p {
    font-size: 14px;
    color: var(--text-dim);
  }

  /* FILE CARD */
  .selected-file-card {
    margin-top: 24px;
    background: rgba(255, 255, 255, 0.03);
    border: 1px solid var(--border-glass);
    border-radius: 16px;
    padding: 16px;
    display: flex;
    align-items: center;
    gap: 16px;
    animation: scaleIn 0.3s ease;
  }

  @keyframes scaleIn { from { opacity: 0; transform: scale(0.95); } to { opacity: 1; transform: scale(1); } }

  .file-type-icon {
    width: 48px; height: 48px;
    background: var(--accent-orange);
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 20px;
    color: white;
    box-shadow: 0 5px 15px rgba(249, 115, 22, 0.3);
  }

  .file-meta { flex: 1; min-width: 0; }
  .file-meta h3 { font-size: 14px; font-weight: 600; margin-bottom: 2px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
  .file-meta p { font-size: 12px; color: var(--text-dim); }

  .remove-btn {
    width: 32px; height: 32px;
    border-radius: 50%;
    border: none;
    background: rgba(255, 255, 255, 0.05);
    color: var(--text-dim);
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: all 0.2s;
  }

  .remove-btn:hover { background: rgba(239, 68, 68, 0.1); color: #ef4444; }

  /* STEPS & PROGRESS */
  .pipeline-card { margin-top: 24px; }

  .progress-section { margin-bottom: 32px; }

  .progress-top {
    display: flex;
    justify-content: space-between;
    align-items: flex-end;
    margin-bottom: 12px;
  }

  .pct-val {
    font-family: var(--font-head);
    font-size: 40px;
    font-weight: 800;
    line-height: 1;
    background: linear-gradient(90deg, #fff, var(--text-dim));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
  }

  .status-label { font-size: 13px; color: var(--accent-violet); font-weight: 600; text-transform: uppercase; letter-spacing: 0.1em; }

  .bar-container {
    height: 8px;
    background: rgba(255,255,255,0.05);
    border-radius: 100px;
    overflow: hidden;
    position: relative;
  }

  .bar-fill {
    height: 100%;
    background: linear-gradient(90deg, var(--accent-violet), var(--accent-orange));
    width: 0%;
    transition: width 0.6s cubic-bezier(0.16, 1, 0.3, 1);
    position: relative;
    box-shadow: 0 0 20px rgba(139, 92, 246, 0.5);
  }

  .bar-fill::after {
    content: '';
    position: absolute;
    inset: 0;
    background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
    animation: slideShimmer 2s infinite;
  }

  @keyframes slideShimmer { from { transform: translateX(-100%); } to { transform: translateX(100%); } }

  .pipeline-steps {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 12px;
  }

  .step-item {
    padding: 12px 16px;
    background: rgba(255, 255, 255, 0.02);
    border: 1px solid var(--border-glass);
    border-radius: 12px;
    display: flex;
    align-items: center;
    gap: 12px;
    font-size: 13px;
    color: var(--text-dim);
    transition: all 0.3s;
  }

  .step-item.active { background: rgba(139, 92, 246, 0.1); border-color: var(--accent-violet); color: var(--text-main); }
  .step-item.done { color: var(--success); }

  .dot-icon {
    width: 18px; height: 18px;
    border-radius: 50%;
    border: 1.5px solid currentColor;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 10px;
  }

  /* BUTTONS */
  .btn-start {
    width: 100%;
    padding: 20px;
    border-radius: 20px;
    border: none;
    font-family: var(--font-head);
    font-size: 18px;
    font-weight: 700;
    color: white;
    cursor: pointer;
    background: linear-gradient(135deg, var(--accent-violet), #6d28d9);
    box-shadow: 0 10px 40px rgba(139, 92, 246, 0.3);
    position: relative;
    overflow: hidden;
    transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
    margin-top: 32px;
  }

  .btn-start:hover:not(:disabled) {
    transform: translateY(-4px);
    box-shadow: 0 20px 50px rgba(139, 92, 246, 0.5);
    background: linear-gradient(135deg, var(--accent-orange), #ea580c);
  }

  .btn-start:active:not(:disabled) { transform: translateY(-1px); }

  .btn-start:disabled { opacity: 0.6; cursor: not-allowed; animation: shimmerBg 2s infinite linear; }

  @keyframes shimmerBg {
    0% { background-position: -200% 0; }
    100% { background-position: 200% 0; }
  }

  /* VIDEO OUTPUT */
  .output-section {
    width: 100%;
    animation: fadeInUp 1s ease;
  }

  .video-container {
    border-radius: 24px;
    overflow: hidden;
    border: 1px solid var(--border-glass);
    background: #000;
    box-shadow: 0 0 40px rgba(0,0,0,0.5);
    position: relative;
  }

  video { width: 100%; display: block; border-radius: 23px; }

  .output-actions {
    display: grid;
    grid-template-columns: 2fr 1fr;
    gap: 12px;
    margin-top: 24px;
  }

  .control-btn {
    padding: 16px;
    border-radius: 16px;
    border: 1px solid var(--border-glass);
    background: rgba(255,255,255,0.03);
    color: var(--text-main);
    font-weight: 600;
    cursor: pointer;
    transition: all 0.2s;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
  }

  .control-btn.primary { background: var(--success); color: #000; border: none; }
  .control-btn.primary:hover { transform: translateY(-2px); box-shadow: 0 10px 20px rgba(16, 185, 129, 0.3); }
  .control-btn.outline:hover { background: rgba(255,255,255,0.08); border-color: rgba(255,255,255,0.2); }

  .wave-visualizer {
    height: 30px;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 3px;
    margin-top: 20px;
    opacity: 0.5;
  }

  .wave-bar {
    width: 3px;
    background: var(--accent-violet);
    border-radius: 10px;
    height: 10px;
    animation: waveBounce 1.2s ease-in-out infinite;
  }

  @keyframes waveBounce { 0%, 100% { height: 8px; } 50% { height: 25px; } }

  /* RESPONSIVE */
  @media (max-width: 600px) {
    .pipeline-steps { grid-template-columns: 1fr; }
    .hero h1 { font-size: 48px; }
    .main-card { padding: 24px; }
  }
`;

const API_BASE = process.env.REACT_APP_API_URL || "http://127.0.0.1:8000";

function formatSize(bytes) {
  if (!bytes) return "0 Bytes";
  const k = 1024;
  const sizes = ["Bytes", "KB", "MB", "GB"];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + " " + sizes[i];
}

const STEPS = [
  { id: "upload", icon: "📤", label: "Uploading video", start: 0, end: 15 },
  { id: "extract", icon: "🔊", label: "Extracting audio", start: 16, end: 30 },
  { id: "transcribe", icon: "📝", label: "Transcribing speech", start: 31, end: 50 },
  { id: "translate", icon: "🌐", label: "Translating", start: 51, end: 70 },
  { id: "synthesize", icon: "🎙️", label: "Synthesizing voice", start: 71, end: 85 },
  { id: "lipsync", icon: "👄", label: "Lip-sync processing", start: 86, end: 95 },
  { id: "render", icon: "🎬", label: "Final rendering", start: 96, end: 100 },
];

export default function App() {
  const [file, setFile] = useState(null);
  const [isDragging, setIsDragging] = useState(false);
  const [progress, setProgress] = useState(0);
  const [status, setStatus] = useState("");
  const [outputUrl, setOutputUrl] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [isDone, setIsDone] = useState(false);
  const [languages, setLanguages] = useState([
    { code: "hi", display_name: "Hindi" },
    { code: "mr", display_name: "Marathi" },
  ]);
  const [sourceLang, setSourceLang] = useState("hi");
  const [targetLang, setTargetLang] = useState("mr");
  const fileInput = useRef();

  useEffect(() => {
    axios.get(`${API_BASE}/languages`)
      .then((res) => setLanguages(res.data.languages))
      .catch(() => {}); // keep the hi/mr defaults if the backend is down
  }, []);

  const handleFile = (f) => {
    if (f && f.type.startsWith("video/")) {
      setFile(f);
      setError("");
    } else {
      setError("Please drop a valid video file.");
    }
  };

  const startProcessing = async () => {
    if (!file) return;
    setLoading(true);
    setIsDone(false);
    setProgress(0);
    setError("");
    setStatus("Initializing AI Pipeline...");

    try {
      const form = new FormData();
      form.append("file", file);
      form.append("source_lang", sourceLang);
      form.append("target_lang", targetLang);
      const res = await axios.post(`${API_BASE}/jobs`, form);
      pollProgress(res.data.job_id);
    } catch (err) {
      const detail = err.response?.data?.detail;
      setError(detail || "AI Gateway Timeout. Ensure the backend is running.");
      setLoading(false);
    }
  };

  const pollProgress = (jobId) => {
    const timer = setInterval(async () => {
      try {
        const res = await axios.get(`${API_BASE}/progress/${jobId}`);
        setProgress(res.data.progress);
        setStatus(res.data.status);

        if (res.data.state === "error") {
          clearInterval(timer);
          setError(res.data.error || "Pipeline failed. Check backend/jobs logs.");
          setLoading(false);
        } else if (res.data.state === "done") {
          clearInterval(timer);
          fetchFinalVideo(jobId);
        }
      } catch (e) {
        clearInterval(timer);
        setError("Pipeline Interrupted. Retrying connection...");
        setLoading(false);
      }
    }, 1500);
  };

  const fetchFinalVideo = async (jobId) => {
    try {
      const res = await axios.get(`${API_BASE}/video/${jobId}`);
      setOutputUrl(API_BASE + res.data.video_url);
      setLoading(false);
      setIsDone(true);
      setStatus("Mission Complete");
    } catch (e) {
      setError("Final render retrieval failed.");
      setLoading(false);
    }
  };

  const currentStepIndex = STEPS.findIndex(s => progress <= s.end);

  return (
    <div className="app-root">
      <style>{styles}</style>
      <div className="bg-noise" />
      <div className="bg-glow-1" />
      <div className="bg-glow-2" />

      <div className="app-container">
        {/* HERO */}
        <header className="hero">
          <div className="logo-badge">
            <span />
            Autonomous AI Dubbing Engine
          </div>
          <h1>Sync<span>Dub</span></h1>
          <p>
            Transform videos into fluent dubs in your language — automatically, in minutes
          </p>
          <div className="lang-toggle">
            <div className="lang-tag active">
              <span>🇮🇳</span>
              <select
                className="lang-select"
                value={sourceLang}
                onChange={(e) => setSourceLang(e.target.value)}
                disabled={loading}
              >
                {languages.map((l) => (
                  <option key={l.code} value={l.code}>{l.display_name}</option>
                ))}
              </select>
            </div>
            <div className="toggle-arrow">→</div>
            <div className="lang-tag active">
              <span>🎙️</span>
              <select
                className="lang-select"
                value={targetLang}
                onChange={(e) => setTargetLang(e.target.value)}
                disabled={loading}
              >
                {languages.map((l) => (
                  <option key={l.code} value={l.code}>{l.display_name}</option>
                ))}
              </select>
            </div>
          </div>
        </header>

        {/* INTERFACE CARD */}
        <main className="main-card">
          {!loading && !isDone ? (
            <>
              <div
                className={`drop-zone ${isDragging ? "active" : ""}`}
                onDragOver={(e) => { e.preventDefault(); setIsDragging(true); }}
                onDragLeave={() => setIsDragging(false)}
                onDrop={(e) => { e.preventDefault(); setIsDragging(false); handleFile(e.dataTransfer.files[0]); }}
                onClick={() => fileInput.current.click()}
              >
                <input ref={fileInput} type="file" accept="video/*" hidden onChange={(e) => handleFile(e.target.files[0])} />
                <div className="upload-icon-anim">🎬</div>
                <div className="drop-text">
                  <h2>{file ? "Replace Video Source" : "Initiate Dubbing Source"}</h2>
                  <p>{file ? "Targeting " + file.name : "Drag and drop video frame or click to browse"}</p>
                </div>
              </div>

              {file && (
                <div className="selected-file-card">
                  <div className="file-type-icon">🎞️</div>
                  <div className="file-meta">
                    <h3>{file.name}</h3>
                    <p>{formatSize(file.size)} • Ready for processing</p>
                  </div>
                  <button className="remove-btn" onClick={(e) => { e.stopPropagation(); setFile(null); }}>✕</button>
                </div>
              )}

              {error && <div style={{ color: "#ef4444", fontSize: 13, marginTop: 16, textAlign: "center" }}>⚠️ {error}</div>}

              <button className="btn-start" disabled={!file} onClick={startProcessing}>
                {file
                  ? `GENERATE ${(languages.find((l) => l.code === targetLang)?.display_name || targetLang).toUpperCase()} DUB`
                  : "AWAITING SOURCE FILE"}
              </button>
            </>
          ) : isDone ? (
            <div className="output-section">
              <div className="video-container">
                <video src={outputUrl} controls autoPlay />
              </div>

              <div className="wave-visualizer">
                {[...Array(20)].map((_, i) => (
                  <div key={i} className="wave-bar" style={{ animationDelay: `${i * 0.1}s` }} />
                ))}
              </div>

              <div className="output-actions">
                <a href={outputUrl} download="syncdub_dubbed.mp4" className="control-btn primary">
                  ⬇️ DOWNLOAD DUBBED VIDEO
                </a>
                <button className="control-btn outline" onClick={() => { setIsDone(false); setFile(null); setProgress(0); }}>
                  🆕 NEW PROJECT
                </button>
              </div>
            </div>
          ) : (
            <div className="pipeline-card">
              <div className="progress-section">
                <div className="progress-top">
                  <div className="status-label">{status}</div>
                  <div className="pct-val">{progress}%</div>
                </div>
                <div className="bar-container">
                  <div className="bar-fill" style={{ width: `${progress}%` }} />
                </div>
              </div>

              <div className="pipeline-steps">
                {STEPS.map((step, idx) => (
                  <div key={step.id} className={`step-item ${progress >= step.start ? (progress > step.end ? "done" : "active") : ""}`}>
                    <div className="dot-icon">{progress > step.end ? "✓" : step.icon}</div>
                    <span>{step.label}</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </main>

        <footer style={{ marginTop: 40, color: "var(--text-dim)", fontSize: 12, textAlign: "center", opacity: 0.5 }}>
          Built with Advanced Zero-Shot Voice Cloning & LipSync Neural Networks
        </footer>
      </div>
    </div>
  );
}
