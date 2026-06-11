from __future__ import annotations

import argparse
import json
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any

import httpx

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DATA_FILE = PROJECT_ROOT / "email-data-advanced.json"
DEFAULT_BASE_URL = "http://localhost:8000"
INGEST_PATH = "/api/ingest"
MAX_RETRIES = 3
RETRY_BACKOFF_SECONDS = 1.0


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Replay emails from email-data-advanced.json to POST /api/ingest.",
    )
    parser.add_argument(
        "--speed",
        type=float,
        default=1.0,
        help="Emails per second (e.g. 1 = one email every second, 0 = no delay).",
    )
    parser.add_argument(
        "--base-url",
        default=DEFAULT_BASE_URL,
        help=f"API base URL (default: {DEFAULT_BASE_URL}).",
    )
    parser.add_argument(
        "--data-file",
        type=Path,
        default=DEFAULT_DATA_FILE,
        help=f"Path to email JSON dataset (default: {DEFAULT_DATA_FILE.name}).",
    )
    return parser.parse_args(argv)


def load_emails(data_file: Path) -> list[dict[str, Any]]:
    if not data_file.exists():
        raise FileNotFoundError(f"Dataset not found: {data_file}")

    with data_file.open(encoding="utf-8") as handle:
        emails = json.load(handle)

    if not isinstance(emails, list):
        raise ValueError("Dataset must be a JSON array of email objects")

    for index, email in enumerate(emails, start=1):
        if not isinstance(email, dict):
            raise ValueError(f"Email at index {index - 1} is not a JSON object")

    return sorted(emails, key=lambda email: email["timestamp"])


def parse_timestamp(value: str) -> datetime:
    if value.endswith("Z"):
        value = f"{value[:-1]}+00:00"
    return datetime.fromisoformat(value)


def build_payload(email: dict[str, Any]) -> dict[str, Any]:
    return {
        "message_id": email["message_id"],
        "thread_id": email["thread_id"],
        "sender": email["sender"],
        "subject": email["subject"],
        "body": email["body"],
        "timestamp": parse_timestamp(email["timestamp"]).isoformat(),
    }


def post_with_retries(
    client: httpx.Client,
    url: str,
    payload: dict[str, Any],
) -> httpx.Response:
    last_error: Exception | None = None

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = client.post(url, json=payload, timeout=30.0)
            if response.status_code >= 500 and attempt < MAX_RETRIES:
                time.sleep(RETRY_BACKOFF_SECONDS * attempt)
                continue
            return response
        except (httpx.RequestError, httpx.TimeoutException) as exc:
            last_error = exc
            if attempt < MAX_RETRIES:
                time.sleep(RETRY_BACKOFF_SECONDS * attempt)
                continue
            raise

    if last_error is not None:
        raise last_error

    raise RuntimeError("Failed to post email after retries")


def format_error_detail(response: httpx.Response) -> str:
    try:
        body = response.json()
    except json.JSONDecodeError:
        return response.text or f"HTTP {response.status_code}"

    if isinstance(body, dict):
        detail = body.get("detail")
        if isinstance(detail, dict):
            return detail.get("message", str(detail))
        if detail is not None:
            return str(detail)

    return str(body)


def replay_emails(
    emails: list[dict[str, Any]],
    *,
    base_url: str,
    speed: float,
) -> int:
    ingest_url = f"{base_url.rstrip('/')}{INGEST_PATH}"
    delay_seconds = 1.0 / speed if speed > 0 else 0.0
    total = len(emails)
    failures = 0

    print(f"Replaying {total} emails to {ingest_url} at {speed or 'unlimited'} emails/sec")

    with httpx.Client() as client:
        for index, email in enumerate(emails, start=1):
            message_id = email["message_id"]
            prefix = f"[{index}/{total}] {message_id}"

            try:
                response = post_with_retries(
                    client,
                    ingest_url,
                    build_payload(email),
                )
            except (httpx.RequestError, httpx.TimeoutException) as exc:
                failures += 1
                print(f"{prefix} network error: {exc}")
            else:
                if response.status_code == 202:
                    print(f"{prefix} ingested")
                elif response.status_code == 409:
                    print(f"{prefix} duplicate (skipped)")
                else:
                    failures += 1
                    print(f"{prefix} failed: {format_error_detail(response)}")

            if index < total and delay_seconds > 0:
                time.sleep(delay_seconds)

    print(f"Replay complete: {total - failures}/{total} succeeded, {failures} failed")
    return failures


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)

    if args.speed < 0:
        print("Error: --speed must be zero or positive.", file=sys.stderr)
        return 1

    try:
        emails = load_emails(args.data_file)
    except (FileNotFoundError, ValueError, json.JSONDecodeError, KeyError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    failures = replay_emails(
        emails,
        base_url=args.base_url,
        speed=args.speed,
    )
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
