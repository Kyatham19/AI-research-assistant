import re
from collections import Counter
from heapq import nlargest

STOPWORDS = set([
    "a","an","the","and","or","but","in","on","at","to","for","of","with",
    "is","are","was","were","be","been","being","have","has","had","do","does",
    "did","will","would","could","should","may","might","shall","can","this",
    "that","these","those","it","its","we","our","they","their","he","she",
    "his","her","i","my","you","your","as","by","from","into","through",
    "during","including","until","against","among","throughout","despite",
    "towards","upon","about","such","not","also","more","than","other",
    "which","who","how","what","when","where","than","there","then","so",
    "if","each","all","both","between","after","before","while","since",
    "however","therefore","thus","hence","et","al","fig","table","paper",
    "study","research","results","data","using","used","based","proposed",
    "approach","method","methods","model","models","show","shows","shown",
    "found","work","use","two","one","three","new","high","low","large",
    "small","different","same","first","second","third","respectively"
])

GAP_PHRASES = [
    "gap in", "lack of", "no existing", "no prior", "little attention",
    "rarely studied", "underexplored", "understudied", "limited research",
    "has not been studied", "not yet explored", "open problem", "open question",
    "remains open", "not well studied", "insufficient research", "few studies",
    "little work", "limited work", "not been addressed"
]

LIMITATION_PHRASES = [
    "limitation", "limitations", "limited by", "drawback", "drawbacks",
    "shortcoming", "shortcomings", "constraint", "constraints", "weakness",
    "weaknesses", "unfortunately", "not able to", "unable to", "fails to",
    "does not handle", "cannot handle", "restricted to", "only works",
    "assumption", "assumptions", "computational cost", "expensive",
    "scalability", "overfitting", "narrow", "incomplete", "inadequate"
]

FUTURE_PHRASES = [
    "future work", "future research", "future direction", "future study",
    "can be extended", "could be extended", "promising direction",
    "in the future", "further investigation", "further exploration",
    "next step", "potential extension", "worth exploring", "remains to be",
    "needs further", "we plan to", "we intend to", "will be explored",
    "can be improved", "could be improved", "scope for improvement",
    "promising avenue", "future avenue", "open for future"
]

CONTRIBUTION_PHRASES = [
    "we propose", "we present", "we introduce", "we develop", "we design",
    "this paper proposes", "this paper presents", "this paper introduces",
    "our contribution", "our approach", "our method", "our model",
    "novel", "new method", "new approach", "outperforms", "state-of-the-art",
    "significantly improves", "first to", "to the best of our knowledge",
    "we demonstrate", "we show that", "we achieve"
]

METHOD_KEYWORDS = [
    "neural network", "deep learning", "machine learning", "transformer",
    "bert", "gpt", "lstm", "cnn", "rnn", "attention mechanism",
    "reinforcement learning", "supervised", "unsupervised", "semi-supervised",
    "random forest", "svm", "support vector", "regression", "classification",
    "clustering", "embedding", "fine-tuning", "pre-training", "transfer learning",
    "gradient descent", "backpropagation", "batch normalization", "dropout",
    "convolutional", "recurrent", "encoder", "decoder", "autoencoder",
    "generative", "discriminative", "bayesian", "probabilistic", "statistical"
]


def clean_text(text):
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'[^\w\s\.\,\!\?\;\:\-]', ' ', text)
    return text.strip()


def sentence_split(text):
    sentences = re.split(r'(?<=[.!?])\s+', text)
    return [s.strip() for s in sentences if len(s.strip()) > 30]


