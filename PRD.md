# Product Requirement Document (PRD)
## CodeAlpha AI Internship — Task 2: Chatbot for FAQs

---

### Document Information
- **Project Name:** CodeAlpha FAQ Chatbot
- **Repository Name:** `CodeAlpha_ChatbotForFAQs`
- **Domain:** Artificial Intelligence / Natural Language Processing (NLP)
- **Document Version:** 1.1.0
- **Status:** Implemented / Ready for Submission
- **Author:** CodeAlpha AI Intern

---

## 1. Executive Summary & Problem Statement

### 1.1 Overview
The **CodeAlpha FAQ Chatbot** is an NLP-driven conversational agent that matches user questions against a structured FAQ knowledge base using text preprocessing and vector similarity (TF-IDF + cosine similarity).

Built to satisfy **Task 2** of the CodeAlpha AI Internship, it delivers accurate, context-relevant answers through a responsive Flask web application. The matcher is entirely local: it needs no API key, paid service, or network connection at query time.

### 1.2 Problem Statement
Users seeking support commonly face:
1. Static FAQ pages with long walls of text that are tedious to scan.
2. Rigid keyword search that fails on synonyms or natural phrasing.
3. Slow responses to repetitive questions.

This project converts static FAQs into a conversational assistant that understands varied phrasings and answers instantly.

---

## 2. Project Goals & Scope

### 2.1 Core In-Scope Objectives
- **FAQ Knowledge Base:** A modular, categorized JSON dataset of **27** FAQs covering internship rules, submission guidelines, perks, AI tasks, NLP architecture, and support.
- **NLP Preprocessing Pipeline:** Lowercasing, punctuation removal, tokenization, stopword filtering, and WordNet lemmatization using `nltk`.
- **Matching Algorithm:** TF-IDF vector space modeling with unigrams + bigrams and cosine similarity ranking using `scikit-learn`.
- **Confidence Scoring & Fallback:**
  - High confidence (score ≥ 0.40): return the primary answer directly.
  - Moderate confidence (0.20 ≤ score < 0.40): return the closest answer with a *"Did you mean...?"* prompt and related questions.
  - Low confidence (score < 0.20): return a friendly fallback with suggested topics.
- **Interactive Chat Interface:** Chat bubbles, typing indicator, quick-reply chips, confidence badges, theme toggle, and a searchable FAQ drawer with keyboard support.
- **Lightweight & Local:** Only `flask`, `nltk`, and `scikit-learn` are required.

### 2.2 Out-of-Scope
- ❌ External LLM / paid translation APIs (keeps the solution free, private, and offline at query time).
- ❌ Multi-turn dialogue state tracking or long-term memory databases (the API accepts a `history` field for compatibility, but matching is stateless).
- ❌ User authentication and persistent login sessions.

### 2.3 Success Metrics
| Metric | Target | Verification Method |
| :--- | :--- | :--- |
| Query Latency | < 50 ms after initialization | Timed test client request |
| Matching Accuracy | > 85% on paraphrased queries (27-entry suite) | `python test_chatbot.py` |
| Dependency Footprint | 3 packages, no API keys | `requirements.txt` |
| CodeAlpha Compliance | 100% adherence to Task 2 specs | checklist in section 9 |

---

## 3. System Architecture & NLP Workflow

### 3.1 Architecture Flowchart
```mermaid
graph TD
    User([User in Chat UI])

    subgraph Frontend ["Frontend (HTML5 / CSS / Vanilla JS)"]
        ChatBox["Chat Window & Message History"]
        QuickChips["Suggested Question Chips"]
        InputArea["Text Input & Send Button"]
        FaqDrawer["Searchable FAQ Drawer"]
    end

    subgraph Backend ["Flask REST API Server"]
        Router["/api/chat, /api/faqs, /api/categories, /api/health"]
        NLP["NLP Preprocessor (Clean, Tokenize, Lemmatize)"]
        Vectorizer["TF-IDF Vectorizer (Unigram + Bigram)"]
        Matcher["Cosine Similarity Matcher & Scorer"]
        KnowledgeBase[("FAQ Knowledge Base (faqs.json)")]
    end

    User --> InputArea
    QuickChips --> InputArea
    FaqDrawer --> InputArea
    InputArea -->|POST /api/chat {message}| Router

    Router --> NLP
    NLP --> Vectorizer
    KnowledgeBase -.->|Initial Indexing| Vectorizer
    Vectorizer --> Matcher
    Matcher -->|Ranked Match & Confidence| Router

    Router -->|JSON {answer, confidence, suggestions}| ChatBox
    ChatBox --> User
```

### 3.2 NLP Matching Pipeline Detail
1. **Corpus Ingestion:** Load `faqs.json` containing questions, answers, categories, and keyword tags.
2. **Text Normalization:** case folding, punctuation removal, stopword removal, and lemmatization (e.g. *submitting* → *submit*).
3. **Feature Extraction:** TF-IDF vectors with `ngram_range=(1, 2)`.
4. **Similarity Computation:**
   $$\text{Cosine Similarity}(\vec{q}, \vec{d}_i) = \frac{\vec{q} \cdot \vec{d}_i}{\|\vec{q}\| \|\vec{d}_i\|}$$
5. **Decision Logic:** Select the top-scoring FAQ and apply the thresholds from §2.1.

---

## 4. Functional Requirements

### 4.1 Knowledge Base (FR-1)
- **FR-1.1 Data Schema:** FAQs stored in `data/faqs.json` with `id`, `category`, `question`, `answer`, and `keywords`.
- **FR-1.2 Domain Coverage:** **27** categorized FAQs.

