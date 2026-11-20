"""
CodeAlpha AI Internship - Task 2: Chatbot for FAQs
NLP Preprocessing, TF-IDF Vectorization & Cosine Similarity Engine.

The engine runs fully locally: no API keys and no external network calls are
needed to answer a question. On first run NLTK fetches its small text corpora
(punkt, punkt_tab, stopwords, wordnet); after that everything is offline.
"""

import os
import re
import json
import logging
from typing import Dict, List, Any, Optional

import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Configure logger
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


def _load_env_file() -> None:
    """Loads optional local key=value settings (e.g. PORT) from a .env file."""
    env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
    if not os.path.exists(env_path):
        return
    try:
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    os.environ.setdefault(key.strip(), value.strip())
    except Exception as e:
        logger.warning(f"Error loading .env file: {e}")


_load_env_file()


def _resource_available(path: str) -> bool:
    """Checks for an extracted resource or its downloaded zip archive."""
    for candidate in (path, f"{path}.zip"):
        try:
            nltk.data.find(candidate)
            return True
        except LookupError:
            continue
    return False


def _init_nltk() -> None:
    """Makes sure the required NLTK resources are available (first run only)."""
    resources = {
        "punkt": "tokenizers/punkt",
        "punkt_tab": "tokenizers/punkt_tab",
        "stopwords": "corpora/stopwords",
        "wordnet": "corpora/wordnet",
    }
    for package, path in resources.items():
        if _resource_available(path):
            continue
        try:
            nltk.download(package, quiet=True)
        except Exception as e:
            logger.warning(f"Could not download NLTK package {package}: {e}")


_init_nltk()

try:
    STOP_WORDS = set(stopwords.words("english"))
except Exception:
    STOP_WORDS = set()

LEMMATIZER = WordNetLemmatizer()


def _lemmatize(token: str) -> str:
    """Lemmatizes a token, falling back to the raw token if wordnet is missing."""
    try:
        token = LEMMATIZER.lemmatize(token, pos="n")
        token = LEMMATIZER.lemmatize(token, pos="v")
    except LookupError:
        logger.warning("NLTK wordnet corpus unavailable; skipping lemmatization.")
    return token


def preprocess_text(text: str) -> str:
    """
    Cleans, tokenizes, removes stopwords, and lemmatizes input text.
    """
    if not text:
        return ""

    # Strip leading slash/backslash or commands
    cleaned = re.sub(r"^[\\/]+", "", text).strip().lower()

    # Remove non-alphanumeric characters except spaces
    cleaned = re.sub(r"[^a-zA-Z0-9\s]", " ", cleaned)

    # Tokenize
    try:
        tokens = word_tokenize(cleaned)
    except Exception:
        tokens = cleaned.split()

    # Remove stopwords and lemmatize
    processed_tokens = []
    for token in tokens:
        token = token.strip()
        if not token or (token in STOP_WORDS and len(token) > 1):
            continue
        processed_tokens.append(_lemmatize(token))

    return " ".join(processed_tokens)


