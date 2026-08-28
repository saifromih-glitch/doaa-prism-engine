"""Auditable local reuse telemetry for Doaa's local-first policy."""
from __future__ import annotations

from typing import Any

CONTRACT = "doaa.reuse_ledger.v1"


class ReuseLedger:
    """Counts explicit route outcomes; it never selects by semantic similarity."""

    def __init__(self) -> None:
        self._hits = 0
        self._misses = 0
        self._blocked = 0
        self._token_saving = 0

    def observe(self, route_status: Any, baseline_tokens: int | None = None, local_tokens: int | None = None) -> dict[str, Any]:
        if route_status == "route_local_algorithm" or route_status == "route_active_knowledge":
            self._hits += 1
            if isinstance(baseline_tokens, int) and isinstance(local_tokens, int) and baseline_tokens >= 0 and local_tokens >= 0:
                self._token_saving += max(0, baseline_tokens - local_tokens)
            event = "local_hit"
        elif route_status == "route_model_or_review":
            self._misses += 1
            event = "local_miss"
        else:
            self._blocked += 1
            event = "route_blocked"
        return {"status": "reuse_observed", "event": event, "execution_authority": "none", "automatic_execution": False}

    def stats(self) -> dict[str, Any]:
        total = self._hits + self._misses
        return {"status": "reuse_stats_ready", "contract": CONTRACT, "local_hits": self._hits, "local_misses": self._misses, "blocked_routes": self._blocked, "total_attempts": total, "hit_rate": round(self._hits / total, 6) if total else 0.0, "token_saving_observed": self._token_saving, "selection_policy": "exact_local_only", "execution_authority": "none", "automatic_execution": False}
