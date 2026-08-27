"""One-shot local CLI for algorithmic mediation; no model call and no execution."""
from __future__ import annotations

import json
import sys

from doaa_algorithmic_mediator import mediate


def main() -> None:
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
    print(json.dumps(output, ensure_ascii=False, sort_keys=True, separators=(",", ":")))


if __name__ == "__main__":
    main()
