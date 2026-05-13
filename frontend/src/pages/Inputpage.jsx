/**
 * InputPage.jsx
 * Creates ONE workspace per search, passes workspace_id up to App.
 * Workspace creation happens here only — never in App.jsx.
 */
import { useState, useRef } from "react";

const API = "";

export default function InputPage({ mode, setMode, onResults, onError, loading, setLoading }) {
  const [topic, setTopic]         = useState("");
  const [maxPapers, setMaxPapers] = useState(5);
  const [url, setUrl]             = useState("");
  const [text, setText]           = useState("");
  const [files, setFiles]         = useState([]);
  const [dragging, setDragging]   = useState(false);
  const fileRef = useRef();

  const addFiles = (newFiles) => {
    const pdfs = Array.from(newFiles).filter(f => f.name.endsWith(".pdf"));
    if (!pdfs.length) { onError("Only PDF files supported."); return; }
    setFiles(prev => {
      const names = new Set(prev.map(f => f.name));
      return [...prev, ...pdfs.filter(f => !names.has(f.name))];
    });
  };

  /** Create exactly ONE workspace and return its id */
  const createWorkspace = async (query) => {
    try {
      const res = await fetch(`${API}/api/workspaces`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query }),
      });
      const ws = await res.json();
      return ws.id || null;
    } catch {
      return null; // non-critical — analysis still proceeds
    }
  };

  const handleSubmit = async () => {
    setLoading(true);
    try {
      let res, data, query = "", wid = null;

      if (mode === "topic") {
        if (!topic.trim()) { onError("Enter a topic."); setLoading(false); return; }
        query = topic.trim();
        wid   = await createWorkspace(query);          // ← ONE workspace created here
        res   = await fetch(`${API}/analyze/topic`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ topic: query, max_papers: maxPapers, workspace_id: wid }),
        });

      } else if (mode === "pdf") {
        if (!files.length) { onError("Upload at least one PDF."); setLoading(false); return; }
        query = files.map(f => f.name).join(", ");
        wid   = await createWorkspace(query);
        const form = new FormData();
        if (files.length === 1) {
          form.append("file", files[0]);
          if (wid) form.append("workspace_id", wid);
          res = await fetch(`${API}/analyze/pdf`, { method: "POST", body: form });
        } else {
          files.forEach(f => form.append("files", f));
          if (wid) form.append("workspace_id", wid);
          res = await fetch(`${API}/analyze/pdfs`, { method: "POST", body: form });
        }

      } else if (mode === "url") {
        if (!url.trim()) { onError("Enter a URL."); setLoading(false); return; }
        query = url.trim();
        wid   = await createWorkspace(query);
        res   = await fetch(`${API}/analyze/url`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ url: query, workspace_id: wid }),
        });

      } else {
        if (!text.trim()) { onError("Paste some text."); setLoading(false); return; }
        query = text.slice(0, 60) + (text.length > 60 ? "..." : "");
        wid   = await createWorkspace(query);
        res   = await fetch(`${API}/analyze/text`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ text: text.trim(), workspace_id: wid }),
        });
      }

      data = await res.json();
      if (!res.ok) { onError(data.error || "Analysis failed."); setLoading(false); return; }

      // Pass results AND workspaceId up — App.jsx does NOT create another workspace
      onResults({ ...data, _mode: mode }, wid);

    } catch {
      onError("Cannot connect to backend. Run: python app.py");
    }
    setLoading(false);
  };

  return (
    <main className="home">
      <div className="home-hero">
        <h1>Analyze Research Papers with AI</h1>
        <p>Search arXiv by topic, upload multiple PDFs, paste a URL, or drop in raw text. Every search is auto-saved.</p>
        <div className="feature-pills">
          {["📊 Multi-paper comparison","🔍 Research gaps","⚠️ Limitations","🚀 Future scope","💾 Saved workspaces","⭐ Favorites"].map(f => (
            <span className="feature-pill" key={f}>{f}</span>
          ))}
        </div>
      </div>

      <div className="input-box">
        <div className="input-tabs">
          {[{id:"topic",icon:"🔍",label:"Topic Search"},{id:"pdf",icon:"📄",label:"PDF Upload"},{id:"url",icon:"🔗",label:"URL"},{id:"text",icon:"✏️",label:"Paste Text"}].map(m => (
            <button key={m.id} className={`input-tab${mode===m.id?" active":""}`} onClick={() => setMode(m.id)}>
              {m.icon} {m.label}
            </button>
          ))}
        </div>

        <div className="input-body">
          {mode === "topic" && (
            <>
              <div className="input-row">
                <input
                  className="input-field"
                  placeholder="e.g. transformer attention, BERT, quantum computing..."
                  value={topic}
                  onChange={e => setTopic(e.target.value)}
                  onKeyDown={e => e.key === "Enter" && handleSubmit()}
                />
                <button className="btn-primary" onClick={handleSubmit} disabled={loading}>
                  {loading ? <><div className="spinner"/>Searching...</> : <>🔍 Search</>}
                </button>
              </div>
              <div className="slider-row">
                <label>Papers to fetch:</label>
                <input type="range" min="1" max="10" value={maxPapers} onChange={e => setMaxPapers(Number(e.target.value))} />
                <span className="slider-val">{maxPapers}</span>
              </div>
            </>
          )}

          {mode === "pdf" && (
            <>
              <div
                className={`drop-zone${dragging ? " drag" : ""}`}
                onDragOver={e => { e.preventDefault(); setDragging(true); }}
                onDragLeave={() => setDragging(false)}
                onDrop={e => { e.preventDefault(); setDragging(false); addFiles(e.dataTransfer.files); }}
                onClick={() => fileRef.current.click()}
              >
                <div className="drop-icon">📄</div>
                <div className="drop-label"><strong>Click or drag & drop</strong> — supports multiple PDFs</div>
              </div>
              <input ref={fileRef} type="file" accept=".pdf" multiple style={{display:"none"}} onChange={e => addFiles(e.target.files)} />
              {files.length > 0 && (
                <div className="file-chips">
                  {files.map(f => (
                    <span className="file-chip" key={f.name}>
                      {f.name}
                      <button onClick={() => setFiles(p => p.filter(x => x.name !== f.name))}>✕</button>
                    </span>
                  ))}
                </div>
              )}
              <button className="btn-primary full" onClick={handleSubmit} disabled={loading}>
                {loading ? <><div className="spinner"/>Analyzing...</> : <>⚡ Analyze {files.length} PDF{files.length !== 1 ? "s" : ""}</>}
              </button>
            </>
          )}

          {mode === "url" && (
            <div className="input-row">
              <input
                className="input-field"
                placeholder="https://arxiv.org/abs/2310.01848"
                value={url}
                onChange={e => setUrl(e.target.value)}
                onKeyDown={e => e.key === "Enter" && handleSubmit()}
              />
              <button className="btn-primary" onClick={handleSubmit} disabled={loading}>
                {loading ? <><div className="spinner"/>Fetching...</> : <>⚡ Analyze</>}
              </button>
            </div>
          )}

          {mode === "text" && (
            <>
              <textarea
                className="input-field"
                placeholder="Paste abstract or paper text here..."
                value={text}
                onChange={e => setText(e.target.value)}
              />
              <button className="btn-primary full" onClick={handleSubmit} disabled={loading}>
                {loading ? <><div className="spinner"/>Analyzing...</> : <>⚡ Analyze Text</>}
              </button>
            </>
          )}
        </div>
      </div>
    </main>
  );
}
