"""Mint and refresh an Instagram (graph.instagram.com) access token carrying
the scopes A Story of Two needs: basic + insights + comments.

This uses the *Instagram API with Instagram Login* OAuth flow. It does NOT need
App Review: Standard Access (development mode) already covers your own / tester
account. The only thing that gates insights and comments is whether the *token*
was minted with the right scopes — which this script makes explicit.

Workflow
--------
1. ``python3 scripts/instagram_token.py auth-url``
   Open the printed URL, log in as the target account, and approve the
   insights + comments permissions. Instagram redirects to your redirect URI
   with ``?code=...`` in the address bar (the page itself may fail to load —
   that's fine, you only need the URL).

2. ``python3 scripts/instagram_token.py exchange --code 'PASTE_CODE_OR_FULL_URL'``
   Exchanges the code for a short-lived token, upgrades it to a long-lived
   (~60 day) token, writes it to the env file, and prints the *granted scopes*
   so you can confirm insights + comments came through.

3. ``python3 scripts/instagram_token.py refresh``
   Extends the long-lived token (run before the 60-day expiry).

Required env keys (in .env.local, gitignored):
    INSTAGRAM_APP_ID        Instagram app ID (Instagram product, not the Meta app ID)
    INSTAGRAM_APP_SECRET    Instagram app secret
    INSTAGRAM_REDIRECT_URI  An OAuth redirect URI registered in Business Login settings
"""

from __future__ import annotations

import argparse
import json
import sys
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any, Callable
from urllib.error import HTTPError, URLError

try:
    from scripts.instagram_check import load_env_file
except ModuleNotFoundError:  # pragma: no cover - import shim for direct execution
    from instagram_check import load_env_file  # type: ignore[no-redef]


DEFAULT_SCOPES = [
    "instagram_business_basic",
    "instagram_business_manage_insights",
    "instagram_business_manage_comments",
]
AUTHORIZE_URL = "https://www.instagram.com/oauth/authorize"
SHORT_TOKEN_URL = "https://api.instagram.com/oauth/access_token"
LONG_TOKEN_URL = "https://graph.instagram.com/access_token"
REFRESH_URL = "https://graph.instagram.com/refresh_access_token"

APP_ID_KEY = "INSTAGRAM_APP_ID"
APP_SECRET_KEY = "INSTAGRAM_APP_SECRET"
REDIRECT_KEY = "INSTAGRAM_REDIRECT_URI"
TOKEN_KEY = "INSTAGRAM_ACCESS_TOKEN"
USER_ID_KEY = "INSTAGRAM_USER_ID"


class InstagramTokenError(RuntimeError):
    """Raised when an OAuth step cannot complete."""


PostForm = Callable[[str, dict[str, str]], dict[str, Any]]
GetJson = Callable[[str], dict[str, Any]]


def http_post_form(url: str, fields: dict[str, str]) -> dict[str, Any]:
    data = urllib.parse.urlencode(fields).encode("utf-8")
    request = urllib.request.Request(url, data=data, method="POST")
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.loads(response.read().decode("utf-8"))


def http_get_json(url: str) -> dict[str, Any]:
    with urllib.request.urlopen(url, timeout=30) as response:
        return json.loads(response.read().decode("utf-8"))


def build_auth_url(
    app_id: str,
    redirect_uri: str,
    scopes: list[str] | None = None,
) -> str:
    query = urllib.parse.urlencode(
        {
            "client_id": app_id,
            "redirect_uri": redirect_uri,
            "response_type": "code",
            "scope": ",".join(scopes or DEFAULT_SCOPES),
        }
    )
    return f"{AUTHORIZE_URL}?{query}"


def clean_code(code: str) -> str:
    """Accept a bare code or a full redirect URL; strip Instagram's `#_` suffix."""

    code = code.strip()
    if "code=" in code:
        parsed = urllib.parse.urlparse(code)
        params = urllib.parse.parse_qs(parsed.query)
        if "code" in params:
            code = params["code"][0]
    if code.endswith("#_"):
        code = code[:-2]
    return code


def exchange_code(
    app_id: str,
    app_secret: str,
    redirect_uri: str,
    code: str,
    post_form: PostForm = http_post_form,
    get_json: GetJson = http_get_json,
) -> dict[str, Any]:
    """Exchange an auth code for a long-lived token. Returns token + granted scopes."""

    short = post_form(
        SHORT_TOKEN_URL,
        {
            "client_id": app_id,
            "client_secret": app_secret,
            "grant_type": "authorization_code",
            "redirect_uri": redirect_uri,
            "code": clean_code(code),
        },
    )
    if "access_token" not in short:
        raise InstagramTokenError(f"Short-lived token exchange failed: {short}")

    long_lived = get_json(
        LONG_TOKEN_URL
        + "?"
        + urllib.parse.urlencode(
            {
                "grant_type": "ig_exchange_token",
                "client_secret": app_secret,
                "access_token": short["access_token"],
            }
        )
    )
    if "access_token" not in long_lived:
        raise InstagramTokenError(f"Long-lived token exchange failed: {long_lived}")

    return {
        "access_token": long_lived["access_token"],
        "expires_in": long_lived.get("expires_in"),
        "user_id": str(short["user_id"]) if short.get("user_id") is not None else None,
        "permissions": short.get("permissions"),
    }


