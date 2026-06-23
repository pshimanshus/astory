import tempfile
import unittest
from pathlib import Path

from scripts import instagram_token


class InstagramTokenTests(unittest.TestCase):
    def test_build_auth_url_includes_all_scopes_and_params(self):
        url = instagram_token.build_auth_url("APP123", "https://localhost/")

        self.assertTrue(url.startswith(instagram_token.AUTHORIZE_URL))
        self.assertIn("client_id=APP123", url)
        self.assertIn("response_type=code", url)
        self.assertIn("instagram_business_basic", url)
        self.assertIn("instagram_business_manage_insights", url)
        self.assertIn("instagram_business_manage_comments", url)

    def test_clean_code_strips_hash_suffix(self):
        self.assertEqual(instagram_token.clean_code("ABC123#_"), "ABC123")

    def test_clean_code_extracts_from_full_redirect_url(self):
        url = "https://localhost/?code=ABC123#_"
        self.assertEqual(instagram_token.clean_code(url), "ABC123")

    def test_exchange_code_upgrades_to_long_lived_token(self):
        posted = {}
        got = {}

        def fake_post_form(url, fields):
            posted["url"] = url
            posted["fields"] = fields
            return {"access_token": "short-token", "user_id": 17841442026478504,
                    "permissions": ["instagram_business_basic",
                                    "instagram_business_manage_insights",
                                    "instagram_business_manage_comments"]}

        def fake_get_json(url):
            got["url"] = url
            return {"access_token": "long-token", "token_type": "bearer",
                    "expires_in": 5184000}

        result = instagram_token.exchange_code(
            "APP123", "SECRET", "https://localhost/", "CODE#_",
            post_form=fake_post_form, get_json=fake_get_json,
        )

        self.assertEqual(result["access_token"], "long-token")
        self.assertEqual(result["user_id"], "17841442026478504")
        self.assertEqual(result["expires_in"], 5184000)
        self.assertIn("instagram_business_manage_insights", result["permissions"])
        # short-lived exchange must use the cleaned code
        self.assertEqual(posted["fields"]["code"], "CODE")
        self.assertIn("ig_exchange_token", got["url"])

    def test_exchange_code_raises_when_short_token_missing(self):
        def fake_post_form(url, fields):
            return {"error_type": "OAuthException", "error_message": "bad code"}

        with self.assertRaises(instagram_token.InstagramTokenError):
            instagram_token.exchange_code(
                "APP123", "SECRET", "https://localhost/", "CODE",
                post_form=fake_post_form, get_json=lambda url: {},
            )

    def test_refresh_token_returns_new_token(self):
        result = instagram_token.refresh_token(
            "long-token",
            get_json=lambda url: {"access_token": "refreshed", "expires_in": 5184000},
        )
        self.assertEqual(result["access_token"], "refreshed")

    def test_upsert_env_value_updates_existing_and_adds_missing(self):
        with tempfile.TemporaryDirectory() as tmp:
            env_path = Path(tmp) / ".env.local"
            env_path.write_text(
                "INSTAGRAM_ACCESS_TOKEN=old\nINSTAGRAM_USERNAME=a.storyof.two\n",
                encoding="utf-8",
            )

            instagram_token.upsert_env_value(env_path, "INSTAGRAM_ACCESS_TOKEN", "new")
            instagram_token.upsert_env_value(env_path, "INSTAGRAM_USER_ID", "123")

            text = env_path.read_text(encoding="utf-8")
            self.assertIn("INSTAGRAM_ACCESS_TOKEN=new", text)
            self.assertIn("INSTAGRAM_USERNAME=a.storyof.two", text)
            self.assertIn("INSTAGRAM_USER_ID=123", text)
            self.assertNotIn("INSTAGRAM_ACCESS_TOKEN=old", text)


if __name__ == "__main__":
    unittest.main()