### 4.2 NLP Preprocessing & Matching (FR-2)
- **FR-2.1 Text Cleaner:** strips noisy characters, tokenizes, removes stopwords.
- **FR-2.2 Lemmatizer:** standardizes inflected forms using NLTK WordNet, with a safe fallback if the corpus is unavailable.
- **FR-2.3 Vectorizer Cache:** in-memory fitted TF-IDF model built at startup.
- **FR-2.4 Confidence Thresholding:** as defined in §2.1 (0.40 / 0.20 / fallback).

### 4.3 Chat User Interface (FR-3)
- **FR-3.1 Conversation Stream:** scrollable stream of user/bot bubbles with timestamps and an ARIA live region.
- **FR-3.2 Typing Indicator:** animated three-dot indicator while processing.
- **FR-3.3 Quick Suggestions:** clickable chips for popular queries and follow-ups.
- **FR-3.4 Clear Chat:** resets the conversation and history.
- **FR-3.5 Confidence Badge:** displays match percentage (e.g. *"58% Match"*).
- **FR-3.6 FAQ Drawer:** searchable modal; `Esc` closes, `Tab` focus is trapped.

### 4.4 REST API Endpoints (FR-4)
| Endpoint | Method | Purpose |
| :--- | :--- | :--- |
| `/api/chat` | POST | Returns the ranked answer wrapped in `data` |
| `/api/faqs` | GET | Returns all FAQs; optional `?category=` filter |
| `/api/categories` | GET | Returns sorted category names |
| `/api/health` | GET | Health check |

**`POST /api/chat` success response (200 OK):**
```json
{
  "status": "success",
  "data": {
    "status": "matched",
    "answer": "Upload your complete source code to GitHub in a repository named: CodeAlpha_ProjectName.",
    "matched_question": "What is the required GitHub repository naming format?",
    "category": "Submission Guidelines",
    "confidence": 76.5,
    "score": 0.765,
    "engine": "NLP Cosine Similarity",
    "suggestions": ["How do I submit my completed project?"]
  }
}
```

**Error response (400):** `{"status": "error", "message": "Message cannot be empty."}`

---

## 5. Non-Functional Requirements

### 5.1 Performance & Efficiency
- No external network calls during query processing.
- Query processing under **50 ms** once the engine is initialized.
- First launch downloads NLTK corpora once (~15 MB); this one-time bootstrap may take several seconds on a fresh machine.
- The Werkzeug debugger is disabled by default and the server binds to `127.0.0.1` unless configured otherwise.

### 5.2 UI/UX Aesthetics
- Crimson/obsidian glassmorphism design.
- Google Font 'Plus Jakarta Sans', 'Racing Sans One', and 'JetBrains Mono'.
- Responsive from 320 px mobile to wide desktop; subtle entrance animations.

### 5.3 Reliability & Robustness
- Handles empty, punctuation-only, and out-of-domain inputs gracefully.
- XSS-safe rendering: all dynamic text is HTML-escaped client side.
- Missing NLTK corpora degrade gracefully instead of crashing requests.

---

## 6. Proposed Project Directory Structure

```text
CodeAlpha_ChatbotForFAQs/
├── app.py                  # Flask server & REST API routes
├── chatbot_engine.py       # NLP preprocessing, TF-IDF & cosine matching
├── requirements.txt        # flask, nltk, scikit-learn
├── .env.example            # Optional local configuration
├── PRD.md                  # This document
├── README.md               # Setup and usage guide
├── test_chatbot.py         # 18 offline unit/API tests
├── data/faqs.json          # 27 categorized FAQs
├── static/css/style.css    # Theme and layout
├── static/js/chat.js       # Messaging and modal logic
└── templates/index.html    # Chat interface
```

---

## 7. UI Wireframe / Layout

```
+-----------------------------------------------------------------------------------+
|  CodeAlpha FAQ Assistant                              [Browse FAQs] [Clear] [Theme]|
+-----------------------------------------------------------------------------------+
|  [Bot]  Welcome to CodeAlpha FAQ Assistant!                                       |
|        Ask me a question or tap a popular prompt below to get started:            |
|        Just now                                                                   |
|                                                                                   |
|                          How do I submit my completed task? [User]                 |
|                                                                                   |
|  [Bot]  A submission form will be shared in your respective WhatsApp group...     |
|        (Submission Guidelines • 46% Match • NLP Cosine Similarity)                |
|                                                                                   |
|  Related questions: [GitHub Repo Naming]  [Internship Perks]                       |
+-----------------------------------------------------------------------------------+
|  [ Type your question here...                                       ] [ Send ]     |
+-----------------------------------------------------------------------------------+
```

---

## 8. Implementation Roadmap

| Milestone | Action Items | Status |
| :--- | :--- | :--- |
| 1. Knowledge Base & NLP Engine | Create 27-entry `faqs.json`; build preprocessing, TF-IDF and cosine matcher | ✅ |
| 2. Backend API | Implement 4 endpoints; add 18 automated tests | ✅ |
| 3. Modern Chat UI | Build responsive chat UI, theme toggle and accessible FAQ drawer | ✅ |
| 4. Verification & Docs | Run tests, align documentation with implementation | ✅ |

---

## 9. CodeAlpha Submission Checklist

- [x] Repository named `CodeAlpha_ChatbotForFAQs`
- [x] FAQ dataset collected with questions and comprehensive answers
- [x] Text preprocessed using NLP (tokenization, cleaning, lemmatization)
- [x] Questions matched using cosine similarity / TF-IDF
- [x] Best matching answer displayed as a chatbot response
- [x] Intuitive, modern chat UI for user interaction
- [x] Complete `README.md` and automated test suite
