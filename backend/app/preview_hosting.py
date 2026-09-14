"""Explicit local/cloud boundary; never trust a client-supplied forwarded host."""

import asyncio
import ipaddress
import os
import re
from dataclasses import dataclass
from urllib.parse import urlsplit

from starlette.responses import JSONResponse

PAGES_ORIGIN = "https://nricl.github.io"
MAX_INFLIGHT = 16
MAX_BODY_BYTES = 65536
SECURITY_HEADERS = {
    "Cache-Control": "no-store",
    "Referrer-Policy": "no-referrer",
    "X-Content-Type-Options": "nosniff",
}


def local_origin(value: str) -> str:
    parsed = urlsplit(value)
    if (parsed.scheme != "http" or parsed.hostname not in {"127.0.0.1", "localhost", "::1"}
            or parsed.username or parsed.password or parsed.path not in ("", "/")
            or parsed.query or parsed.fragment or parsed.port is None
            or not 1024 <= parsed.port <= 65535):
        raise ValueError("Configure an explicit HTTP loopback origin and port for the local preview.")
    return f"http://{parsed.netloc}"


def https_origin(value: str) -> str:
    parsed = urlsplit(value)
    if (parsed.scheme != "https" or not parsed.hostname or parsed.username or parsed.password
            or parsed.port not in (None, 443) or parsed.path not in ("", "/")
            or parsed.query or parsed.fragment or parsed.netloc != parsed.hostname
            or not re.fullmatch(r"[a-z0-9]+(?:[a-z0-9.-]*[a-z0-9])?", parsed.hostname)
            or "." not in parsed.hostname):
        raise ValueError("Configure an explicit HTTPS origin without credentials, port or path.")
    return f"https://{parsed.hostname}"


def application_url(value: str, allowed_origins: set[str], *, cloud: bool = False) -> str:
    parsed = urlsplit(value)
    origin = (https_origin if cloud else local_origin)(f"{parsed.scheme}://{parsed.netloc}")
    if (origin not in allowed_origins or parsed.query or parsed.fragment
            or not re.fullmatch(r"/[A-Za-z0-9_/-]+", parsed.path)
            or "//" in parsed.path):
        raise ValueError("Configure an application URL with an allowlisted origin and a plain absolute path.")
    return origin + parsed.path


