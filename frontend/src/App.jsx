/**
 * App.jsx — Root component
 * Workspace is created ONLY in InputPage, never here.
 * handleResults just stores the data and refreshes sidebar.
 */
import { useState, useCallback } from "react";
import Sidebar from "./components/Sidebar";
import InputPage from "./pages/InputPage";
import ResultsPage from "./pages/ResultsPage";
import "./App.css";

const API = "";

export default function App() {
  const [results, setResults]                       = useState(null);
  const [mode, setMode]                             = useState("topic");
  const [error, setError]                           = useState(null);
  const [loading, setLoading]                       = useState(false);
  const [currentWorkspaceId, setCurrentWorkspaceId] = useState(null);
  const [sidebarRefresh, setSidebarRefresh]         = useState(0);

  const refreshSidebar = useCallback(() => setSidebarRefresh(n => n + 1), []);

  // Called when analysis completes — workspace already created in InputPage
  const handleResults = (data, workspaceId) => {
    setResults(data);
    setError(null);
    if (workspaceId) {
      setCurrentWorkspaceId(workspaceId);
      refreshSidebar();
    }
  };

  // Load a saved workspace from sidebar click
  const handleSelectWorkspace = async (id) => {
    try {
      const res  = await fetch(`${API}/api/workspaces/${id}`);
      const data = await res.json();
      if (data.error) { setError(data.error); return; }

      setCurrentWorkspaceId(id);
      const ws = data;

      if (ws.metadata.mode === "topic" && ws.analyses.length > 0) {
        setMode("topic");
        setResults({
          _mode: "topic",
          _input: ws.metadata.query,
          topic: ws.metadata.query,
          paper_count: ws.papers.length,
          individual_papers: ws.analyses,
          combined_analysis: ws.analyses[0] || {},
          workspace_id: id,
        });
      } else if (ws.analyses.length > 0) {
        setMode(ws.metadata.mode || "text");
        setResults({
          ...ws.analyses[0],
          _mode: ws.metadata.mode,
          _input: ws.metadata.query,
          workspace_id: id,
        });
      }
    } catch {
      setError("Failed to load workspace.");
    }
  };

  const handleNew = () => {
    setResults(null);
    setCurrentWorkspaceId(null);
    setError(null);
  };

  return (
    <div className="app">
      <header className="header">
        <div className="logo">
          <div className="logo-icon">🔬</div>
          <span className="logo-name">Research<span>AI</span></span>
        </div>
        <div className="header-right">
          <span className="header-badge">NLP · arXiv · Workspaces</span>
        </div>
      </header>

      <div className="app-body">
        <Sidebar
          currentId={currentWorkspaceId}
          onSelect={handleSelectWorkspace}
          onNew={handleNew}
          refreshTrigger={sidebarRefresh}
        />

        <div className="main-content">
          {results ? (
            <ResultsPage
              results={results} mode={mode}
              workspaceId={currentWorkspaceId}
              onBack={handleNew}
            />
          ) : (
            <InputPage
              mode={mode} setMode={setMode}
              onResults={handleResults}
              onError={setError}
              loading={loading} setLoading={setLoading}
            />
          )}
        </div>
      </div>

      {error && (
        <div className="error-toast">
          <span>⚠ {error}</span>
          <button onClick={() => setError(null)}>✕</button>
        </div>
      )}
    </div>
  );
}
