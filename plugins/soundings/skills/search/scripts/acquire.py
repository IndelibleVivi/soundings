#!/usr/bin/env python3
"""Fetch one explicitly selected public text URL into an inquiry workspace.

Discovery and interactive/media observation remain with the host's existing
tools. This helper performs a bounded GET without cookies or credentials. It
retains the decoded response beside any HTML text extraction; it is not a
browser, search backend, source authenticator, or automatic refresh service.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from html.parser import HTMLParser
import ipaddress
import math
from pathlib import Path
import socket
import sys
import tempfile
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import HTTPRedirectHandler, ProxyHandler, Request, build_opener

from evidence import EvidenceError, encode


TEXT_TYPES = {"application/json", "application/xml", "application/xhtml+xml"}
HTML_TYPES = {"text/html", "application/xhtml+xml"}
MAX_SOURCE_BYTES = 2 * 1024 * 1024


@dataclass(frozen=True)
class AcquiredText:
    requested_url: str
    url: str
    title: str
    content_type: str
    charset: str
    raw_text: str
    text: str
    omissions: tuple[str, ...]


class TextExtractor(HTMLParser):
    """A visible text approximation; retain the HTML as its separate basis."""

    BLOCKS = {"p", "div", "section", "article", "header", "footer", "nav", "aside",
              "h1", "h2", "h3", "h4", "h5", "h6", "li", "ul", "ol", "blockquote",
              "pre", "table", "tr", "dl", "dt", "dd", "figure", "figcaption", "br", "hr"}
    OMIT = {"script", "style", "template"}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []
        self.title_parts: list[str] = []
        self.in_title = False
        self.first_title = True
        self.omitted: set[str] = set()
        self.hidden: list[str] = []

    def handle_starttag(self, tag, attrs):
        if self.hidden:
            if tag == self.hidden[-1]:
                self.hidden.append(tag)
            return
        if tag in self.OMIT:
            self.hidden.append(tag)
            self.omitted.add(tag)
        elif tag == "title":
            self.in_title = True
            self.first_title = not self.title_parts
        elif tag in self.BLOCKS:
            self.parts.append("\n")
        elif tag in {"td", "th"}:
            self.parts.append("\t")
        elif tag == "img":
            alt = dict(attrs).get("alt")
            if alt:
                self.parts.append(" [image alt: " + alt + "] ")

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        self.handle_endtag(tag)

    def handle_endtag(self, tag):
        if self.hidden:
            if tag == self.hidden[-1]:
                self.hidden.pop()
            return
        if tag == "title":
            self.in_title = False
        elif tag in self.BLOCKS:
            self.parts.append("\n")

    def handle_data(self, data):
        if self.hidden:
            return
        if self.in_title and self.first_title:
            self.title_parts.append(data)
        else:
            self.parts.append(data)

    def result(self):
        # Preserve short lines, table row boundaries, footnote text and preformatted
        # spacing. Blank-line compression is presentation, never completeness.
        text = "\n".join(line.rstrip() for line in "".join(self.parts).splitlines())
        while "\n\n\n" in text:
            text = text.replace("\n\n\n", "\n\n")
        return text.strip(), " ".join("".join(self.title_parts).split()), tuple(sorted(self.omitted))


def validate_url(url: str, *, allow_http=False, allow_private_network=False) -> str:
    try:
        parsed = urlsplit(url)
        port = parsed.port
    except ValueError as exc:
        raise EvidenceError(f"invalid URL: {exc}") from exc
    if parsed.scheme not in ({"https", "http"} if allow_http else {"https"}):
        raise EvidenceError("use an HTTPS URL (explicit --allow-http permits HTTP)")
    if not parsed.hostname or parsed.username is not None or parsed.password is not None:
        raise EvidenceError("a URL must have a host and must not contain credentials")
    if any(ord(char) < 33 or ord(char) == 127 for char in url) or "\\" in url:
        raise EvidenceError("URL contains a control character, whitespace, or backslash")
    try:
        addresses = socket.getaddrinfo(parsed.hostname, port or (443 if parsed.scheme == "https" else 80),
                                       type=socket.SOCK_STREAM)
    except OSError as exc:
        raise EvidenceError(f"cannot resolve source host: {exc}") from exc
    if not addresses:
        raise EvidenceError("source host has no resolved address")
    if not allow_private_network and any(not ipaddress.ip_address(item[4][0]).is_global for item in addresses):
        raise EvidenceError("non-public destination; use the host's authorized local access or explicit --allow-private-network")
    return url


class CheckedRedirect(HTTPRedirectHandler):
    def __init__(self, *, allow_http=False, allow_private_network=False):
        self.options = dict(allow_http=allow_http, allow_private_network=allow_private_network)

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        validate_url(newurl, **self.options)
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def fetch_text(url: str, *, max_source_bytes=MAX_SOURCE_BYTES, timeout=20,
               allow_http=False, allow_private_network=False) -> AcquiredText:
    if type(max_source_bytes) is not int or max_source_bytes < 1:
        raise EvidenceError("max-source-bytes must be a positive integer")
    if not math.isfinite(timeout) or timeout <= 0:
        raise EvidenceError("timeout must be positive")
    options = dict(allow_http=allow_http, allow_private_network=allow_private_network)
    validate_url(url, **options)
    # A proxy inherited from the environment could cross another account/network
    # boundary. This explicit public fetch uses a direct connection.
    opener = build_opener(ProxyHandler({}), CheckedRedirect(**options))
    request = Request(url, headers={"User-Agent": "Soundings-text-acquisition/0.7",
                                    "Accept": "text/html,text/plain,application/json,application/xml;q=0.8",
                                    "Accept-Encoding": "identity"})
    try:
        with opener.open(request, timeout=timeout) as response:
            validate_url(response.geturl(), **options)
            content_type = response.headers.get_content_type()
            if not (content_type.startswith("text/") or content_type in TEXT_TYPES):
                raise EvidenceError("unsupported source type; use the host's document/media reader and capture its labelled text")
            if response.headers.get("Content-Encoding", "identity").lower() not in {"", "identity"}:
                raise EvidenceError("encoded response unsupported; use the host reader or an uncompressed text endpoint")
            body = response.read(max_source_bytes + 1)
            if len(body) > max_source_bytes:
                raise EvidenceError("source exceeds max-source-bytes; nothing captured (use host reading or explicitly raise the limit)")
            charset = response.headers.get_content_charset() or "utf-8"
            try:
                raw_text = body.decode(charset)
            except (LookupError, UnicodeError) as exc:
                raise EvidenceError("source cannot be decoded exactly with its declared charset; nothing captured") from exc
            final_url = response.geturl()
    except (HTTPError, URLError, TimeoutError, OSError) as exc:
        raise EvidenceError(f"source request failed: {exc}") from exc
    if not raw_text.strip():
        raise EvidenceError("source returned empty text; nothing captured")
    title, text, omissions = final_url, raw_text, ()
    if content_type in HTML_TYPES:
        parser = TextExtractor()
        parser.feed(raw_text)
        parser.close()
        text, extracted_title, omissions = parser.result()
        title = extracted_title or final_url
        if not text.strip():
            raise EvidenceError("HTML has no extractable text; use the host browser for this source")
    return AcquiredText(url, final_url, title, content_type, charset, raw_text, text, omissions)


def acquire(root: Path, url: str, *, lead_id=None, max_bytes=8192, **options) -> dict:
    # Import only the adjacent installed helper. A workspace is data, never an
    # import path or an executable acquisition configuration.
    import workspace

    workspace.load_state(root)  # Reject an invalid workspace before networking.
    source = fetch_text(url, **options)
    is_html = source.content_type in HTML_TYPES
    receipt = {"operation": "acquire", "requested_url": source.requested_url,
               "source": source.url, "title": source.title, "content_type": source.content_type,
               "charset": source.charset, "raw_ref": "s-" + "0" * 32,
               "ref": "s-" + "0" * 32,
               "representation": "extracted" if is_html else "verbatim",
               "extraction_omissions": list(source.omissions),
               "limits": "Decoded response retained; HTML extraction does not establish layout, interaction, or complete reading."}
    encode(receipt, max_bytes)  # Reject an impossible receipt before any capture.
    with tempfile.TemporaryDirectory(prefix="soundings-acquire-") as temporary:
        path = Path(temporary) / "response.txt"
        path.write_bytes(source.raw_text.encode("utf-8"))
        raw = workspace.capture_source(root, path, source.url, source.title + (" (HTTP text)" if is_html else ""),
                                       "verbatim", via="direct-http; charset=" + source.charset,
                                       lead_id=lead_id)
        receipt["raw_ref"] = receipt["ref"] = raw["ref"]
        if is_html:
            path.write_bytes(source.text.encode("utf-8"))
            try:
                extracted = workspace.capture_source(root, path, source.url, source.title, "extracted",
                                                     via="html-text-extraction", lead_id=lead_id,
                                                     derived_from=raw["ref"])
            except (EvidenceError, OSError) as exc:
                raise EvidenceError(f"raw source retained as {raw['ref']}; extraction capture failed: {exc}") from exc
            receipt["ref"] = extracted["ref"]
    return receipt


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("url")
    parser.add_argument("--workspace", required=True, type=Path)
    parser.add_argument("--lead", dest="lead_id")
    parser.add_argument("--max-source-bytes", type=int, default=MAX_SOURCE_BYTES)
    parser.add_argument("--timeout", type=float, default=20)
    parser.add_argument("--max-bytes", type=int, default=8192)
    parser.add_argument("--allow-http", action="store_true")
    parser.add_argument("--allow-private-network", action="store_true")
    args = vars(parser.parse_args(argv))
    root, url, max_bytes = args.pop("workspace"), args.pop("url"), args.pop("max_bytes")
    try:
        sys.stdout.buffer.write(encode(acquire(root, url, max_bytes=max_bytes, **args), max_bytes))
    except (EvidenceError, OSError, UnicodeError, ValueError) as exc:
        print(f"acquire: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
