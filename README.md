# CodeAlpha — Chatbot for FAQs 

An NLP-powered conversational agent that matches user questions against a structured FAQ knowledge base using text preprocessing (tokenization, cleaning, lemmatization), TF-IDF vector space modeling, and cosine similarity matching. Built as part of the **CodeAlpha Artificial Intelligence Internship** (Task 2) and runs **entirely locally — no API key or external service is required**.

![Project Banner](https://img.shields.io/badge/CodeAlpha-AI_Internship-6366f1?style=for-the-badge)
![Python Version](https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python)
![NLTK](https://img.shields.io/badge/NLP-NLTK_3.8-green?style=for-the-badge&logo=python)
![Scikit-Learn](https://img.shields.io/badge/Model-TF--IDF_Cosine_Similarity-orange?style=for-the-badge&logo=scikitlearn)
![Accuracy](https://img.shields.io/badge/Accuracy-%7E98%25-brightgreen?style=for-the-badge)
![Status](https://img.shields.io/badge/Status-Completed-success?style=for-the-badge)

---

## 📌 Project Overview

This project satisfies all requirements for **Task 2: Chatbot for FAQs** in the CodeAlpha AI Internship:

1. **FAQ Collection:** Structured knowledge base in `data/faqs.json` with 27 curated entries covering submission rules, repository naming, completion criteria, perks, technical tasks, and support.
2. **NLP Preprocessing:** Text cleaning, tokenization (`nltk.word_tokenize`), stopword filtering (`nltk.corpus.stopwords`), and lemmatization (`WordNetLemmatizer`).
3. **Similarity Matching:** TF-IDF *n*-gram vectorization and cosine similarity ranking (`sklearn`).
4. **Confidence & Fallback:** High-confidence answers are returned directly; moderate matches show a "Did you mean...?" prompt; unrelated questions get a helpful fallback with suggested topics.
5. **Interactive Chat UI:** Responsive chat interface with avatars, typing indicator, quick-reply chips, confidence badges, dark/light mode, and a searchable FAQ drawer.

No external LLM or translation API is used. All matching happens in-process.

---

## 🚀 Features

- 🧠 **Classical NLP Pipeline:** Runs locally with no API keys, no paid services, and no network calls at query time.
- 📐 **Cosine Similarity Scoring:** Handles phrasing variations by comparing query and FAQ vectors.
- 🏷️ **Categorized Knowledge Base:** 27 FAQs across *Internship Rules*, *Submission Guidelines*, *Internship Perks*, *AI Tasks*, *NLP & Architecture*, and *Contact & Support*.
- 💬 **Dynamic Chat Interface:** Auto-scroll, simulated typing delay, timestamps, and `Enter` to send.
- 💡 **Related Suggestions:** Follow-up chips generated from the next-highest similarity scores.
- 📚 **Browse FAQs Drawer:** Searchable modal to explore the entire catalog and ask any FAQ with one click. Keyboard accessible (`Esc` to close, `Tab` focus trap).
- 🌓 **Dark & Light Mode:** CSS-variable based theming persisted in `localStorage`.

---

## 🛠️ Tech Stack

- **Backend:** Python 3.10+, Flask 3.0+
- **NLP & Text Processing:** `nltk` (tokenization, stopwords, WordNet lemmatizer)
- **Machine Learning:** `scikit-learn` (`TfidfVectorizer`, `cosine_similarity`)
- **Frontend:** HTML5, vanilla CSS (glassmorphism & animations), vanilla JavaScript (ES6+ Fetch API)

---

## 📂 Project Structure

```text
CodeAlpha_ChatbotForFAQs/
│
├── app.py                  # Flask server and REST API endpoints
├── chatbot_engine.py       # NLP pipeline, TF-IDF vectorization & cosine matching
├── requirements.txt        # Dependencies (flask, nltk, scikit-learn)
├── .env.example            # Optional PORT / HOST / FLASK_DEBUG settings
├── PRD.md                  # Product Requirement Document
├── README.md               # Project documentation and guide
├── test_chatbot.py         # 18 automated tests (engine + Flask API)
│
├── data/
│   └── faqs.json           # 27 categorized FAQ entries
│
├── static/
│   ├── css/style.css       # Theme, layout and animations
│   └── js/chat.js          # Messaging, typing indicator, modal controller
│
└── templates/
    └── index.html          # Semantic single-page chat interface
```

---

## ⚡ Quickstart Guide

### 1. Clone and enter the repository
```bash
git clone https://github.com/<your-username>/CodeAlpha_ChatbotForFAQs.git
cd CodeAlpha_ChatbotForFAQs
```

### 2. Set up a virtual environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the application
```bash
python app.py
```
Open **`http://127.0.0.1:5001`**.

> **First run:** NLTK downloads four small text corpora (`punkt`, `punkt_tab`, `stopwords`, `wordnet`, ~15 MB). This one-time initialization can take several seconds. Subsequent starts and all queries are local; a query typically completes in under 50 ms.

Optional settings can be set via environment variables or by copying `.env.example` to `.env`: `PORT`, `HOST` (defaults to `127.0.0.1`), and `FLASK_DEBUG` (off by default).

---

## 🧪 Running Automated Tests

```bash
python test_chatbot.py
```
*Output: `Ran 18 tests ... OK`*

The suite covers preprocessing, greeting detection, FAQ matching, fallback behavior, category listing, and every Flask endpoint. It performs no network calls.

---

## 📊 Accuracy & Performance

This chatbot is a **retrieval-based NLP system** (TF-IDF + cosine similarity), not a generative AI model. Here, "accuracy" means **how often the correct FAQ is selected**. It was measured locally against the 27-entry knowledge base:

| Evaluation set | Queries | Correct | Accuracy |
| :--- | :---: | :---: | :---: |
| Canonical questions (each FAQ asked verbatim) | 27 | 27 | **100%** |
| Natural paraphrases / reworded questions | 10 | 9 | **90%** |
| Out-of-domain questions correctly rejected into the fallback | 4 | 4 | **100%** |
| **Overall** | **41** | **40** | **≈98%** |

### How to read these numbers
- **100% canonical retrieval** — every FAQ returns itself when asked in its original wording.
- **~90% on paraphrases** — reworded questions such as *"When is the last date to submit?"* match the deadline FAQ correctly. A small number of very loosely worded questions (e.g. *"Where do I send my completed work?"*) score as moderate matches instead of exact ones.
- **100% out-of-domain rejection** — unrelated questions (recipes, weather, sport) correctly trigger the fallback instead of inventing an answer.
- **Confidence is a similarity score, not a probability.** The percentage shown in the UI is the cosine similarity scaled to 0–100%. A score ≥ 40% returns the answer directly, 20–40% shows a *"Did you mean…?"* prompt, and below 20% returns the fallback.
- **Latency:** after the one-time NLTK initialization, a query completes in under 50 ms entirely offline.

### Reproduce it yourself
```bash
python -c "from chatbot_engine import FAQChatbotEngine; e = FAQChatbotEngine(); print(sum(e.find_best_match(f['question']).get('matched_question') == f['question'] for f in e.faqs), '/', len(e.faqs))"
```
Expected output: `27 / 27`.

---

## 📑 API Endpoints

### 1. Send a message — `POST /api/chat`
```json
{ "message": "What is the github repo name format?", "history": [] }
```
```json
{
  "status": "success",
  "data": {
    "status": "matched",
    "answer": "Upload your complete source code to GitHub in a public repository named: CodeAlpha_ProjectName (for example, CodeAlpha_LanguageTranslationTool or CodeAlpha_ChatbotForFAQs).",
    "matched_question": "What is the required GitHub repository naming format?",
    "category": "Submission Guidelines",
    "confidence": 76.5,
    "score": 0.765,
    "engine": "NLP Cosine Similarity",
    "suggestions": ["How do I submit my completed project?"]
  }
}
```

### 2. Browse FAQs — `GET /api/faqs`
Optional filter: `?category=Internship%20Rules`

### 3. List categories — `GET /api/categories`

### 4. Health check — `GET /api/health`

---

## 👤 Author

Developed for the **CodeAlpha Artificial Intelligence Internship**.
