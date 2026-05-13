import { useState } from "react";

/* ── helpers ── */
function Section({ icon, title, color, count, children, defaultOpen = true }) {
  const [open, setOpen] = useState(defaultOpen);
  return (
    <div className="section-card">
      <div className="section-head" onClick={() => setOpen(!open)}>
        <div className="section-icon" style={{ background:`${color}18`, color }}>{icon}</div>
        <h3>{title}</h3>
        {count != null && <span className="section-count">{count}</span>}
        <span className={`section-toggle${open?" open":""}`}>▼</span>
      </div>
      {open && <div className="section-body">{children}</div>}
    </div>
  );
}

function Badge({ type, label }) {
  return <span className={`badge ${type}`}>{label}</span>;
}

function hasMeaningful(arr) {
  return arr && arr.length > 0 && !arr[0].includes("No explicit");
}

/* ── single paper analysis ── */
function SingleAnalysis({ data }) {
  const s = data.stats || {};
  return (
    <>
      <div className="stats-row">
        <div className="stat-card"><span className="stat-num">{(s.word_count||0).toLocaleString()}</span><span className="stat-label">Words</span></div>
        <div className="stat-card"><span className="stat-num">{s.sentence_count||0}</span><span className="stat-label">Sentences</span></div>
        <div className="stat-card"><span className="stat-num">{s.unique_words||0}</span><span className="stat-label">Unique words</span></div>
        <div className="stat-card"><span className="stat-num">{s.avg_sentence_length||0}</span><span className="stat-label">Avg sent. len</span></div>
      </div>

      <div className="analysis-grid">
        <div className="full">
          <Section icon="📋" title="Summary" color="#6366f1" count={null}>
            <p className="summary-text">{data.summary || "No summary available."}</p>
          </Section>
        </div>

        <Section icon="🔑" title="Keywords" color="#818cf8" count={(data.keywords||[]).length}>
          <div className="keyword-cloud">
            {(data.keywords||[]).map((kw,i) => (
              <span className="kw-tag" key={i}>{kw.term}<span className="kw-score">{kw.score}</span></span>
            ))}
          </div>
        </Section>

        <Section icon="⚙️" title="Methods" color="#14b8a6" count={(data.methods||[]).filter(m=>m!=="No specific methods detected").length} defaultOpen={false}>
          <div className="method-pills">
            {(data.methods||[]).map((m,i) => <span className="method-pill" key={i}>{m}</span>)}
          </div>
        </Section>

        <Section icon="💡" title="Contributions" color="#22c55e" count={hasMeaningful(data.contributions)?(data.contributions||[]).length:0} defaultOpen={false}>
          <ul className="result-list contrib">
            {(data.contributions||[]).map((c,i) => <li key={i}>{c}</li>)}
          </ul>
        </Section>

        <Section icon="⭐" title="Key Sentences" color="#a855f7" count={(data.important_sentences||[]).length} defaultOpen={false}>
          <ul className="result-list">
            {(data.important_sentences||[]).map((s,i) => <li key={i}>{s}</li>)}
          </ul>
        </Section>

        <Section icon="🔍" title="Research Gaps" color="#f59e0b" count={hasMeaningful(data.research_gaps)?(data.research_gaps||[]).length:0} defaultOpen={true}>
          <ul className="result-list gaps">
            {(data.research_gaps||[]).map((g,i) => <li key={i}>{g}</li>)}
          </ul>
        </Section>

        <Section icon="⚠️" title="Limitations" color="#ef4444" count={hasMeaningful(data.limitations)?(data.limitations||[]).length:0} defaultOpen={true}>
          <ul className="result-list limits">
            {(data.limitations||[]).map((l,i) => <li key={i}>{l}</li>)}
          </ul>
        </Section>

        <div className="full">
          <Section icon="🚀" title="Future Scope" color="#0ea5e9" count={hasMeaningful(data.future_scope)?(data.future_scope||[]).length:0} defaultOpen={true}>
            <ul className="result-list future">
              {(data.future_scope||[]).map((f,i) => <li key={i}>{f}</li>)}
            </ul>
          </Section>
        </div>
      </div>
    </>
  );
}

