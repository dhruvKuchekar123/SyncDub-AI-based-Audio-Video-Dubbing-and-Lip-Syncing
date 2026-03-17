import React, { useState, useRef } from "react";
import axios from "axios";

const styles = `
  @import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:ital,wght@0,300;0,400;0,500;1,300&display=swap');

  *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

  :root {
    --bg: #0a0a0f;
    --surface: #111118;
    --surface2: #18181f;
    --border: rgba(255,255,255,0.07);
    --accent: #ff5c3a;
    --accent2: #ff8c6b;
    --gold: #f5c842;
    --text: #f0efe8;
    --muted: #6b6a75;
    --success: #3affa0;
    --radius: 16px;
    --font-display: 'Syne', sans-serif;
    --font-body: 'DM Sans', sans-serif;
  }

  body {
    background: var(--bg);
    color: var(--text);
    font-family: var(--font-body);
    min-height: 100vh;
  }

  .app {
    min-height: 100vh;
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 48px 24px 80px;
    position: relative;
    overflow: hidden;
  }

  .app::before {
    content: '';
    position: fixed;
    top: -200px;
    left: 50%;
    transform: translateX(-50%);
    width: 700px;
    height: 500px;
    background: radial-gradient(ellipse, rgba(255,92,58,0.13) 0%, transparent 70%);
    pointer-events: none;
    z-index: 0;
  }

  .app::after {
    content: '';
    position: fixed;
    bottom: -100px;
    right: -100px;
    width: 400px;
    height: 400px;
    background: radial-gradient(ellipse, rgba(245,200,66,0.06) 0%, transparent 70%);
    pointer-events: none;
    z-index: 0;
  }

  .grain {
    position: fixed;
    inset: 0;
    pointer-events: none;
    z-index: 999;
    opacity: 0.022;
    background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noise)'/%3E%3C/svg%3E");
  }

  .header {
    text-align: center;
    margin-bottom: 52px;
    position: relative;
    z-index: 1;
    animation: fadeUp 0.7s ease both;
  }

  .badge {
    display: inline-flex;
    align-items: center;
    gap: 7px;
    background: rgba(255,92,58,0.1);
    border: 1px solid rgba(255,92,58,0.25);
    border-radius: 99px;
    padding: 6px 14px;
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: var(--accent2);
    margin-bottom: 20px;
  }

  .badge-dot {
    width: 6px; height: 6px;
    border-radius: 50%;
    background: var(--accent);
    animation: pulse 2s infinite;
  }

  @keyframes pulse {
    0%, 100% { opacity: 1; transform: scale(1); }
    50% { opacity: 0.5; transform: scale(0.8); }
  }

  h1 {
    font-family: var(--font-display);
    font-size: clamp(36px, 6vw, 60px);
    font-weight: 800;
    letter-spacing: -0.03em;
    line-height: 1.05;
    background: linear-gradient(135deg, #f0efe8 30%, rgba(240,239,232,0.5) 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin-bottom: 14px;
  }

  h1 span {
    background: linear-gradient(135deg, var(--accent) 0%, var(--gold) 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
  }

  .subtitle {
    font-size: 16px;
    color: var(--muted);
    font-weight: 300;
    max-width: 400px;
    line-height: 1.6;
    margin: 0 auto;
  }

  .card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 24px;
    padding: 36px;
    width: 100%;
    max-width: 640px;
    position: relative;
    z-index: 1;
    animation: fadeUp 0.7s 0.15s ease both;
  }

  .card + .card {
    margin-top: 20px;
  }

  @keyframes fadeUp {
    from { opacity: 0; transform: translateY(24px); }
    to { opacity: 1; transform: translateY(0); }
  }

  /* UPLOAD ZONE */
  .upload-zone {
    border: 1.5px dashed rgba(255,255,255,0.12);
    border-radius: var(--radius);
    padding: 40px 24px;
    text-align: center;
    cursor: pointer;
    transition: all 0.25s ease;
    background: var(--surface2);
    position: relative;
    overflow: hidden;
  }

  .upload-zone:hover, .upload-zone.drag-over {
    border-color: var(--accent);
    background: rgba(255,92,58,0.05);
  }

  .upload-zone input {
    position: absolute;
    inset: 0;
    opacity: 0;
    cursor: pointer;
    width: 100%;
    height: 100%;
  }

  .upload-icon {
    width: 52px; height: 52px;
    background: linear-gradient(135deg, rgba(255,92,58,0.15), rgba(245,200,66,0.1));
    border: 1px solid rgba(255,92,58,0.2);
    border-radius: 14px;
    display: flex;
    align-items: center;
    justify-content: center;
    margin: 0 auto 16px;
    font-size: 22px;
    transition: transform 0.25s ease;
  }

  .upload-zone:hover .upload-icon {
    transform: scale(1.08) translateY(-2px);
  }

  .upload-label {
    font-family: var(--font-display);
    font-size: 15px;
    font-weight: 600;
    margin-bottom: 6px;
    color: var(--text);
  }

  .upload-hint {
    font-size: 13px;
    color: var(--muted);
  }

  .file-selected {
    margin-top: 16px;
    display: flex;
    align-items: center;
    gap: 10px;
    background: rgba(58,255,160,0.07);
    border: 1px solid rgba(58,255,160,0.2);
    border-radius: 10px;
    padding: 10px 14px;
    animation: fadeIn 0.3s ease;
  }

  @keyframes fadeIn {
    from { opacity: 0; transform: scale(0.97); }
    to { opacity: 1; transform: scale(1); }
  }

  .file-icon {
    font-size: 18px;
  }

  .file-info { flex: 1; text-align: left; }
  .file-name {
    font-size: 13px;
    font-weight: 500;
    color: var(--success);
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    max-width: 300px;
  }
  .file-size { font-size: 11px; color: var(--muted); margin-top: 1px; }

  .file-remove {
    background: none;
    border: none;
    color: var(--muted);
    cursor: pointer;
    font-size: 16px;
    padding: 2px 6px;
    border-radius: 6px;
    transition: color 0.2s, background 0.2s;
  }
  .file-remove:hover { color: var(--accent); background: rgba(255,92,58,0.1); }

  /* ACTIONS */
  .actions {
    display: flex;
    gap: 12px;
    margin-top: 24px;
  }

  .btn {
    flex: 1;
    padding: 14px 20px;
    border: none;
    border-radius: 12px;
    font-family: var(--font-display);
    font-size: 14px;
    font-weight: 700;
    letter-spacing: 0.02em;
    cursor: pointer;
    transition: all 0.2s ease;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
    position: relative;
    overflow: hidden;
  }

  .btn::before {
    content: '';
    position: absolute;
    inset: 0;
    background: linear-gradient(135deg, rgba(255,255,255,0.1) 0%, transparent 60%);
    opacity: 0;
    transition: opacity 0.2s;
  }

  .btn:hover::before { opacity: 1; }

  .btn-primary {
    background: linear-gradient(135deg, var(--accent) 0%, #ff3d1a 100%);
    color: white;
    box-shadow: 0 4px 24px rgba(255,92,58,0.35);
  }

  .btn-primary:hover:not(:disabled) {
    transform: translateY(-2px);
    box-shadow: 0 8px 32px rgba(255,92,58,0.45);
  }

  .btn-primary:active:not(:disabled) { transform: translateY(0); }

  .btn-primary:disabled {
    opacity: 0.6;
    cursor: not-allowed;
    box-shadow: none;
  }

  .btn-secondary {
    background: var(--surface2);
    border: 1px solid var(--border);
    color: var(--text);
  }

  .btn-secondary:hover { border-color: rgba(255,255,255,0.15); background: rgba(255,255,255,0.04); }
  .btn-secondary:disabled { opacity: 0.4; cursor: not-allowed; }

  .btn-download {
    background: linear-gradient(135deg, var(--success) 0%, #00d47a 100%);
    color: #0a1a10;
    box-shadow: 0 4px 24px rgba(58,255,160,0.25);
  }

  .btn-download:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 32px rgba(58,255,160,0.35);
  }

  /* SPINNER */
  .spinner {
    width: 16px; height: 16px;
    border: 2px solid rgba(255,255,255,0.3);
    border-top-color: white;
    border-radius: 50%;
    animation: spin 0.7s linear infinite;
    flex-shrink: 0;
  }

  @keyframes spin { to { transform: rotate(360deg); } }

  /* ERROR */
  .error-msg {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-top: 14px;
    padding: 12px 14px;
    background: rgba(255,92,58,0.08);
    border: 1px solid rgba(255,92,58,0.2);
    border-radius: 10px;
    color: var(--accent2);
    font-size: 13px;
    animation: fadeIn 0.3s ease;
  }

  /* PROGRESS CARD */
  .progress-card {
    animation: fadeUp 0.4s ease both;
  }

  .progress-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 20px;
  }

  .progress-label {
    font-family: var(--font-display);
    font-size: 13px;
    font-weight: 700;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: var(--muted);
  }

  .progress-status {
    display: flex;
    align-items: center;
    gap: 7px;
    font-size: 13px;
    color: var(--text);
    font-weight: 500;
  }

  .status-dot {
    width: 7px; height: 7px;
    border-radius: 50%;
    background: var(--accent);
    animation: pulse 1.5s infinite;
    flex-shrink: 0;
  }

  .status-dot.done { background: var(--success); animation: none; }

  .progress-track {
    height: 6px;
    background: var(--surface2);
    border-radius: 99px;
    overflow: hidden;
    position: relative;
    border: 1px solid var(--border);
  }

  .progress-fill {
    height: 100%;
    border-radius: 99px;
    background: linear-gradient(90deg, var(--accent) 0%, var(--gold) 100%);
    transition: width 0.5s cubic-bezier(0.25, 1, 0.5, 1);
    position: relative;
    box-shadow: 0 0 12px rgba(255,92,58,0.5);
  }

  .progress-fill::after {
    content: '';
    position: absolute;
    right: 0; top: 0; bottom: 0;
    width: 30px;
    background: linear-gradient(90deg, transparent, rgba(255,255,255,0.3));
    animation: shimmer 1.5s infinite;
  }

  @keyframes shimmer {
    0% { opacity: 0; }
    50% { opacity: 1; }
    100% { opacity: 0; }
  }

  .progress-fill.done {
    background: linear-gradient(90deg, var(--success), #00e088);
    box-shadow: 0 0 12px rgba(58,255,160,0.5);
  }

  .progress-fill.done::after { display: none; }

  .progress-numbers {
    display: flex;
    justify-content: space-between;
    margin-top: 10px;
  }

  .progress-pct {
    font-family: var(--font-display);
    font-size: 28px;
    font-weight: 800;
    background: linear-gradient(135deg, var(--accent), var(--gold));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    line-height: 1;
    transition: all 0.3s;
  }

  .progress-pct.done {
    background: linear-gradient(135deg, var(--success), #00d47a);
    -webkit-background-clip: text;
    background-clip: text;
  }

  .steps {
    margin-top: 18px;
    display: flex;
    flex-direction: column;
    gap: 8px;
  }

  .step {
    display: flex;
    align-items: center;
    gap: 10px;
    font-size: 13px;
    color: var(--muted);
    transition: color 0.3s;
  }

  .step.active { color: var(--text); }
  .step.done-step { color: var(--success); }

  .step-icon {
    width: 20px; height: 20px;
    border-radius: 50%;
    background: var(--surface2);
    border: 1px solid var(--border);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 10px;
    flex-shrink: 0;
    transition: all 0.3s;
  }

  .step.active .step-icon {
    background: rgba(255,92,58,0.15);
    border-color: var(--accent);
    color: var(--accent);
  }

  .step.done-step .step-icon {
    background: rgba(58,255,160,0.15);
    border-color: var(--success);
    color: var(--success);
  }

  /* OUTPUT CARD */
  .output-card {
    animation: fadeUp 0.5s ease both;
  }

  .output-header {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 20px;
  }

  .output-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: rgba(58,255,160,0.1);
    border: 1px solid rgba(58,255,160,0.2);
    border-radius: 99px;
    padding: 4px 12px;
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: var(--success);
  }

  .output-title {
    font-family: var(--font-display);
    font-size: 20px;
    font-weight: 700;
  }

  .video-wrapper {
    border-radius: var(--radius);
    overflow: hidden;
    background: #000;
    border: 1px solid var(--border);
    position: relative;
  }

  .video-wrapper video {
    width: 100%;
    display: block;
  }

  .video-actions {
    margin-top: 16px;
    display: flex;
    gap: 10px;
  }

  /* LANG CHIPS */
  .lang-row {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-top: 16px;
    justify-content: center;
  }

  .lang-chip {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 5px 12px;
    border-radius: 99px;
    font-size: 12px;
    font-weight: 600;
    border: 1px solid var(--border);
    color: var(--muted);
  }

  .lang-chip.active {
    background: rgba(255,92,58,0.1);
    border-color: rgba(255,92,58,0.3);
    color: var(--accent2);
  }

  .lang-arrow { color: var(--muted); font-size: 16px; }

  /* DIVIDER */
  .section-divider {
    width: 100%;
    max-width: 640px;
    height: 1px;
    background: var(--border);
    margin: 0;
    position: relative;
    z-index: 1;
  }
`;

