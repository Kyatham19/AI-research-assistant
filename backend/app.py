"""
app.py — Flask API server
Serves React frontend and exposes analysis + workspace endpoints.
"""

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os

from analyzer import analyze_text
from extractors import extract_from_pdf, extract_from_url, search_arxiv
from storage import (
    create_workspace, list_workspaces, load_workspace, delete_workspace,
    save_papers, save_analyses, save_chat_message,
    toggle_favorite, update_last_opened, update_metadata, save_uploaded_file
)

app = Flask(__name__, static_folder='../frontend/dist', static_url_path='')
CORS(app)

# ── Serve React ───────────────────────────────────────────────────────────────
@app.route('/')
def serve():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/<path:path>')
def static_files(path):
    fp = os.path.join(app.static_folder, path)
    if os.path.exists(fp):
        return send_from_directory(app.static_folder, path)
    return send_from_directory(app.static_folder, 'index.html')

# ── Health ────────────────────────────────────────────────────────────────────
@app.route('/health')
def health():
    return jsonify({"status": "ok"})

# ── Workspace API ─────────────────────────────────────────────────────────────
@app.route('/api/workspaces', methods=['GET'])
def get_workspaces():
    return jsonify(list_workspaces())

@app.route('/api/workspaces', methods=['POST'])
def create_new_workspace():
    data = request.get_json()
    query = data.get('query', 'Untitled').strip()
    return jsonify(create_workspace(query)), 201

@app.route('/api/workspaces/<wid>', methods=['GET'])
def get_workspace(wid):
    update_last_opened(wid)
    ws = load_workspace(wid)
    if not ws:
        return jsonify({"error": "Not found"}), 404
    return jsonify(ws)

@app.route('/api/workspaces/<wid>', methods=['DELETE'])
def remove_workspace(wid):
    if not delete_workspace(wid):
        return jsonify({"error": "Not found"}), 404
    return jsonify({"deleted": True})

@app.route('/api/favorite/<wid>', methods=['POST'])
def favorite_workspace(wid):
    return jsonify({"favorite": toggle_favorite(wid)})

@app.route('/api/workspaces/<wid>/chat', methods=['POST'])
def add_chat(wid):
    data = request.get_json()
    role    = data.get('role', 'user')
    content = data.get('content', '').strip()
    if not content:
        return jsonify({"error": "Empty message"}), 400
    return jsonify(save_chat_message(wid, role, content)), 201

# ── Analysis endpoints ────────────────────────────────────────────────────────
@app.route('/analyze/text', methods=['POST'])
def analyze_raw_text():
    data = request.get_json()
    text = data.get('text', '').strip()
    if not text:
        return jsonify({"error": "No text provided"}), 400
    return jsonify(analyze_text(text))

@app.route('/analyze/pdf', methods=['POST'])
def analyze_pdf():
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    file = request.files['file']
    wid  = request.form.get('workspace_id')
    text = extract_from_pdf(file)
    if not text:
        return jsonify({"error": "Could not extract text"}), 400
    result = analyze_text(text)
    result['source'] = file.filename
    if wid:
        file.seek(0)
        save_uploaded_file(wid, file.filename, file.read())
        save_analyses(wid, [result])
        update_metadata(wid, {"mode": "pdf", "query": file.filename})
    return jsonify(result)

@app.route('/analyze/pdfs', methods=['POST'])
def analyze_multiple_pdfs():
    files = request.files.getlist('files')
    wid   = request.form.get('workspace_id')
    if not files:
        return jsonify({"error": "No files uploaded"}), 400
    results, all_text = [], ""
    for file in files:
        text = extract_from_pdf(file)
        if text:
            a = analyze_text(text)
            a['title'] = file.filename
            a['source'] = file.filename
            results.append(a)
            all_text += " " + text
            if wid:
                file.seek(0)
                save_uploaded_file(wid, file.filename, file.read())
    if not results:
        return jsonify({"error": "Could not extract text from any PDF"}), 400
    combined = analyze_text(all_text) if len(results) > 1 else results[0]
    combined['title'] = f"Combined: {len(results)} PDFs"
    if wid:
        save_analyses(wid, results)
    return jsonify({"papers": results, "combined": combined, "paper_count": len(results)})

@app.route('/analyze/url', methods=['POST'])
def analyze_url():
    data = request.get_json()
    url  = data.get('url', '').strip()
    wid  = data.get('workspace_id')
    if not url:
        return jsonify({"error": "No URL provided"}), 400
    text = extract_from_url(url)
    if not text:
        return jsonify({"error": "Could not extract content"}), 400
    result = analyze_text(text)
    result['source'] = url
    if wid:
        save_analyses(wid, [result])
        update_metadata(wid, {"mode": "url", "query": url})
    return jsonify(result)

@app.route('/analyze/topic', methods=['POST'])
def analyze_topic():
    data       = request.get_json()
    topic      = data.get('topic', '').strip()
    max_papers = data.get('max_papers', 5)
    wid        = data.get('workspace_id')
    if not topic:
        return jsonify({"error": "No topic provided"}), 400
    papers = search_arxiv(topic, max_results=max_papers)
    if not papers:
        return jsonify({"error": "No papers found"}), 404
    results = []
    for p in papers:
        a = analyze_text(p['abstract'])
        a.update({"title": p['title'], "authors": p['authors'], "url": p['url'], "published": p['published']})
        results.append(a)
    combined = analyze_text(" ".join([p['abstract'] for p in papers]))
    combined['title'] = f"Combined: {topic}"
    if wid:
        save_papers(wid, papers)
        save_analyses(wid, results)
        update_metadata(wid, {"mode": "topic", "paper_count": len(papers)})
    return jsonify({
        "topic": topic, "paper_count": len(papers),
        "individual_papers": results, "combined_analysis": combined,
        "workspace_id": wid
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)