/* ── comparison table ── */
function CompareView({ papers }) {
  return (
    <div className="section-card">
      <div className="section-head" style={{cursor:"default"}}>
        <div className="section-icon" style={{background:"rgba(99,102,241,0.1)",color:"#6366f1"}}>🆚</div>
        <h3>Side-by-side Comparison — {papers.length} papers</h3>
      </div>
      <div className="section-body">
        <div className="compare-wrap">
          <table className="compare-table">
            <thead>
              <tr>
                <th>#</th>
                <th>Title</th>
                <th>Authors</th>
                <th>Year</th>
                <th>Top Keywords</th>
                <th>Methods</th>
                <th>Research Gaps</th>
                <th>Limitations</th>
                <th>Future Scope</th>
                <th>Link</th>
              </tr>
            </thead>
            <tbody>
              {papers.map((p,i) => (
                <tr key={i}>
                  <td className="ct-num">{i+1}</td>
                  <td className="ct-title">{p.title}</td>
                  <td className="ct-author">{(p.authors||[]).slice(0,2).join(", ")}{(p.authors||[]).length>2?" et al.":""}</td>
                  <td className="ct-date">{p.published?.slice(0,4)||"—"}</td>
                  <td><div className="mini-pills">{(p.keywords||[]).slice(0,3).map((k,j)=><span className="mini-pill" key={j}>{k.term}</span>)}</div></td>
                  <td><div className="mini-pills">{(p.methods||[]).slice(0,2).filter(m=>m!=="No specific methods detected").map((m,j)=><span className="mini-pill teal" key={j}>{m}</span>)}</div></td>
                  <td className="ct-center">{hasMeaningful(p.research_gaps)?<Badge type="yes" label="✓ Yes"/>:<Badge type="no" label="No"/>}</td>
                  <td className="ct-center">{hasMeaningful(p.limitations)?<Badge type="warn" label="✓ Yes"/>:<Badge type="no" label="No"/>}</td>
                  <td className="ct-center">{hasMeaningful(p.future_scope)?<Badge type="sky" label="✓ Yes"/>:<Badge type="no" label="No"/>}</td>
                  <td>{p.url&&<a className="paper-link" href={p.url} target="_blank" rel="noreferrer">arXiv ↗</a>}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

/* ── individual papers ── */
function PapersView({ papers }) {
  const [expanded, setExpanded] = useState({});
  const toggle = (i) => setExpanded(p => ({...p, [i]: !p[i]}));

  return (
    <div className="papers-list">
      {papers.map((p,i) => (
        <div className="paper-card" key={i}>
          <div className="paper-header">
            <div className="paper-num">{i+1}</div>
            <div className="paper-title">{p.title}</div>
          </div>
          <div className="paper-meta">
            {(p.authors||[]).slice(0,4).join(", ")}{(p.authors||[]).length>4?" et al.":""} · {p.published}
          </div>
          <p className="paper-summary">{p.summary}</p>
          <div className="paper-tags">
            {hasMeaningful(p.research_gaps) && <Badge type="yes" label="🔍 Has research gaps"/>}
            {hasMeaningful(p.limitations)    && <Badge type="warn" label="⚠️ Has limitations"/>}
            {hasMeaningful(p.future_scope)   && <Badge type="sky" label="🚀 Future scope"/>}
          </div>
          <div className="keyword-cloud" style={{marginBottom:8}}>
            {(p.keywords||[]).slice(0,6).map((kw,j) => <span className="kw-tag" key={j} style={{fontSize:11}}>{kw.term}</span>)}
          </div>

          <button className="expand-btn" onClick={() => toggle(i)}>
            {expanded[i] ? "▲ Hide details" : "▼ Show gaps, limitations & future scope"}
          </button>

          {expanded[i] && (
            <div className="paper-details">
              <div className="paper-details-grid">
                <div className="detail-block">
                  <div className="detail-label" style={{color:"#f59e0b"}}>🔍 Research Gaps</div>
                  <div className="detail-items">
                    {(p.research_gaps||[]).map((g,j) => <div className="detail-item" key={j}>{g}</div>)}
                  </div>
                </div>
                <div className="detail-block">
                  <div className="detail-label" style={{color:"#ef4444"}}>⚠️ Limitations</div>
                  <div className="detail-items">
                    {(p.limitations||[]).map((l,j) => <div className="detail-item" key={j}>{l}</div>)}
                  </div>
                </div>
                <div className="detail-block">
                  <div className="detail-label" style={{color:"#0ea5e9"}}>🚀 Future Scope</div>
                  <div className="detail-items">
                    {(p.future_scope||[]).map((f,j) => <div className="detail-item" key={j}>{f}</div>)}
                  </div>
                </div>
                <div className="detail-block">
                  <div className="detail-label" style={{color:"#14b8a6"}}>⚙️ Methods</div>
                  <div className="method-pills" style={{flexWrap:"wrap"}}>
                    {(p.methods||[]).map((m,j) => <span className="method-pill" key={j}>{m}</span>)}
                  </div>
                </div>
              </div>
            </div>
          )}

          {p.url && <a className="paper-link" href={p.url} target="_blank" rel="noreferrer" style={{marginTop:8,display:"inline-flex"}}>View on arXiv ↗</a>}
        </div>
      ))}
    </div>
  );
}

/* ── main results page ── */
export default function ResultsPage({ results, mode, onBack }) {
  const isTopic = mode === "topic";
  const isMultiPDF = Array.isArray(results.papers);
  const isMulti = isTopic || isMultiPDF;

  const papers = isTopic ? (results.individual_papers||[]) : (isMultiPDF ? results.papers : []);
  const combined = isTopic ? results.combined_analysis : (isMultiPDF ? results.combined : null);

  const VIEWS = isMulti
    ? [{id:"combined",icon:"📊",label:"Combined"},{id:"compare",icon:"🆚",label:"Compare"},{id:"papers",icon:"📚",label:`Papers (${papers.length})`}]
    : [];

  const [view, setView] = useState("combined");

  const title = results.topic ? `"${results.topic}"` : results.source || results.title || "Analysis";

  return (
    <div className="results-page">
      <div className="results-toolbar">
        <div className="results-title-bar">
          <div className="results-label">{isTopic ? "Topic Search" : isMultiPDF ? "Multi-PDF" : mode.toUpperCase()} · {isTopic ? `${papers.length} papers` : "Analysis"}</div>
          <div className="results-title">{title}</div>
        </div>

        {isMulti && (
          <div className="view-tabs">
            {VIEWS.map(v => (
              <button key={v.id} className={`view-tab${view===v.id?" active":""}`} onClick={() => setView(v.id)}>
                {v.icon} {v.label}
              </button>
            ))}
          </div>
        )}

        <button className="btn-outline" onClick={onBack}>← New Search</button>
      </div>

      <div className="results-body">
        {!isMulti && <SingleAnalysis data={results} />}
        {isMulti && view === "combined"  && <SingleAnalysis data={combined || results} />}
        {isMulti && view === "compare"   && <CompareView papers={papers} />}
        {isMulti && view === "papers"    && <PapersView papers={papers} />}
      </div>
    </div>
  );
}