def extract_keywords(text, top_n=12):
    words = re.findall(r'\b[a-zA-Z]{4,}\b', text.lower())
    filtered = [w for w in words if w not in STOPWORDS]
    freq = Counter(filtered)
    tokens = text.lower().split()
    bigrams = [f"{tokens[i]} {tokens[i+1]}" for i in range(len(tokens)-1)
               if tokens[i] not in STOPWORDS and tokens[i+1] not in STOPWORDS
               and len(tokens[i]) > 3 and len(tokens[i+1]) > 3]
    bigram_freq = Counter(bigrams)
    keywords = []
    seen = set()
    for bigram, count in bigram_freq.most_common(6):
        if count >= 2:
            keywords.append({"term": bigram, "score": count * 2})
            seen.update(bigram.split())
    for word, count in freq.most_common(20):
        if word not in seen and len(keywords) < top_n:
            keywords.append({"term": word, "score": count})
    return keywords[:top_n]


def score_sentences(sentences, keywords):
    kw_set = set(k['term'].lower() for k in keywords)
    word_freq = Counter()
    for s in sentences:
        words = re.findall(r'\b[a-zA-Z]{4,}\b', s.lower())
        word_freq.update(w for w in words if w not in STOPWORDS)
    scored = []
    for sent in sentences:
        score = 0
        words = re.findall(r'\b[a-zA-Z]{4,}\b', sent.lower())
        for word in words:
            if word in word_freq:
                score += word_freq[word]
        for kw in kw_set:
            if kw in sent.lower():
                score += 5
        scored.append((score, sent))
    return scored


def generate_summary(text, num_sentences=5):
    sentences = sentence_split(text)
    if len(sentences) <= num_sentences:
        return " ".join(sentences)
    keywords = extract_keywords(text, top_n=10)
    scored = score_sentences(sentences, keywords)
    top = nlargest(num_sentences, scored, key=lambda x: x[0])
    top_sents = [s for _, s in top]
    ordered = [s for s in sentences if s in top_sents]
    return " ".join(ordered)


def extract_by_phrases(text, phrases, max_results=5):
    sentences = sentence_split(text)
    matched = []
    for sent in sentences:
        sl = sent.lower()
        for phrase in phrases:
            if phrase in sl:
                matched.append(sent.strip())
                break
    return matched[:max_results]


def extract_research_gaps(text):
    results = extract_by_phrases(text, GAP_PHRASES)
    return results if results else ["No explicit research gaps detected."]


def extract_limitations(text):
    results = extract_by_phrases(text, LIMITATION_PHRASES)
    return results if results else ["No explicit limitations detected."]


def extract_future_scope(text):
    results = extract_by_phrases(text, FUTURE_PHRASES)
    return results if results else ["No explicit future scope detected."]


def extract_contributions(text):
    results = extract_by_phrases(text, CONTRIBUTION_PHRASES)
    return results if results else ["No explicit contributions detected."]


def extract_methods(text):
    found = []
    tl = text.lower()
    for method in METHOD_KEYWORDS:
        if method in tl:
            found.append(method.title())
    return list(dict.fromkeys(found))[:10] if found else ["No specific methods detected"]


def extract_important_sentences(text, n=5):
    sentences = sentence_split(text)
    keywords = extract_keywords(text)
    scored = score_sentences(sentences, keywords)
    top = nlargest(n, scored, key=lambda x: x[0])
    return [s for _, s in top]


def compute_stats(text):
    words = re.findall(r'\b\w+\b', text)
    sentences = sentence_split(text)
    return {
        "word_count": len(words),
        "sentence_count": len(sentences),
        "avg_sentence_length": round(len(words) / max(len(sentences), 1), 1),
        "unique_words": len(set(w.lower() for w in words))
    }


def analyze_text(text):
    text = clean_text(text)
    if len(text) < 50:
        return {"error": "Text too short for analysis"}
    return {
        "summary": generate_summary(text),
        "keywords": extract_keywords(text),
        "important_sentences": extract_important_sentences(text),
        "research_gaps": extract_research_gaps(text),
        "limitations": extract_limitations(text),
        "future_scope": extract_future_scope(text),
        "contributions": extract_contributions(text),
        "methods": extract_methods(text),
        "stats": compute_stats(text)
    }