@dataclass(frozen=True)
class HostingPolicy:
    mode: str
    own_origin: str
    frontend_origin: str
    cors_origins: frozenset[str]
    app_url: str
    trusted_proxies: tuple

    @classmethod
    def from_environment(cls, backend_origin=None):
        mode = os.environ.get("AVIA_PREVIEW_HOSTING", "local")
        if mode not in {"local", "azure_test"}:
            raise ValueError("AVIA_PREVIEW_HOSTING must be local or azure_test; no fallback.")
        cloud = mode == "azure_test"
        validator = https_origin if cloud else local_origin
        own = validator(backend_origin or os.environ.get(
            "AVIA_PREVIEW_ORIGIN", "" if cloud else "http://127.0.0.1:8767"))
        frontend = validator(os.environ.get(
            "AVIA_PREVIEW_FRONTEND_ORIGIN", "" if cloud else "http://127.0.0.1:4178"))
        cors = {frontend, PAGES_ORIGIN} if cloud else {own, frontend}
        app_url = application_url(os.environ.get(
            "AVIA_PREVIEW_APP_URL", "" if cloud else frontend + "/preview"),
            cors | {own}, cloud=cloud)
        proxies = ()
        if cloud:
            raw = os.environ.get("AVIA_PREVIEW_TRUSTED_PROXY_CIDRS", "")
            try:
                proxies = tuple(ipaddress.ip_network(value.strip()) for value in raw.split(","))
                if any(network.prefixlen == 0 for network in proxies):
                    raise ValueError()
            except ValueError:
                raise ValueError("azure_test requires explicit trusted ingress IPs/CIDRs; wildcard trust is forbidden.") from None
        return cls(mode, own, frontend, frozenset(cors), app_url, proxies)

    def rejection(self, scope):
        headers = {}
        for key, value in scope["headers"]:
            key = key.decode("latin-1").lower()
            if key in headers and key in {"host", "origin", "x-forwarded-proto", "sec-fetch-site"}:
                return "invalid_headers"
            headers[key] = value.decode("latin-1")
        host = headers.get("host", "")
        origin = headers.get("origin")
        client = (scope.get("client") or ("", 0))[0]
        if self.mode == "local":
            try:
                hostname = urlsplit("http://" + host).hostname
            except ValueError:
                return "local_only"
            if hostname not in {"127.0.0.1", "localhost", "::1", "testserver"} or client not in {
                    "127.0.0.1", "::1", "testclient"}:
                return "local_only"
            if origin and origin not in self.cors_origins or headers.get("sec-fetch-site") == "cross-site":
                return "origin_not_allowed"
        else:
            # Azure ingress preserves Host. X-Forwarded-Host/Forwarded never authorize a host.
            if host != urlsplit(self.own_origin).netloc:
                return "host_not_allowed"
            if origin is not None and origin not in self.cors_origins | {self.own_origin}:
                return "origin_not_allowed"
            bearer_document_navigation = (
                origin is None and scope.get("method") in {"GET", "HEAD"}
                and re.fullmatch(r"/preview/parcours/[0-9a-f]{32}", scope.get("path", "")) is not None
                and headers.get("sec-fetch-mode") == "navigate"
                and headers.get("sec-fetch-dest") == "document"
            )
            if (headers.get("sec-fetch-site") == "cross-site" and origin not in self.cors_origins
                    and not bearer_document_navigation):
                return "origin_not_allowed"
            if scope.get("scheme") != "https":
                try:
                    trusted = any(ipaddress.ip_address(client) in network for network in self.trusted_proxies)
                except ValueError:
                    trusted = False
                if not trusted or headers.get("x-forwarded-proto") != "https":
                    return "https_required"
        return None


class PreviewBoundary:
    """Bound active work/body buffering, including callers waiting on the session lock."""

    def __init__(self, app, policy: HostingPolicy):
        self.app, self.policy, self.inflight = app, policy, 0

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            return await self.app(scope, receive, send)

        async def secured_send(message):
            if message["type"] == "http.response.start":
                names = {key.lower().encode() for key in SECURITY_HEADERS}
                message["headers"] = [(key, value) for key, value in message.get("headers", [])
                                      if key.lower() not in names]
                message["headers"] += [(key.lower().encode(), value.encode())
                                       for key, value in SECURITY_HEADERS.items()]
            await send(message)

        async def error(code, status):
            origin = next((value.decode("latin-1") for key, value in scope["headers"] if key == b"origin"), None)
            headers = {"Access-Control-Allow-Origin": origin, "Vary": "Origin"} if origin in self.policy.cors_origins else {}
            await JSONResponse({"error": code}, status_code=status, headers=headers)(scope, receive, secured_send)

        rejected = self.policy.rejection(scope)
        if rejected:
            return await error(rejected, 403)
        if scope["path"] == "/health" and scope["method"] in {"GET", "HEAD", "OPTIONS"}:
            return await self.app(scope, receive, secured_send)
        if self.inflight >= MAX_INFLIGHT:
            return await error("capacity", 429)
        self.inflight += 1
        try:
            async def read_body():
                data = bytearray()
                while True:
                    message = await receive()
                    if message["type"] == "http.disconnect":
                        return None
                    chunk = message.get("body", b"")
                    if len(data) + len(chunk) > MAX_BODY_BYTES:
                        raise ValueError()
                    data.extend(chunk)
                    if not message.get("more_body", False):
                        return bytes(data)
            try:
                body = await asyncio.wait_for(read_body(), timeout=15)
            except ValueError:
                return await error("request_too_large", 413)
            except asyncio.TimeoutError:
                return await error("request_timeout", 408)
            if body is None:
                return
            delivered = False

            async def bounded_receive():
                nonlocal delivered
                if not delivered:
                    delivered = True
                    return {"type": "http.request", "body": body, "more_body": False}
                return await receive()
            return await self.app(scope, bounded_receive, secured_send)
        finally:
            self.inflight -= 1
