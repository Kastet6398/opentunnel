"""Command-line client for RouteTunnel backend.

Provides simple commands:
- register
- login
- create-tunnel
- connect  (connects a local HTTP server to the tunnel via WebSocket token and forwards requests)

This is a lightweight helper that uses httpx and websockets. It stores auth tokens in
~/.routetunnel_auth.json when logging in.
"""

import argparse
import asyncio
import base64
import json
import os
import sys
import time
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse, urlunparse, urlencode

import httpx
import websockets

TOKEN_STORE = os.path.expanduser("~/.routetunnel_auth.json")


def save_tokens(data: Dict[str, Any]) -> None:
    try:
        with open(TOKEN_STORE, "w") as f:
            json.dump(data, f)
        print(f"Saved tokens to {TOKEN_STORE}")
    except Exception as exc:
        print("Failed to save tokens:", exc)


def load_tokens() -> Optional[Dict[str, Any]]:
    try:
        with open(TOKEN_STORE, "r") as f:
            return json.load(f)
    except Exception:
        return None


async def register(api_base: str, email: str, phone: str, password: str) -> None:
    url = api_base.rstrip("/") + "/api/auth/register"
    async with httpx.AsyncClient() as client:
        resp = await client.post(url, json={"email": email, "phone_number": phone, "password": password})
        if resp.status_code >= 400:
            print("Register failed:", resp.status_code, resp.text)
            sys.exit(1)
        print("Registered successfully. You can now login.")


async def login(api_base: str, email: str, password: str) -> None:
    url = api_base.rstrip("/") + "/api/auth/login"
    async with httpx.AsyncClient() as client:
        resp = await client.post(url, json={"email": email, "password": password})
        if resp.status_code >= 400:
            print("Login failed:", resp.status_code, resp.text)
            sys.exit(1)
        data = resp.json()
        save_tokens(data)
        print("Login successful.")


async def create_tunnel(api_base: str, route: str, description: Optional[str], is_public: bool = False) -> None:
    tokens = load_tokens()
    if not tokens or "access_token" not in tokens:
        print("No access token found. Please login first.")
        sys.exit(1)

    url = api_base.rstrip("/") + "/api/tunnels"
    headers = {"Authorization": f"Bearer {tokens['access_token']}"}
    payload = {"route": route, "is_public": is_public}
    if description:
        payload["description"] = description

    async with httpx.AsyncClient() as client:
        resp = await client.post(url, json=payload, headers=headers)
        if resp.status_code >= 400:
            print("Create tunnel failed:", resp.status_code, resp.text)
            sys.exit(1)
        data = resp.json()
        print(json.dumps(data, indent=2))


async def forward_request_to_local(local_base: str, request_msg: Dict[str, Any]) -> Dict[str, Any]:
    method = request_msg.get("method", "GET")
    path = request_msg.get("path", "/")
    query = request_msg.get("query", {})
    headers = request_msg.get("headers", {}) or {}
    body_b64 = request_msg.get("body_b64")
    body = base64.b64decode(body_b64.encode("ascii")) if body_b64 else None

    # Build URL
    local_base = local_base.rstrip("/")
    url = local_base + path

    # Convert query (dict of lists) into simple params dict for httpx
    params: List[tuple] = []
    for k, v in query.items():
        if isinstance(v, list):
            for item in v:
                params.append((k, item))
        else:
            params.append((k, v))

    # Remove hop-by-hop headers that may confuse local server
    headers.pop("host", None)
    headers.pop("connection", None)

    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            resp = await client.request(method, url, params=params or None, headers=headers or None, content=body)
        except Exception as exc:
            # Return 502 to registry if local server is unreachable
            return {
                "status_code": 502,
                "headers": {"content-type": "text/plain"},
                "body_b64": base64.b64encode(str(exc).encode("utf-8")).decode("ascii")
            }

    # Prepare response to send back over websocket
    resp_headers = {k: v for k, v in resp.headers.items()} if resp.headers else {}
    body_b64 = base64.b64encode(resp.content).decode("ascii") if resp.content else None

    return {
        "status_code": resp.status_code,
        "headers": resp_headers,
        "body_b64": body_b64,
    }


async def run_connector(ws_url: str, local_base: str, token: Optional[str] = None) -> None:
    """Connect to tunnel WebSocket and forward incoming requests to local server."""
    reconnect_delay = 1
    while True:
        try:
            print(f"Connecting to {ws_url} ...")
            async with websockets.connect(ws_url) as ws:
                print("Connected. Waiting for requests...")
                reconnect_delay = 1
                async for raw in ws:
                    try:
                        msg = json.loads(raw)
                    except Exception:
                        # ignore non-json messages
                        continue

                    mtype = msg.get("type")
                    if mtype == "ping":
                        # reply with pong
                        try:
                            await ws.send(json.dumps({"type": "pong", "ts": time.time()}))
                        except Exception:
                            pass
                        continue

                    if mtype == "request":
                        correlation_id = msg.get("correlation_id")
                        resp_payload = await forward_request_to_local(local_base, msg)
                        resp_payload["type"] = "response"
                        resp_payload["correlation_id"] = correlation_id
                        try:
                            await ws.send(json.dumps(resp_payload))
                        except Exception:
                            print("Failed to send response for", correlation_id)
                            # websocket may be closed - break to reconnect
                            break

        except websockets.exceptions.ConnectionClosed as exc:
            print("Connection closed:", exc)
        except Exception as exc:
            print("Connection error:", exc)

        print(f"Reconnecting in {reconnect_delay}s...")
        await asyncio.sleep(reconnect_delay)
        reconnect_delay = min(reconnect_delay * 2, 30)