import re
from collections import Counter
from heapq import nlargest

STOPWORDS = set([
    "a","an","the","and","or","but","in","on","at","to","for","of","with",
    "is","are","was","were","be","been","being","have","has","had","do","does",
    "did","will","would","could","should","may","might","shall","can","this",
    "that","these","those","it","its","we","our","they","their","he","she",
    "his","her","i","my","you","your","as","by","from","into","through",
    "during","including","until","against","among","throughout","despite",
    "towards","upon","about","such","not","also","more","than","other",
    "which","who","how","what","when","where","than","there","then","so",
    "if","each","all","both","between","after","before","while","since",
    "however","therefore","thus","hence","et","al","fig","table","paper",
    "study","research","results","data","using","used","based","proposed",
    "approach","method","methods","model","models","show","shows","shown",
    "found","work","use","two","one","three","new","high","low","large",
    "small","different","same","first","second","third","respectively"
])

GAP_PHRASES = [
    "gap in", "lack of", "no existing", "no prior", "little attention",
    "rarely studied", "underexplored", "understudied", "limited research",
    "has not been studied", "not yet explored", "open problem", "open question",
    "remains open", "not well studied", "insufficient research", "few studies",
    "little work", "limited work", "not been addressed"
]

LIMITATION_PHRASES = [
    "limitation", "limitations", "limited by", "drawback", "drawbacks",
    "shortcoming", "shortcomings", "constraint", "constraints", "weakness",
    "weaknesses", "unfortunately", "not able to", "unable to", "fails to",
    "does not handle", "cannot handle", "restricted to", "only works",
    "assumption", "assumptions", "computational cost", "expensive",
    "scalability", "overfitting", "narrow", "incomplete", "inadequate"
]

FUTURE_PHRASES = [
    "future work", "future research", "future direction", "future study",
    "can be extended", "could be extended", "promising direction",
    "in the future", "further investigation", "further exploration",
    "next step", "potential extension", "worth exploring", "remains to be",
    "needs further", "we plan to", "we intend to", "will be explored",
    "can be improved", "could be improved", "scope for improvement",
    "promising avenue", "future avenue", "open for future"
]

CONTRIBUTION_PHRASES = [
    "we propose", "we present", "we introduce", "we develop", "we design",
    "this paper proposes", "this paper presents", "this paper introduces",
    "our contribution", "our approach", "our method", "our model",
    "novel", "new method", "new approach", "outperforms", "state-of-the-art",
    "significantly improves", "first to", "to the best of our knowledge",
    "we demonstrate", "we show that", "we achieve"
]

METHOD_KEYWORDS = [
    "neural network", "deep learning", "machine learning", "transformer",
    "bert", "gpt", "lstm", "cnn", "rnn", "attention mechanism",
    "reinforcement learning", "supervised", "unsupervised", "semi-supervised",
    "random forest", "svm", "support vector", "regression", "classification",
    "clustering", "embedding", "fine-tuning", "pre-training", "transfer learning",
    "gradient descent", "backpropagation", "batch normalization", "dropout",
    "convolutional", "recurrent", "encoder", "decoder", "autoencoder",
    "generative", "discriminative", "bayesian", "probabilistic", "statistical"
]


def clean_text(text):
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'[^\w\s\.\,\!\?\;\:\-]', ' ', text)
    return text.strip()


def sentence_split(text):
    sentences = re.split(r'(?<=[.!?])\s+', text)
    return [s.strip() for s in sentences if len(s.strip()) > 30]


