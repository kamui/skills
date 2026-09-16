#!/usr/bin/env python3
"""Mint a GitHub App installation token and report the app's identity.

Usage: python3 scripts/review_token.py token --client-id ID OWNER/REPO
       python3 scripts/review_token.py whoami --client-id ID OWNER/REPO

Inputs: the app's client id, the repository the token is scoped to (always
named; never inferred from a remote), and the app's private key, resolved as
--key, then REVIEWBOT_KEY, then ~/.config/reviewbot/<client id>.pem, then
~/.config/reviewbot/key.pem. --api or REVIEWBOT_API replaces the forge base
(default https://api.github.com; a base ending in /api/v3 is GitHub
Enterprise). REVIEWBOT_CACHE_DIR replaces ~/.cache/reviewbot, where minted
tokens live under <client id>/<owner>/<repo>.json (directories 700, files
600) and are reused while more than five minutes remain; REVIEWBOT_NO_CACHE=1
always mints. No config file is read.

`token` prints the installation token, and nothing else, on stdout. `whoami`
prints the app's name and slug, its REST login (<slug>[bot]), its GraphQL
login read with the minted token, the installation id and permissions, and
the review-token command a publisher runs to obtain the token. A cached token
the probe refuses is dropped and minted again, once.

Exit 0: success.
Exit 1: the forge answered and refused: the app is not installed on the
        repository, HTTP 401/403/404, or the minted token failed the probe.
Exit 2: no answer or no local input: key missing or unreadable, openssl absent
        or refusing the key, network or TLS failure, naming the failing
        command on stderr.
Every failure reason goes to stderr; a token never reaches the argv of any
command this script runs.
"""
from __future__ import annotations

import argparse
import base64
import datetime as dt
import json
import os
import shlex
import ssl
import stat
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path

DEFAULT_API = "https://api.github.com"
CACHE_MARGIN = 300
TLS_HINT = (
    "TLS certificate verification failed; on a python.org macOS build run "
    "Install Certificates.command, or point SSL_CERT_FILE at a CA bundle"
)


class Refused(Exception):
    """The forge answered and refused: exit 1."""


class Unavailable(Exception):
    """No answer or no local input: exit 2."""


def b64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def split_repo(value: str) -> tuple[str, str]:
    owner, sep, name = value.partition("/")
    if not sep or not owner or not name or "/" in name or ".." in (owner, name):
        raise argparse.ArgumentTypeError("repository must be OWNER/REPO")
    return owner, name


def graphql_url(api: str) -> str:
    base = api.rstrip("/")
    if base.endswith("/api/v3"):
        return base[: -len("/api/v3")] + "/api/graphql"
    return base + "/graphql"


def resolve_key(option: str | None, client_id: str) -> Path:
    if option:
        candidates = [Path(option)]
    elif os.environ.get("REVIEWBOT_KEY"):
        candidates = [Path(os.environ["REVIEWBOT_KEY"])]
    else:
        config = Path("~/.config/reviewbot").expanduser()
        candidates = [config / f"{client_id}.pem", config / "key.pem"]
    for path in candidates:
        if path.is_file():
            return path
    raise Unavailable("key not found at " + " or ".join(str(p) for p in candidates))


def warn_if_shared(key: Path) -> None:
    try:
        mode = stat.S_IMODE(key.stat().st_mode)
    except OSError:
        return
    if mode & 0o077:
        print(f"review_token: warning: {key} is readable by other users; chmod 600 it", file=sys.stderr)


