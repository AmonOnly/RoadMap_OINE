import json
import unittest

from web.app import app


class WebApiTests(unittest.TestCase):
    def setUp(self) -> None:
        self.client = app.test_client()

    def test_daily_plan(self) -> None:
        response = self.client.get("/api/daily-plan?hours=2&days=5")
        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertIn("days", payload)
        self.assertEqual(len(payload["days"]), 5)

    def test_quiz_endpoint(self) -> None:
        response = self.client.get("/api/quiz?hours=2")
        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertIn("questions", payload)

    def test_complete_day_validation(self) -> None:
        response = self.client.post(
            "/api/complete-day",
            data=json.dumps({}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)


if __name__ == "__main__":
    unittest.main()