def refresh_token(token: str, get_json: GetJson = http_get_json) -> dict[str, Any]:
    result = get_json(
        REFRESH_URL
        + "?"
        + urllib.parse.urlencode(
            {"grant_type": "ig_refresh_token", "access_token": token}
        )
    )
    if "access_token" not in result:
        raise InstagramTokenError(f"Token refresh failed: {result}")
    return result


def upsert_env_value(path: str | Path, key: str, value: str) -> None:
    """Set KEY=value in an env file, preserving other lines."""

    env_path = Path(path)
    lines = env_path.read_text(encoding="utf-8").splitlines() if env_path.exists() else []
    output: list[str] = []
    replaced = False
    for line in lines:
        if line.strip().startswith(f"{key}="):
            output.append(f"{key}={value}")
            replaced = True
        else:
            output.append(line)
    if not replaced:
        output.append(f"{key}={value}")
    env_path.write_text("\n".join(output) + "\n", encoding="utf-8")


def _require(env: dict[str, str], key: str) -> str:
    value = env.get(key)
    if not value:
        raise InstagramTokenError(f"Missing {key}. Add it to your env file first.")
    return value


def _mask(token: str) -> str:
    return f"{token[:6]}…{token[-4:]} ({len(token)} chars)" if token else "(empty)"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Instagram access token helper.")
    parser.add_argument("--env", default=".env.local", help="Env file path.")
    sub = parser.add_subparsers(dest="command", required=True)

    p_auth = sub.add_parser("auth-url", help="Print the consent URL.")
    p_auth.add_argument("--scopes", nargs="*", help="Override default scopes.")

    p_exchange = sub.add_parser("exchange", help="Exchange a code for a long-lived token.")
    p_exchange.add_argument("--code", required=True, help="Auth code or full redirect URL.")
    p_exchange.add_argument(
        "--no-write", action="store_true", help="Print only; do not update the env file."
    )

    p_refresh = sub.add_parser("refresh", help="Refresh the long-lived token.")
    p_refresh.add_argument(
        "--no-write", action="store_true", help="Print only; do not update the env file."
    )

    args = parser.parse_args(argv)
    env = load_env_file(args.env)

    try:
        if args.command == "auth-url":
            url = build_auth_url(
                _require(env, APP_ID_KEY),
                _require(env, REDIRECT_KEY),
                scopes=args.scopes,
            )
            print(url)
            return 0

        if args.command == "exchange":
            result = exchange_code(
                _require(env, APP_ID_KEY),
                _require(env, APP_SECRET_KEY),
                _require(env, REDIRECT_KEY),
                args.code,
            )
            if not args.no_write:
                upsert_env_value(args.env, TOKEN_KEY, result["access_token"])
                # Note: the OAuth response's user_id is the app-scoped id, which
                # differs from the canonical IG account id (/me?fields=user_id)
                # the rest of the pipeline uses. Don't overwrite INSTAGRAM_USER_ID.
            print(
                json.dumps(
                    {
                        "status": "ok",
                        "access_token": _mask(result["access_token"]),
                        "granted_permissions": result.get("permissions"),
                        "user_id": result.get("user_id"),
                        "expires_in_days": (
                            round(result["expires_in"] / 86400, 1)
                            if result.get("expires_in")
                            else None
                        ),
                        "written_to": None if args.no_write else args.env,
                    },
                    sort_keys=True,
                )
            )
            return 0

        if args.command == "refresh":
            result = refresh_token(_require(env, TOKEN_KEY))
            if not args.no_write:
                upsert_env_value(args.env, TOKEN_KEY, result["access_token"])
            print(
                json.dumps(
                    {
                        "status": "ok",
                        "access_token": _mask(result["access_token"]),
                        "expires_in_days": (
                            round(result["expires_in"] / 86400, 1)
                            if result.get("expires_in")
                            else None
                        ),
                        "written_to": None if args.no_write else args.env,
                    },
                    sort_keys=True,
                )
            )
            return 0
    except InstagramTokenError as error:
        print(f"instagram token error: {error}", file=sys.stderr)
        return 2
    except HTTPError as error:
        body = error.read().decode("utf-8", errors="replace")
        print(f"instagram token error: HTTP {error.code}: {body}", file=sys.stderr)
        return 1
    except (URLError, TimeoutError, json.JSONDecodeError) as error:
        print(f"instagram token error: {error}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