def app_jwt(key: Path, client_id: str) -> str:
    warn_if_shared(key)
    now = int(dt.datetime.now(dt.timezone.utc).timestamp())
    header = b64url(json.dumps({"alg": "RS256", "typ": "JWT"}, separators=(",", ":")).encode())
    claims = b64url(
        json.dumps({"iat": now - 60, "exp": now + 540, "iss": client_id}, separators=(",", ":")).encode()
    )
    signing_input = f"{header}.{claims}".encode("ascii")
    command = ["openssl", "dgst", "-sha256", "-sign", str(key)]
    try:
        with open(key, "rb"):
            pass
    except OSError as error:
        raise Unavailable(f"key unreadable at {key}: {error.strerror}") from error
    try:
        result = subprocess.run(command, input=signing_input, capture_output=True, check=False)
    except OSError as error:
        raise Unavailable(f"{shlex.join(command)} could not run: {error.strerror}") from error
    if result.returncode != 0 or not result.stdout:
        detail = result.stderr.decode("utf-8", "replace").strip().splitlines()
        reason = detail[-1] if detail else f"exit {result.returncode}"
        raise Unavailable(f"signing failed with {shlex.join(command)}: {reason} (not an app private key?)")
    return f"{header}.{claims}.{b64url(result.stdout)}"


def request(url: str, bearer: str, body: dict | None = None) -> dict:
    data = json.dumps(body).encode("utf-8") if body is not None else None
    headers = {
        "Authorization": f"Bearer {bearer}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "reviewbot",
    }
    if data is not None:
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=data, headers=headers, method="POST" if data is not None else "GET")
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            payload = response.read().decode("utf-8")
    except urllib.error.HTTPError as error:
        try:
            message = json.loads(error.read().decode("utf-8", "replace")).get("message", "")
        except (ValueError, AttributeError):
            message = ""
        raise Refused(f"forge refused {req.get_method()} {url}: HTTP {error.code}: {message or error.reason}") from error
    except urllib.error.URLError as error:
        if isinstance(error.reason, ssl.SSLCertVerificationError):
            raise Unavailable(f"{req.get_method()} {url}: {TLS_HINT}") from error
        raise Unavailable(f"{req.get_method()} {url}: network failure: {error.reason}") from error
    except (OSError, ssl.SSLError) as error:
        raise Unavailable(f"{req.get_method()} {url}: network failure: {error}") from error
    try:
        document = json.loads(payload)
    except ValueError as error:
        raise Unavailable(f"{req.get_method()} {url}: response is not JSON") from error
    if not isinstance(document, dict):
        raise Unavailable(f"{req.get_method()} {url}: response is not a JSON object")
    return document


def installation(api: str, jwt: str, owner: str, name: str) -> dict:
    try:
        return request(f"{api}/repos/{owner}/{name}/installation", jwt)
    except Refused as error:
        if "HTTP 404" in str(error):
            raise Refused(f"app not installed on {owner}/{name}") from error
        raise


def cache_path(client_id: str, owner: str, name: str) -> Path:
    root = os.environ.get("REVIEWBOT_CACHE_DIR") or "~/.cache/reviewbot"
    return Path(root).expanduser() / client_id / owner / f"{name}.json"


def cached_token(path: Path) -> str | None:
    try:
        with open(path, encoding="utf-8") as handle:
            record = json.load(handle)
        expires = dt.datetime.strptime(record["expires_at"], "%Y-%m-%dT%H:%M:%SZ")
        token = record["token"]
    except (OSError, ValueError, KeyError, TypeError):
        return None
    left = (expires.replace(tzinfo=dt.timezone.utc) - dt.datetime.now(dt.timezone.utc)).total_seconds()
    return token if isinstance(token, str) and token and left > CACHE_MARGIN else None