def build_ws_url(ws_base: str, token: str, api_base: Optional[str] = None) -> str:
    """Build a correct WebSocket URL for the tunnel endpoint.

    - If the provided ws_base contains no path (just host[:port]), assume the
      websocket endpoint is under the API prefix "/api/tunnels" and build
      e.g. ws://host:port/api/tunnels/ws/tunnel?token=... .
    - If ws_base already contains a path, append "/ws/tunnel" to that path.
    - Accept http(s) schemes and convert them to ws(s).
    """
    ws_base = ws_base.rstrip("/")
    parsed = urlparse(ws_base)

    scheme = parsed.scheme
    netloc = parsed.netloc or parsed.path  # in case someone passed 'localhost:8000'
    path = parsed.path if parsed.path and parsed.path != "" else ""

    # Convert http(s) to ws(s)
    if scheme == "http":
        scheme = "ws"
    elif scheme == "https":
        scheme = "wss"
    elif scheme in ("ws", "wss", ""):  # keep ws/wss or empty
        # leave as-is; if empty, default to ws
        if scheme == "":
            scheme = "ws"

    # Decide base path: if no meaningful path provided, try to derive from api_base
    if not path or path == "/":
        # prefer api_base if passed and contains a path
        if api_base:
            parsed_api = urlparse(api_base.rstrip("/"))
            api_path = parsed_api.path.rstrip('/')
            base_path = api_path if api_path and api_path != '/' else '/api/tunnels'
        else:
            base_path = '/api/tunnels'
    else:
        base_path = path.rstrip('/')

    full_path = f"{base_path}/ws/tunnel"
    query = urlencode({"token": token})

    built = urlunparse((scheme, netloc, full_path, '', query, ''))
    return built


def main():
    parser = argparse.ArgumentParser(prog="routetunnelctl", description="RouteTunnel CLI")
    parser.add_argument("--api", default=os.getenv("API_BASE_URL", "http://localhost:8000"), help="API base URL")
    parser.add_argument("--ws", default=os.getenv("WS_BASE_URL", "ws://localhost:8000"), help="WebSocket base URL")

    sub = parser.add_subparsers(dest="cmd")

    reg = sub.add_parser("register", help="Register a new user")
    reg.add_argument("email")
    reg.add_argument("phone")
    reg.add_argument("password")

    log = sub.add_parser("login", help="Login and store tokens")
    log.add_argument("email")
    log.add_argument("password")

    ct = sub.add_parser("create-tunnel", help="Create a new tunnel")
    ct.add_argument("route")
    ct.add_argument("-d", "--description", default=None)
    ct.add_argument("--public", action="store_true", help="Make the tunnel public")

    connect = sub.add_parser("connect", help="Connect local server to tunnel using token")
    connect.add_argument("--token", default=None, help="Tunnel token (if not provided will read from create-tunnel output or env)")
    connect.add_argument("--local", default=os.getenv("LOCAL_BASE", "http://localhost:8000"), help="Local base URL to forward requests to")
    connect.add_argument("--ws-url", default=None, help="Full websocket URL to use (overrides --ws and --token)")

    args = parser.parse_args()

    if args.cmd == "register":
        asyncio.run(register(args.api, args.email, args.phone, args.password))
        return

    if args.cmd == "login":
        asyncio.run(login(args.api, args.email, args.password))
        return

    if args.cmd == "create-tunnel":
        asyncio.run(create_tunnel(args.api, args.route, args.description, args.public))
        return

    if args.cmd == "connect":
        token = args.token
        if not token:
            # Try token from stored tokens (some responses may include token)
            tokens = load_tokens()
            if tokens and "token" in tokens:
                token = tokens["token"]
        if args.ws_url:
            ws_url = args.ws_url
        else:
            if not token:
                print("No token provided. Provide --token or ensure create-tunnel output includes token or set the token in command.")
                sys.exit(1)
            # Pass api base so builder can infer /api/tunnels path when needed
            ws_url = build_ws_url(args.ws, token, api_base=args.api)

        try:
            asyncio.run(run_connector(ws_url, args.local, token))
        except KeyboardInterrupt:
            print("Exiting...")
            return

    parser.print_help()


if __name__ == "__main__":
    main()