def extract_keywords(text, top_n=12):
    words = re.findall(r'\b[a-zA-Z]{4,}\b', text.lower())
    filtered = [w for w in words if w not in STOPWORDS]
    freq = Counter(filtered)
    tokens = text.lower().split()
    bigrams = [f"{tokens[i]} {tokens[i+1]}" for i in range(len(tokens)-1)
               if tokens[i] not in STOPWORDS and tokens[i+1] not in STOPWORDS
               and len(tokens[i]) > 3 and len(tokens[i+1]) > 3]
    bigram_freq = Counter(bigrams)
    keywords = []
    seen = set()
    for bigram, count in bigram_freq.most_common(6):
        if count >= 2:
            keywords.append({"term": bigram, "score": count * 2})
            seen.update(bigram.split())
    for word, count in freq.most_common(20):
        if word not in seen and len(keywords) < top_n:
            keywords.append({"term": word, "score": count})
    return keywords[:top_n]


def score_sentences(sentences, keywords):
    kw_set = set(k['term'].lower() for k in keywords)
    word_freq = Counter()
    for s in sentences:
        words = re.findall(r'\b[a-zA-Z]{4,}\b', s.lower())
        word_freq.update(w for w in words if w not in STOPWORDS)
    scored = []
    for sent in sentences:
        score = 0
        words = re.findall(r'\b[a-zA-Z]{4,}\b', sent.lower())
        for word in words:
            if word in word_freq:
                score += word_freq[word]
        for kw in kw_set:
            if kw in sent.lower():
                score += 5
        scored.append((score, sent))
    return scored


def generate_summary(text, num_sentences=5):
    sentences = sentence_split(text)
    if len(sentences) <= num_sentences:
        return " ".join(sentences)
    keywords = extract_keywords(text, top_n=10)
    scored = score_sentences(sentences, keywords)
    top = nlargest(num_sentences, scored, key=lambda x: x[0])
    top_sents = [s for _, s in top]
    ordered = [s for s in sentences if s in top_sents]
    return " ".join(ordered)


def extract_by_phrases(text, phrases, max_results=5):
    sentences = sentence_split(text)
    matched = []
    for sent in sentences:
        sl = sent.lower()
        for phrase in phrases:
            if phrase in sl:
                matched.append(sent.strip())
                break
    return matched[:max_results]


def extract_research_gaps(text):
    results = extract_by_phrases(text, GAP_PHRASES)
    return results if results else ["No explicit research gaps detected."]


def extract_limitations(text):
    results = extract_by_phrases(text, LIMITATION_PHRASES)
    return results if results else ["No explicit limitations detected."]


def extract_future_scope(text):
    results = extract_by_phrases(text, FUTURE_PHRASES)
    return results if results else ["No explicit future scope detected."]


def extract_contributions(text):
    results = extract_by_phrases(text, CONTRIBUTION_PHRASES)
    return results if results else ["No explicit contributions detected."]


def extract_methods(text):
    found = []
    tl = text.lower()
    for method in METHOD_KEYWORDS:
        if method in tl:
            found.append(method.title())
    return list(dict.fromkeys(found))[:10] if found else ["No specific methods detected"]


def extract_important_sentences(text, n=5):
    sentences = sentence_split(text)
    keywords = extract_keywords(text)
    scored = score_sentences(sentences, keywords)
    top = nlargest(n, scored, key=lambda x: x[0])
    return [s for _, s in top]


def compute_stats(text):
    words = re.findall(r'\b\w+\b', text)
    sentences = sentence_split(text)
    return {
        "word_count": len(words),
        "sentence_count": len(sentences),
        "avg_sentence_length": round(len(words) / max(len(sentences), 1), 1),
        "unique_words": len(set(w.lower() for w in words))
    }


def analyze_text(text):
    text = clean_text(text)
    if len(text) < 50:
        return {"error": "Text too short for analysis"}
    return {
        "summary": generate_summary(text),
        "keywords": extract_keywords(text),
        "important_sentences": extract_important_sentences(text),
        "research_gaps": extract_research_gaps(text),
        "limitations": extract_limitations(text),
        "future_scope": extract_future_scope(text),
        "contributions": extract_contributions(text),
        "methods": extract_methods(text),
        "stats": compute_stats(text)
    }