def write_cache(path: Path, record: dict) -> None:
    for directory in reversed(list(path.parents)):
        if directory == Path(directory.anchor) or directory.exists():
            continue
        directory.mkdir(mode=0o700)
        directory.chmod(0o700)
    part = path.with_name(path.name + ".part")
    fd = os.open(part, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(record, handle)
    except BaseException:
        part.unlink(missing_ok=True)
        raise
    part.chmod(0o600)
    os.replace(part, path)


def mint_token(
    api: str, key: Path, client_id: str, owner: str, name: str, jwt: str | None = None, install: dict | None = None
) -> str:
    path = cache_path(client_id, owner, name)
    if os.environ.get("REVIEWBOT_NO_CACHE") != "1":
        token = cached_token(path)
        if token:
            return token
    jwt = jwt or app_jwt(key, client_id)
    install = install or installation(api, jwt, owner, name)
    record = request(f"{api}/app/installations/{install['id']}/access_tokens", jwt, {"repositories": [name]})
    token = record.get("token")
    if not isinstance(token, str) or not token:
        raise Refused(f"forge refused the token exchange for {owner}/{name}: no token in the response")
    try:
        write_cache(path, record)
    except OSError as error:
        print(f"review_token: warning: cannot write the token cache at {path}: {error.strerror}", file=sys.stderr)
    return token


def cmd_token(args: argparse.Namespace) -> int:
    owner, name = args.repo
    key = resolve_key(args.key, args.client_id)
    print(mint_token(args.api, key, args.client_id, owner, name))
    return 0


def probe(api: str, token: str, origin: str) -> str:
    try:
        viewer = request(graphql_url(api), token, {"query": "{viewer{login}}"})
        return viewer["data"]["viewer"]["login"]
    except Refused as error:
        raise Refused(f"the {origin} token failed the probe: {error}") from error
    except (KeyError, TypeError) as error:
        raise Refused(f"the {origin} token failed the probe: GraphQL returned no viewer login") from error


def cmd_whoami(args: argparse.Namespace) -> int:
    owner, name = args.repo
    key = resolve_key(args.key, args.client_id)
    jwt = app_jwt(key, args.client_id)
    app = request(f"{args.api}/app", jwt)
    install = installation(args.api, jwt, owner, name)
    path = cache_path(args.client_id, owner, name)
    cached = os.environ.get("REVIEWBOT_NO_CACHE") != "1" and cached_token(path) is not None
    token = mint_token(args.api, key, args.client_id, owner, name, jwt, install)
    try:
        login = probe(args.api, token, "cached" if cached else "minted")
    except Refused as error:
        if not cached:
            raise
        print(f"review_token: warning: {error}; dropping {path} and minting again", file=sys.stderr)
        path.unlink(missing_ok=True)
        token = mint_token(args.api, key, args.client_id, owner, name, jwt, install)
        login = probe(args.api, token, "minted")
    slug = app.get("slug", "")
    permissions = install.get("permissions") or {}
    script = shlex.quote(str(Path(__file__).resolve()))
    print(f"app: {app.get('name', '')} ({slug})")
    print(f"rest login: {slug}[bot]")
    print(f"graphql login: {login}")
    print(f"installation: {install.get('id', '')} on {owner}/{name}")
    print("permissions: " + (", ".join(f"{k}: {v}" for k, v in sorted(permissions.items())) or "none"))
    print(f"review-token command: python3 {script} token --client-id {shlex.quote(args.client_id)} {owner}/{name}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Mint a GitHub App installation token or report the app's identity.")
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--client-id", required=True, help="the app's client id, the JWT issuer")
    common.add_argument("--key", help="private key path; else REVIEWBOT_KEY, then ~/.config/reviewbot")
    common.add_argument(
        "--api",
        default=os.environ.get("REVIEWBOT_API") or DEFAULT_API,
        help="forge REST base; GitHub Enterprise uses https://<host>/api/v3",
    )
    common.add_argument("repo", type=split_repo, metavar="OWNER/REPO", help="the repository the token is scoped to")
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("token", parents=[common], help="print an installation token on stdout").set_defaults(run=cmd_token)
    subparsers.add_parser("whoami", parents=[common], help="report the app, its logins, and the installation").set_defaults(
        run=cmd_whoami
    )
    args = parser.parse_args(argv)
    args.api = args.api.rstrip("/")
    try:
        return args.run(args)
    except Refused as error:
        print(f"review_token: {error}", file=sys.stderr)
        return 1
    except Unavailable as error:
        print(f"review_token: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
