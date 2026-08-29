from __future__ import annotations
import hashlib, json
from pathlib import Path
from typing import Any


def normalize(text: str) -> str:
    return " ".join(text.replace("ـ", "").split())


def cache_key(context: str, question: str, algorithm_version: str = "v1") -> str:
    raw = "|".join([normalize(context), normalize(question), algorithm_version])
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


class RouteCache:
    def __init__(self, path: str):
        self.path = Path(path)
        self.data = json.loads(self.path.read_text(encoding="utf-8")) if self.path.exists() else {}

    def get(self, context: str, question: str, algorithm_version: str = "v1") -> Any:
        return self.data.get(cache_key(context, question, algorithm_version))

    def put(self, context: str, question: str, result: Any, algorithm_version: str = "v1") -> str:
        key = cache_key(context, question, algorithm_version)
        self.data[key] = result
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(self.data, ensure_ascii=False, indent=2), encoding="utf-8")
        return key
