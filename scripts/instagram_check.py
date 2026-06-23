"""Verify the local Instagram Graph API token without printing it."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any, Callable
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import urlopen


GRAPH_ME_URL = "https://graph.instagram.com/me"
TOKEN_ENV_KEY = "INSTAGRAM_ACCESS_TOKEN"


class InstagramCheckError(RuntimeError):
    """Raised when local Instagram token verification cannot run."""


def load_env_file(path: str | Path) -> dict[str, str]:
    """Load simple KEY=VALUE lines from an env file."""

    env_path = Path(path)
    values: dict[str, str] = {}
    if not env_path.exists():
        return values

    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip()
        if not key:
            continue
        if len(value) >= 2 and value[0] == value[-1] and value[0] in {'"', "'"}:
            value = value[1:-1]
        values[key] = value

    return values


def build_profile_url(access_token: str) -> str:
    query = urlencode(
        {
            "fields": "user_id,username",
            "access_token": access_token,
        }
    )
    return f"{GRAPH_ME_URL}?{query}"


def fetch_json(url: str) -> dict[str, Any]:
    with urlopen(url, timeout=15) as response:
        body = response.read().decode("utf-8")
    return json.loads(body)


def check_profile(
    env: dict[str, str],
    get_json: Callable[[str], dict[str, Any]] = fetch_json,
) -> dict[str, Any]:
    access_token = env.get(TOKEN_ENV_KEY)
    if not access_token:
        raise InstagramCheckError(
            f"Missing {TOKEN_ENV_KEY}. Save it in .env.local or export it first."
        )

    profile = get_json(build_profile_url(access_token))
    username = profile.get("username")
    user_id = profile.get("user_id")
    if not username or not user_id:
        raise InstagramCheckError("Instagram /me response did not include username and user_id.")

    result = {
        "status": "ok",
        "username": username,
        "user_id": user_id,
    }
    if "id" in profile:
        result["id"] = profile["id"]
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Verify INSTAGRAM_ACCESS_TOKEN from .env.local."
    )
    parser.add_argument(
        "--env",
        default=".env.local",
        help="Path to env file. Defaults to .env.local.",
    )
    args = parser.parse_args(argv)

    env = dict(os.environ)
    env.update(load_env_file(args.env))

    try:
        result = check_profile(env)
    except InstagramCheckError as error:
        print(f"instagram check failed: {error}", file=sys.stderr)
        return 2
    except HTTPError as error:
        body = error.read().decode("utf-8", errors="replace")
        print(f"instagram check failed: HTTP {error.code}: {body}", file=sys.stderr)
        return 1
    except (URLError, TimeoutError, json.JSONDecodeError) as error:
        print(f"instagram check failed: {error}", file=sys.stderr)
        return 1

    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
