import random
import unittest
from unittest.mock import patch

import requests

from questions import Question, avaliar_resposta, fetch_questions


class QuestionsTests(unittest.TestCase):
    @patch("questions.requests.get", side_effect=requests.RequestException)
    def test_fallback_quando_sem_internet(self, _mock_get) -> None:
        rng = random.Random(4)
        questions, source = fetch_questions(amount=3, rng=rng)
        self.assertEqual(source, "offline")
        self.assertEqual(len(questions), 3)
        self.assertIsInstance(questions[0], Question)

    def test_avaliacao_resposta(self) -> None:
        question = Question(
            prompt="Teste",
            options=("A", "B", "C", "D"),
            correct="B",
        )
        correto, feedback = avaliar_resposta(question, "B")
        self.assertTrue(correto)
        self.assertIn("Correto", feedback)

        correto, feedback = avaliar_resposta(question, "A")
        self.assertFalse(correto)
        self.assertIn("Incorreto", feedback)


if __name__ == "__main__":
    unittest.main()
