#!/usr/bin/env python3
"""Validate AI HOT X/QT draft cards without external dependencies."""

from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
from datetime import datetime
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

URL_RE = re.compile(r"https?://[^\s<>]+")
X_STATUS_RE = re.compile(r"^https://(?:www\.)?(?:x\.com|twitter\.com)/[^/]+/status/\d+(?:[/?#].*)?$")
AIHOT_RE = re.compile(r"^https://aihot\.virxact\.com/(?:items|daily)/[^\s]+$")


def weighted_length(text: str) -> int:
    """Conservative X length: ASCII=1, other code points=2, every URL=23."""
    normalized = unicodedata.normalize("NFC", text)
    total = 0
    cursor = 0
    for match in URL_RE.finditer(normalized):
        total += sum(1 if ord(char) < 128 else 2 for char in normalized[cursor : match.start()])
        total += 23
        cursor = match.end()
    total += sum(1 if ord(char) < 128 else 2 for char in normalized[cursor:])
    return total


def valid_http_url(value: Any) -> bool:
    if not isinstance(value, str):
        return False
    parsed = urlparse(value)
    return parsed.scheme == "https" and bool(parsed.netloc)


def valid_timestamp(value: Any) -> bool:
    if not isinstance(value, str) or not value:
        return False
    try:
        datetime.fromisoformat(value.replace("Z", "+00:00"))
        return True
    except ValueError:
        return False


def validate_draft(draft: Any, index: int) -> dict[str, Any]:
    errors: list[str] = []
    if not isinstance(draft, dict):
        return {"index": index, "ok": False, "errors": ["draft must be an object"]}

    kind = draft.get("type")
    text = draft.get("text")
    source_url = draft.get("sourceUrl")
    canonical = draft.get("aihotCanonical")
    published_at = draft.get("publishedAt")
    reason = draft.get("selectionReason")

    if kind not in {"qt", "link"}:
        errors.append("type must be 'qt' or 'link'")
    if not isinstance(text, str) or not text.strip():
        errors.append("text must be non-empty")
        text = ""
    if not valid_http_url(source_url):
        errors.append("sourceUrl must be an HTTPS URL")
    if not isinstance(canonical, str) or not AIHOT_RE.match(canonical):
        errors.append("aihotCanonical must be an AI HOT item or daily URL")
    if not valid_timestamp(published_at):
        errors.append("publishedAt must be ISO 8601")
    if not isinstance(reason, str) or not reason.strip():
        errors.append("selectionReason must be non-empty")

    length = weighted_length(text)
    body_length: int | None = None
    if kind == "qt":
        if not isinstance(source_url, str) or not X_STATUS_RE.match(source_url):
            errors.append("qt sourceUrl must be an X/Twitter status URL")
        if length > 260:
            errors.append(f"qt text exceeds 260 weighted characters ({length})")
    elif kind == "link":
        if isinstance(source_url, str) and X_STATUS_RE.match(source_url):
            errors.append("link sourceUrl must not be an X/Twitter status URL")
        if isinstance(source_url, str) and source_url not in text:
            errors.append("link text must include sourceUrl")
        body = text.replace(source_url, "", 1).strip() if isinstance(source_url, str) else text
        body_length = weighted_length(body)
        if body_length > 230:
            errors.append(f"link body exceeds 230 weighted characters ({body_length})")
        if length > 280:
            errors.append(f"link post exceeds 280 weighted characters ({length})")

    return {
        "index": index,
        "type": kind,
        "ok": not errors,
        "weightedLength": length,
        "bodyWeightedLength": body_length,
        "errors": errors,
    }


def validate_payload(payload: Any) -> dict[str, Any]:
    if not isinstance(payload, dict) or not isinstance(payload.get("drafts"), list):
        return {"ok": False, "draftCount": 0, "results": [], "errors": ["root.drafts must be a list"]}
    drafts = payload["drafts"]
    results = [validate_draft(draft, index) for index, draft in enumerate(drafts, start=1)]
    root_errors: list[str] = []
    if len(drafts) > 5:
        root_errors.append("at most 5 drafts are allowed")
    return {
        "ok": not root_errors and all(result["ok"] for result in results),
        "draftCount": len(drafts),
        "results": results,
        "errors": root_errors,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", nargs="?", help="JSON file; omit to read stdin")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        raw = Path(args.path).read_text(encoding="utf-8") if args.path else sys.stdin.read()
        payload = json.loads(raw)
    except (OSError, json.JSONDecodeError) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False))
        return 1
    result = validate_payload(payload)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

