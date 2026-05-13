import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
import re
import io
import ssl

# SSL context that works on all platforms
SSL_CTX = ssl.create_default_context()

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
}


def extract_from_pdf(file_obj):
    """Extract text from uploaded PDF using PyMuPDF (fitz)"""
    try:
        import fitz
        file_bytes = file_obj.read()
        doc = fitz.open(stream=file_bytes, filetype="pdf")
        text = ""
        for page in doc:
            text += page.get_text()
        doc.close()
        return clean_extracted(text)
    except ImportError:
        try:
            from pdfminer.high_level import extract_text_to_fp
            from pdfminer.layout import LAParams
            file_obj.seek(0)
            output = io.StringIO()
            extract_text_to_fp(file_obj, output, laparams=LAParams())
            return clean_extracted(output.getvalue())
        except Exception as e:
            print(f"PDF extraction error: {e}")
            return None
    except Exception as e:
        print(f"PDF extraction error: {e}")
        return None


def extract_from_url(url):
    """Extract text from a URL (supports arXiv abstract pages)"""
    try:
        if 'arxiv.org/pdf' in url:
            url = url.replace('/pdf/', '/abs/').replace('.pdf', '')

        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=15, context=SSL_CTX) as response:
            html = response.read().decode('utf-8', errors='ignore')

        html = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL)
        html = re.sub(r'<style[^>]*>.*?</style>', '', html, flags=re.DOTALL)

        if 'arxiv.org' in url:
            abstract_match = re.search(
                r'<blockquote[^>]*class="abstract"[^>]*>(.*?)</blockquote>',
                html, re.DOTALL
            )
            if abstract_match:
                text = abstract_match.group(1)
                text = re.sub(r'<[^>]+>', ' ', text)
                return clean_extracted(text)

        text = re.sub(r'<[^>]+>', ' ', html)
        return clean_extracted(text)

    except Exception as e:
        print(f"URL extraction error: {e}")
        return None


def search_arxiv(topic, max_results=5):
    """
    Search arXiv for papers on a topic.
    Uses HTTPS + browser-like headers to avoid 403 blocks.
    Falls back to Semantic Scholar if arXiv fails.
    """
    papers = _search_arxiv_api(topic, max_results)
    if papers:
        return papers

    print("arXiv failed, trying Semantic Scholar...")
    papers = _search_semantic_scholar(topic, max_results)
    if papers:
        return papers

    print("Both APIs failed, returning mock data for testing...")
    return _mock_papers(topic, max_results)


def _search_arxiv_api(topic, max_results):
    """Try arXiv API with HTTPS and browser headers."""
    try:
        query = urllib.parse.quote(topic)
        url = (
            f"https://export.arxiv.org/api/query?"
            f"search_query=all:{query}"
            f"&start=0&max_results={max_results}"
            f"&sortBy=relevance&sortOrder=descending"
        )

        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=20, context=SSL_CTX) as response:
            xml_data = response.read()

        ns = {
            'atom': 'http://www.w3.org/2005/Atom',
            'arxiv': 'http://arxiv.org/schemas/atom'
        }

        root = ET.fromstring(xml_data)
        papers = []

        for entry in root.findall('atom:entry', ns):
            title_el     = entry.find('atom:title', ns)
            summary_el   = entry.find('atom:summary', ns)
            published_el = entry.find('atom:published', ns)
            id_el        = entry.find('atom:id', ns)

            authors = []
            for author in entry.findall('atom:author', ns):
                name_el = author.find('atom:name', ns)
                if name_el is not None:
                    authors.append(name_el.text)

            if title_el is not None and summary_el is not None:
                papers.append({
                    "title":     title_el.text.strip().replace('\n', ' '),
                    "abstract":  summary_el.text.strip().replace('\n', ' '),
                    "authors":   authors[:5],
                    "published": published_el.text[:10] if published_el is not None else "Unknown",
                    "url":       id_el.text if id_el is not None else ""
                })

        print(f"arXiv returned {len(papers)} papers")
        return papers

    except Exception as e:
        print(f"arXiv API error: {e}")
        return []


def _search_semantic_scholar(topic, max_results):
    """Fallback: Semantic Scholar public API."""
    try:
        import json
        query = urllib.parse.quote(topic)
        url = (
            f"https://api.semanticscholar.org/graph/v1/paper/search"
            f"?query={query}&limit={max_results}"
            f"&fields=title,abstract,authors,year,externalIds"
        )

        req = urllib.request.Request(url, headers={
            **HEADERS,
            'Accept': 'application/json'
        })

        with urllib.request.urlopen(req, timeout=20, context=SSL_CTX) as response:
            data = json.loads(response.read())

        papers = []
        for p in data.get('data', []):
            abstract = p.get('abstract') or ''
            if not abstract:
                continue
            authors = [a.get('name', '') for a in p.get('authors', [])[:5]]
            ext_ids = p.get('externalIds', {})
            arxiv_id = ext_ids.get('ArXiv', '')
            url_link = f"https://arxiv.org/abs/{arxiv_id}" if arxiv_id else ""

            papers.append({
                "title":     p.get('title', 'Unknown Title'),
                "abstract":  abstract,
                "authors":   authors,
                "published": str(p.get('year', 'Unknown')),
                "url":       url_link
            })

        print(f"Semantic Scholar returned {len(papers)} papers")
        return papers

    except Exception as e:
        print(f"Semantic Scholar error: {e}")
        return []


def _mock_papers(topic, max_results):
    """
    Last resort: return placeholder papers so the UI doesn't break.
    User will see results but with a note that live search failed.
    """
    import random
    methods = ["deep learning", "transformer", "neural network", "BERT", "GPT"]
    years   = ["2022", "2023", "2024"]

    papers = []
    for i in range(min(max_results, 3)):
        method = random.choice(methods)
        year   = random.choice(years)
        papers.append({
            "title":    f"[DEMO] {topic.title()}: A {method.title()} Approach ({i+1})",
            "abstract": (
                f"This paper investigates {topic} using {method} techniques. "
                f"We propose a novel approach that addresses key limitations in existing methods. "
                f"Our method achieves state-of-the-art results on multiple benchmarks. "
                f"However, limitations remain in scalability and generalization. "
                f"Future work will explore extending this approach to broader domains."
            ),
            "authors":   [f"Author {chr(65+i)}", f"Author {chr(66+i)}"],
            "published": f"{year}-01-01",
            "url":       f"https://arxiv.org/search/?query={urllib.parse.quote(topic)}"
        })

    return papers


def clean_extracted(text):
    """Clean and normalize extracted text."""
    if not text:
        return None
    text = re.sub(r'\s+', ' ', text)
    lines = [l.strip() for l in text.split('.') if len(l.strip()) > 20]
    text = '. '.join(lines)
    return text.strip() if len(text) > 100 else None
