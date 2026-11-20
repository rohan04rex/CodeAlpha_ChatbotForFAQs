"""
Unit tests for CodeAlpha FAQ Chatbot.

Covers NLP preprocessing, cosine-similarity matching, the local fallback path,
and all Flask REST endpoints. No external services or API keys are required.
"""

import unittest

from app import app
from chatbot_engine import FAQChatbotEngine, preprocess_text


class TestFAQChatbotEngine(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.engine = FAQChatbotEngine()

    def test_preprocessing(self):
        """Text normalization, stopword filtering and lemmatization."""
        cleaned = preprocess_text("Submitting multiple completed tasks!")
        self.assertIn("submit", cleaned)
        self.assertIn("task", cleaned)
        self.assertNotIn("!", cleaned)

    def test_greeting_handling(self):
        res = self.engine.find_best_match("Hello")
        self.assertEqual(res["status"], "greeting")
        self.assertIn("CodeAlpha", res["answer"])

    def test_github_naming_match(self):
        res = self.engine.find_best_match("What should be my github repo name?")
        self.assertEqual(res["status"], "matched")
        self.assertIn("CodeAlpha_ProjectName", res["answer"])
        self.assertGreater(res["confidence"], 40.0)

    def test_submission_form_match(self):
        res = self.engine.find_best_match("How can I submit my project?")
        self.assertEqual(res["status"], "matched")
        self.assertIn("submission form", res["answer"].lower())

    def test_certificate_criteria_match(self):
        res = self.engine.find_best_match("How many tasks are needed for certificate?")
        self.assertEqual(res["status"], "matched")
        self.assertIn("two (2) or three (3) tasks", res["answer"])

    def test_perks_match(self):
        res = self.engine.find_best_match("What are the benefits or perks?")
        self.assertEqual(res["status"], "matched")
        self.assertIn("Offer Letter", res["answer"])

    def test_answer_comes_from_knowledge_base(self):
        """Matched answers are deterministic FAQ text, not generated content."""
        res = self.engine.find_best_match("What is the official CodeAlpha website URL?")
        self.assertEqual(res["status"], "matched")
        self.assertEqual(res["answer"], "The official CodeAlpha website is https://www.codealpha.tech.")
        self.assertEqual(res["category"], "Contact & Support")

    def test_unrelated_query_fallback(self):
        res = self.engine.find_best_match("What is the recipe for chocolate cake?")
        answer_lower = res["answer"].lower()
        self.assertEqual(res["status"], "fallback")
        self.assertTrue(
            "couldn't find" in answer_lower or "sorry" in answer_lower,
            f"Unexpected fallback response: {res['answer']}",
        )

    def test_empty_query(self):
        res = self.engine.find_best_match("   ")
        self.assertEqual(res["status"], "empty")

    def test_categories_are_sorted_and_unique(self):
        categories = self.engine.get_categories()
        self.assertEqual(categories, sorted(set(categories)))


class TestFAQChatbotAPI(unittest.TestCase):
    def setUp(self):
        self.app = app
        self.app.config["TESTING"] = True
        self.client = self.app.test_client()

    def test_index_route(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"CodeAlpha", response.data)
        self.assertIn(b"FAQ Assistant", response.data)

    def test_chat_api_success(self):
        response = self.client.post("/api/chat", json={"message": "Hello"})
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data["status"], "success")
        self.assertEqual(data["data"]["status"], "greeting")

    def test_chat_api_with_history(self):
        response = self.client.post("/api/chat", json={
            "message": "What is the required GitHub repository naming format?",
            "history": [{"role": "user", "text": "hello"}],
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn("CodeAlpha_ProjectName", response.get_json()["data"]["answer"])

    def test_chat_api_empty_message(self):
        response = self.client.post("/api/chat", json={"message": "   "})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.get_json()["status"], "error")

    def test_faqs_api(self):
        response = self.client.get("/api/faqs")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.get_json()["faqs"]), 27)

    def test_faqs_api_with_category_filter(self):
        response = self.client.get("/api/faqs?category=Internship%20Rules")
        data = response.get_json()
        self.assertEqual(data["status"], "success")
        self.assertTrue(data["faqs"])
        self.assertTrue(all(f["category"] == "Internship Rules" for f in data["faqs"]))

    def test_categories_api(self):
        response = self.client.get("/api/categories")
        self.assertEqual(response.status_code, 200)
        self.assertIn("Internship Rules", response.get_json()["categories"])

    def test_health_api(self):
        response = self.client.get("/api/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["status"], "success")


if __name__ == "__main__":
    unittest.main(verbosity=2)
