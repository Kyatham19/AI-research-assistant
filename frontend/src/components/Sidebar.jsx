/**
 * Sidebar.jsx
 * Persistent workspace sidebar — shows recent searches and favorites.
 * Mirrors the ChatGPT conversation list pattern.
 */
import { useState, useEffect } from "react";

const API = "";

export default function Sidebar({ currentId, onSelect, onNew, refreshTrigger }) {
  const [workspaces, setWorkspaces] = useState([]);
  const [loading, setLoading]       = useState(true);
  const [collapsed, setCollapsed]   = useState(false);

  // Fetch workspace list whenever refreshTrigger changes
  useEffect(() => {
    fetchWorkspaces();
  }, [refreshTrigger]);

  const fetchWorkspaces = async () => {
    try {
      const res  = await fetch(`${API}/api/workspaces`);
      const data = await res.json();
      setWorkspaces(Array.isArray(data) ? data : []);
    } catch {
      setWorkspaces([]);
    } finally {
      setLoading(false);
    }
  };

  const handleFavorite = async (e, id) => {
    e.stopPropagation();
    await fetch(`${API}/api/favorite/${id}`, { method: "POST" });
    fetchWorkspaces(); // refresh list
  };

  const handleDelete = async (e, id) => {
    e.stopPropagation();
    if (!confirm("Delete this workspace?")) return;
    await fetch(`${API}/api/workspaces/${id}`, { method: "DELETE" });
    fetchWorkspaces();
    if (currentId === id) onNew(); // go home if deleted current
  };

  const formatTime = (iso) => {
    if (!iso) return "";
    const d = new Date(iso);
    const now = new Date();
    const diff = now - d;
    if (diff < 60000)   return "Just now";
    if (diff < 3600000) return `${Math.floor(diff/60000)}m ago`;
    if (diff < 86400000) return `${Math.floor(diff/3600000)}h ago`;
    return d.toLocaleDateString();
  };

  const favorites = workspaces.filter(w => w.favorite);
  const recent    = workspaces.filter(w => !w.favorite);

  const modeIcon = (mode) => ({ topic: "🔍", pdf: "📄", url: "🔗", text: "✏️" }[mode] || "🔍");

  if (collapsed) return (
    <div className="sidebar sidebar-collapsed">
      <button className="sidebar-toggle" onClick={() => setCollapsed(false)} title="Expand sidebar">
        ☰
      </button>
    </div>
  );

  return (
    <aside className="sidebar">
      {/* Header */}
      <div className="sidebar-header">
        <span className="sidebar-title">Workspaces</span>
        <button className="sidebar-toggle" onClick={() => setCollapsed(true)} title="Collapse">✕</button>
      </div>

      {/* New search button */}
      <div className="sidebar-new">
        <button className="btn-new-search" onClick={onNew}>
          <span>+</span> New Search
        </button>
      </div>

      <div className="sidebar-body">
        {loading && <div className="sidebar-empty">Loading...</div>}

        {/* Favorites section */}
        {favorites.length > 0 && (
          <div className="sidebar-section">
            <div className="sidebar-section-label">⭐ Favorites</div>
            {favorites.map(ws => (
              <WorkspaceItem
                key={ws.id} ws={ws} active={currentId === ws.id}
                onSelect={() => onSelect(ws.id)}
                onFavorite={(e) => handleFavorite(e, ws.id)}
                onDelete={(e) => handleDelete(e, ws.id)}
                formatTime={formatTime} modeIcon={modeIcon}
              />
            ))}
          </div>
        )}

        {/* Recent section */}
        {recent.length > 0 && (
          <div className="sidebar-section">
            <div className="sidebar-section-label">🕐 Recent</div>
            {recent.map(ws => (
              <WorkspaceItem
                key={ws.id} ws={ws} active={currentId === ws.id}
                onSelect={() => onSelect(ws.id)}
                onFavorite={(e) => handleFavorite(e, ws.id)}
                onDelete={(e) => handleDelete(e, ws.id)}
                formatTime={formatTime} modeIcon={modeIcon}
              />
            ))}
          </div>
        )}

        {!loading && workspaces.length === 0 && (
          <div className="sidebar-empty">
            <div style={{fontSize:28,marginBottom:8}}>🔬</div>
            <div>No searches yet.</div>
            <div style={{fontSize:11,marginTop:4,color:"var(--text3)"}}>Start a new search above.</div>
          </div>
        )}
      </div>
    </aside>
  );
}

function WorkspaceItem({ ws, active, onSelect, onFavorite, onDelete, formatTime, modeIcon }) {
  return (
    <div className={`ws-item${active ? " active" : ""}`} onClick={onSelect}>
      <span className="ws-icon">{modeIcon(ws.mode)}</span>
      <div className="ws-info">
        <div className="ws-query">{ws.query}</div>
        <div className="ws-meta">
          {ws.paper_count > 0 && <span>{ws.paper_count} papers · </span>}
          <span>{formatTime(ws.last_opened)}</span>
        </div>
      </div>
      <div className="ws-actions">
        <button
          className={`ws-btn${ws.favorite ? " starred" : ""}`}
          onClick={onFavorite} title={ws.favorite ? "Unstar" : "Star"}
        >★</button>
        <button className="ws-btn ws-btn-del" onClick={onDelete} title="Delete">✕</button>
      </div>
    </div>
  );
}