class FAQChatbotEngine:
    """
    Local FAQ chatbot engine using TF-IDF vectorization and cosine similarity.
    """

    def __init__(self, data_path: Optional[str] = None):
        if data_path is None:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            data_path = os.path.join(base_dir, "data", "faqs.json")

        self.data_path = data_path
        self.faqs: List[Dict[str, Any]] = []
        self.processed_corpus: List[str] = []
        self.vectorizer: Optional[TfidfVectorizer] = None
        self.tfidf_matrix = None

        self.load_data()
        self.build_index()

    def load_data(self) -> None:
        """Loads the FAQ dataset from a JSON file."""
        if not os.path.exists(self.data_path):
            raise FileNotFoundError(f"FAQ dataset file not found at: {self.data_path}")

        with open(self.data_path, "r", encoding="utf-8") as f:
            self.faqs = json.load(f)
        logger.info(f"Loaded {len(self.faqs)} FAQ entries from {self.data_path}")

    def build_index(self) -> None:
        """Preprocesses questions and builds the TF-IDF feature matrix."""
        self.processed_corpus = []
        for item in self.faqs:
            question = item.get("question", "")
            keywords = " ".join(item.get("keywords", []))
            processed = preprocess_text(f"{question} {keywords}")
            self.processed_corpus.append(processed)

        self.vectorizer = TfidfVectorizer(ngram_range=(1, 2), sublinear_tf=True)
        self.tfidf_matrix = self.vectorizer.fit_transform(self.processed_corpus)
        logger.info("TF-IDF vectorizer fitted successfully on FAQ corpus.")

    def find_best_match(
        self, query: str, history: Optional[List[Dict[str, str]]] = None
    ) -> Dict[str, Any]:
        """
        Ranks FAQs with cosine similarity and returns the best matching answer.

        `history` is accepted for API compatibility; matching itself is stateless
        and depends only on the current question.
        """
        raw_query = query.strip() if query else ""
        if not raw_query:
            return {
                "status": "empty",
                "answer": "Please ask a question so I can help you!",
                "confidence": 0.0,
                "suggestions": [f["question"] for f in self.faqs[:3]],
            }

        cleaned_for_check = re.sub(r"^[\\/]+", "", raw_query).strip()

        # Handle simple greetings
        greetings = {"hi", "hello", "hey", "greetings", "good morning", "good afternoon"}
        if cleaned_for_check.lower() in greetings:
            return {
                "status": "greeting",
                "answer": (
                    "Hello! I am your CodeAlpha FAQ Assistant. You can ask me anything "
                    "about the internship tasks, submission rules, certificate criteria, "
                    "deadlines, or guidelines."
                ),
                "confidence": 100.0,
                "engine": "Greeting Responder",
                "suggestions": [
                    "How many tasks do I need to complete?",
                    "When is the submission deadline or last date?",
                    "What is the required GitHub repository naming format?",
                ],
            }

        processed_query = preprocess_text(cleaned_for_check)
        if not processed_query:
            processed_query = cleaned_for_check.lower()

        query_vector = self.vectorizer.transform([processed_query])
        similarity_scores = cosine_similarity(query_vector, self.tfidf_matrix).flatten()

        ranked_indices = similarity_scores.argsort()[::-1]
        best_index = ranked_indices[0]
        best_score = float(similarity_scores[best_index])
        best_faq = self.faqs[best_index]

        suggestions = [self.faqs[idx]["question"] for idx in ranked_indices[1:4]]
        confidence_pct = round(best_score * 100, 1)

        # Confidence thresholds are specified in PRD.md section 2.1 / 4.2.
        if best_score >= 0.40:
            return {
                "status": "matched",
                "answer": best_faq["answer"],
                "matched_question": best_faq["question"],
                "category": best_faq.get("category", "General"),
                "confidence": confidence_pct,
                "score": round(best_score, 4),
                "engine": "NLP Cosine Similarity",
                "suggestions": suggestions,
            }

        if best_score >= 0.20:
            return {
                "status": "moderate",
                "answer": (
                    f"Did you mean: \"{best_faq['question']}\"?\n\n{best_faq['answer']}"
                ),
                "matched_question": best_faq["question"],
                "category": best_faq.get("category", "General"),
                "confidence": confidence_pct,
                "score": round(best_score, 4),
                "engine": "NLP Cosine Similarity",
                "suggestions": suggestions,
            }

        return {
            "status": "fallback",
            "answer": (
                "I couldn't find an exact match for your question in our knowledge base. "
                "For deadlines, please check your Internship Offer Letter or your official "
                "CodeAlpha WhatsApp group. You can also reach support at "
                "services@codealpha.tech."
            ),
            "matched_question": None,
            "confidence": confidence_pct,
            "score": round(best_score, 4),
            "engine": "NLP Fallback",
            "suggestions": [
                "When is the submission deadline or last date for projects?",
                "How do I submit my completed project?",
                "How many tasks do I need to complete to get the certificate?",
            ],
        }

    def get_categories(self) -> List[str]:
        """Returns the sorted list of FAQ categories."""
        return sorted({f.get("category", "General") for f in self.faqs})

    def get_all_faqs(self) -> List[Dict[str, Any]]:
        """Returns the full FAQ knowledge base."""
        return self.faqs
