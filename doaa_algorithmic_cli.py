"""One-shot local CLI for algorithmic mediation; no model call and no execution."""
from __future__ import annotations

import argparse
import json
import sys

from doaa_algorithmic_mediator import mediate


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run local Doaa mediation validation; no model call and no execution."
    )
    parser.add_argument("--pretty", action="store_true", help="Print indented JSON output.")
    parser.add_argument("--version", action="version", version="doaa.alg.v1 cli")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    if hasattr(sys.stdin, "reconfigure"):
        sys.stdin.reconfigure(encoding="utf-8")
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    try:
        payload = json.loads(sys.stdin.read())
        if not isinstance(payload, dict) or set(payload) != {"request", "raw_model_result"}:
            raise ValueError("envelope_schema_invalid")
        output = mediate(payload["request"], payload["raw_model_result"])
    except (json.JSONDecodeError, ValueError, TypeError) as exc:
        output = {"status": "mediation_blocked", "reason": str(exc), "execution_authority": "none", "automatic_execution": False}
    print(json.dumps(
        output,
        ensure_ascii=False,
        sort_keys=True,
        indent=2 if args.pretty else None,
        separators=None if args.pretty else (",", ":"),
    ))


if __name__ == "__main__":
    main()