function formatBytes(bytes) {
  if (!bytes) return "";
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(0)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

const PROCESSING_STEPS = [
  { label: "Uploading video", threshold: 10 },
  { label: "Extracting audio track", threshold: 25 },
  { label: "Transcribing Hindi speech", threshold: 50 },
  { label: "Translating to Marathi", threshold: 70 },
  { label: "Synthesizing dubbed audio", threshold: 85 },
  { label: "Merging audio and video", threshold: 95 },
  { label: "Finalizing output", threshold: 100 },
];

export default function App() {
  const [video, setVideo] = useState(null);
  const [dragOver, setDragOver] = useState(false);
  const [progress, setProgress] = useState(0);
  const [status, setStatus] = useState("");
  const [outputVideo, setOutputVideo] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [done, setDone] = useState(false);
  const fileInputRef = useRef();

  const handleFile = (file) => {
    if (file && file.type.startsWith("video/")) {
      setVideo(file);
      setError("");
    } else {
      setError("Please select a valid video file.");
    }
  };

  const uploadVideo = async () => {
    if (!video) { setError("Please select a video first."); return; }
    setError(""); setLoading(true); setDone(false);
    setStatus("Uploading video..."); setProgress(0);
    try {
      const formData = new FormData();
      formData.append("file", video);
      await axios.post("http://127.0.0.1:8000/upload-video/", formData, {
        headers: { "Content-Type": "multipart/form-data" }
      });
      checkProgress();
    } catch {
      setError("Upload failed. Please check your connection and try again.");
      setLoading(false);
    }
  };

  const checkProgress = () => {
    const interval = setInterval(async () => {
      try {
        const res = await axios.get("http://127.0.0.1:8000/progress");
        setProgress(res.data.progress);
        setStatus(res.data.status);
        if (res.data.progress === 100) {
          clearInterval(interval);
          const videoRes = await axios.get("http://127.0.0.1:8000/video");
          setOutputVideo("http://127.0.0.1:8000" + videoRes.data.video_url);
          setLoading(false);
          setDone(true);
          setStatus("Processing Complete");
        }
      } catch {
        clearInterval(interval);
        setError("Error fetching progress. Please try again.");
        setLoading(false);
      }
    }, 2000);
  };

  const activeStep = PROCESSING_STEPS.filter(s => progress >= s.threshold).length - 1;

  const handleDownload = () => {
    if (!outputVideo) return;
    const a = document.createElement("a");
    a.href = outputVideo;
    a.download = "syncdub_output.mp4";
    a.click();
  };

  return (
    <>
      <style>{styles}</style>
      <div className="grain" />
      <div className="app">

        {/* HEADER */}
        <header className="header">
          <div className="badge">
            <span className="badge-dot" />
            AI-Powered Dubbing
          </div>
          <h1>Sync<span>Dub</span></h1>
          <p className="subtitle">
            Transform Hindi videos into fluent Marathi dubs — automatically, in minutes.
          </p>
          <div className="lang-row">
            <span className="lang-chip active">🇮🇳 Hindi</span>
            <span className="lang-arrow">→</span>
            <span className="lang-chip active">🎙️ Marathi</span>
          </div>
        </header>

        {/* UPLOAD CARD */}
        <div className="card">
          <div
            className={`upload-zone${dragOver ? " drag-over" : ""}`}
            onDragOver={e => { e.preventDefault(); setDragOver(true); }}
            onDragLeave={() => setDragOver(false)}
            onDrop={e => { e.preventDefault(); setDragOver(false); handleFile(e.dataTransfer.files[0]); }}
          >
            <input
              ref={fileInputRef}
              type="file"
              accept="video/*"
              onChange={e => handleFile(e.target.files[0])}
            />
            <div className="upload-icon">🎬</div>
            <div className="upload-label">
              {video ? "Change video" : "Drop your video here"}
            </div>
            <div className="upload-hint">
              {video ? "Click to replace" : "or click to browse · MP4, MOV, AVI supported"}
            </div>
          </div>

          {video && (
            <div className="file-selected">
              <span className="file-icon">🎞️</span>
              <div className="file-info">
                <div className="file-name">{video.name}</div>
                <div className="file-size">{formatBytes(video.size)}</div>
              </div>
              <button className="file-remove" onClick={() => { setVideo(null); setOutputVideo(""); setDone(false); setProgress(0); }}>✕</button>
            </div>
          )}

          {error && (
            <div className="error-msg">
              <span>⚠️</span> {error}
            </div>
          )}

          <div className="actions">
            <button
              className="btn btn-primary"
              onClick={uploadVideo}
              disabled={loading || !video}
            >
              {loading ? <><span className="spinner" /> Processing...</> : <><span>🎙️</span> Start Dubbing</>}
            </button>
          </div>
        </div>

        {/* PROGRESS CARD */}
        {(loading || done) && (
          <div className="card progress-card">
            <div className="progress-header">
              <span className="progress-label">Progress</span>
              <div className="progress-status">
                <span className={`status-dot${done ? " done" : ""}`} />
                {status || "Processing..."}
              </div>
            </div>

            <div className="progress-track">
              <div
                className={`progress-fill${done ? " done" : ""}`}
                style={{ width: `${progress}%` }}
              />
            </div>

            <div className="progress-numbers">
              <span className={`progress-pct${done ? " done" : ""}`}>{progress}%</span>
              <span style={{ fontSize: 12, color: "var(--muted)", alignSelf: "flex-end", marginBottom: 2 }}>
                {done ? "Complete ✓" : "Estimated: ~2–3 min"}
              </span>
            </div>

            <div className="steps">
              {PROCESSING_STEPS.map((step, i) => (
                <div
                  key={i}
                  className={`step${i === activeStep && !done ? " active" : ""}${progress >= step.threshold ? " done-step" : ""}`}
                >
                  <div className="step-icon">
                    {progress >= step.threshold ? "✓" : i + 1}
                  </div>
                  {step.label}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* OUTPUT CARD */}
        {outputVideo && (
          <div className="card output-card">
            <div className="output-header">
              <div>
                <div className="output-badge">✓ Dubbed Output</div>
                <div className="output-title" style={{ marginTop: 8 }}>Your Marathi Video</div>
              </div>
            </div>

            <div className="video-wrapper">
              <video controls>
                <source src={outputVideo} type="video/mp4" />
              </video>
            </div>

            <div className="video-actions">
              <button className="btn btn-download" onClick={handleDownload}>
                <span>⬇</span> Download Video
              </button>
              <button
                className="btn btn-secondary"
                onClick={() => {
                  setVideo(null); setOutputVideo(""); setDone(false);
                  setProgress(0); setStatus(""); setLoading(false);
                }}
              >
                <span>↺</span> New Video
              </button>
            </div>
          </div>
        )}

      </div>
    </>
  );
}
