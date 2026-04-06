#!/usr/bin/env python3
"""Minimal incident notifier for Redmine + Bitrix24."""

from __future__ import annotations

import argparse
import os
import sys
from typing import Dict, Any

import requests


REDMINE_BASE_URL = "REDMINE_BASE_URL"
REDMINE_ALERT_TOKEN = "REDMINE_ALERT_TOKEN"
BITRIX_WEBHOOK_URL = "BITRIX_WEBHOOK_URL"
BITRIX_DIALOG_ID = "BITRIX_DIALOG_ID"
VALID_SEVERITIES = {"info", "warning", "critical"}


def parse_bool(value: str) -> bool:
    lowered = value.strip().lower()
    if lowered in {"1", "true", "yes", "y"}:
        return True
    if lowered in {"0", "false", "no", "n"}:
        return False
    raise argparse.ArgumentTypeError("Expected boolean value (true/false)")


def require_env(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        print(f"Missing required environment variable: {name}", file=sys.stderr)
        sys.exit(2)
    return value


def redmine_post(path: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    base_url = require_env(REDMINE_BASE_URL).rstrip("/")
    token = require_env(REDMINE_ALERT_TOKEN)

    url = f"{base_url}{path}"
    headers = {
        "Content-Type": "application/json",
        "X-Service-Alert-Token": token,
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=15)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as exc:
        print(f"Redmine request failed: {exc}", file=sys.stderr)
        sys.exit(1)
    except ValueError:
        print("Redmine returned non-JSON response", file=sys.stderr)
        sys.exit(1)


def bitrix_send(text: str) -> None:
    webhook_url = require_env(BITRIX_WEBHOOK_URL).rstrip("/")
    dialog_id = require_env(BITRIX_DIALOG_ID)
    url = f"{webhook_url}/im.message.add"

    payload = {"DIALOG_ID": dialog_id, "MESSAGE": text}

    try:
        response = requests.post(url, json=payload, timeout=15)
        response.raise_for_status()
        data = response.json()
    except requests.RequestException as exc:
        print(f"Bitrix request failed: {exc}", file=sys.stderr)
        sys.exit(1)
    except ValueError:
        print("Bitrix returned non-JSON response", file=sys.stderr)
        sys.exit(1)

    if "error" in data:
        print(f"Bitrix API error: {data['error']}", file=sys.stderr)
        sys.exit(1)


def cmd_start(args: argparse.Namespace) -> int:
    if args.severity not in VALID_SEVERITIES:
        print(f"Invalid severity: {args.severity}", file=sys.stderr)
        return 2

    payload = {
        "severity": args.severity,
        "title": args.title,
        "message": args.message,
        "link_url": args.link_url or "",
        "show_popup": args.show_popup,
    }

    state = redmine_post("/service_alert/activate", payload)

    chat_message = (
        f"[INCIDENT STARTED] {args.title}\n"
        f"Severity: {args.severity}\n"
        f"{args.message}"
    )
    if args.link_url:
        chat_message += f"\nDetails: {args.link_url}"

    bitrix_send(chat_message)
    print(f"Incident started. Redmine state: enabled={state.get('enabled')} version={state.get('version')}")
    return 0


def cmd_end(args: argparse.Namespace) -> int:
    state = redmine_post("/service_alert/deactivate", {})

    chat_message = f"[INCIDENT RESOLVED] {args.message}"
    bitrix_send(chat_message)
    print(f"Incident ended. Redmine state: enabled={state.get('enabled')} version={state.get('version')}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Incident notifier for Redmine and Bitrix24")
    subparsers = parser.add_subparsers(dest="command", required=True)

    start = subparsers.add_parser("start", help="Activate incident in Redmine and notify Bitrix24")
    start.add_argument("--severity", required=True, choices=sorted(VALID_SEVERITIES))
    start.add_argument("--title", required=True)
    start.add_argument("--message", required=True)
    start.add_argument("--link-url", default="")
    start.add_argument("--show-popup", type=parse_bool, default=False)
    start.set_defaults(func=cmd_start)

    end = subparsers.add_parser("end", help="Deactivate incident in Redmine and notify Bitrix24")
    end.add_argument("--message", required=True)
    end.set_defaults(func=cmd_end)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
