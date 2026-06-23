import json
import tempfile
import unittest
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from scripts import instagram_check


class InstagramCheckTests(unittest.TestCase):
    def test_load_env_file_reads_instagram_settings(self):
        with tempfile.TemporaryDirectory() as tmp:
            env_path = Path(tmp) / ".env.local"
            env_path.write_text(
                "\n".join(
                    [
                        "# local secrets",
                        "INSTAGRAM_ACCESS_TOKEN=secret-token",
                        "INSTAGRAM_USER_ID=17841442026478504",
                        "INSTAGRAM_USERNAME=a.storyof.two",
                        "OTHER_VALUE=left-alone",
                        "",
                    ]
                ),
                encoding="utf-8",
            )

            env = instagram_check.load_env_file(env_path)

        self.assertEqual(env["INSTAGRAM_ACCESS_TOKEN"], "secret-token")
        self.assertEqual(env["INSTAGRAM_USER_ID"], "17841442026478504")
        self.assertEqual(env["INSTAGRAM_USERNAME"], "a.storyof.two")
        self.assertEqual(env["OTHER_VALUE"], "left-alone")

    def test_check_profile_calls_graph_me_without_returning_token(self):
        requested_urls = []

        def fake_get_json(url):
            requested_urls.append(url)
            return {
                "id": "27742535022021073",
                "user_id": "17841442026478504",
                "username": "a.storyof.two",
            }

        result = instagram_check.check_profile(
            {"INSTAGRAM_ACCESS_TOKEN": "secret-token"},
            get_json=fake_get_json,
        )

        parsed = urlparse(requested_urls[0])
        query = parse_qs(parsed.query)

        self.assertEqual(parsed.netloc, "graph.instagram.com")
        self.assertEqual(parsed.path, "/me")
        self.assertEqual(query["fields"], ["user_id,username"])
        self.assertEqual(query["access_token"], ["secret-token"])
        self.assertEqual(result["username"], "a.storyof.two")
        self.assertEqual(result["user_id"], "17841442026478504")
        self.assertNotIn("secret-token", json.dumps(result))


if __name__ == "__main__":
    unittest.main()
