"""Deterministic on-disk response cache for paid model calls."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


class FileResponseCache:
    """Cache one canonical provider response per request hash.

    Cache files are deliberately simple JSON so experiment provenance remains auditable.
    """

    def __init__(self, root: str | Path = ".cache/polis") -> None:
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def key(payload: dict[str, Any]) -> str:
        canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
        return hashlib.sha256(canonical.encode("utf-8")).hexdigest()

    def get(self, payload: dict[str, Any]) -> dict[str, Any] | None:
        path = self.root / f"{self.key(payload)}.json"
        if not path.exists():
            return None
        with path.open("r", encoding="utf-8") as handle:
            data = json.load(handle)
        if not isinstance(data, dict):
            raise ValueError(f"Invalid cache record: {path}")
        return data

    def put(self, payload: dict[str, Any], response: dict[str, Any]) -> Path:
        key = self.key(payload)
        path = self.root / f"{key}.json"
        tmp = path.with_suffix(".tmp")
        record = {"request_sha256": key, "request": payload, "response": response}
        with tmp.open("w", encoding="utf-8") as handle:
            json.dump(record, handle, indent=2, sort_keys=True, ensure_ascii=False)
        tmp.replace(path)
        return path
