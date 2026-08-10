#!/usr/bin/env python3
"""Export the complete generated POLIS v2 design before protocol freeze."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from polis.v2.protocol import load_protocol
from polis.v2.scenarios import canonical_design_payload, design_digest


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="results/v2/design_manifest.json")
    args = parser.parse_args()
    protocol = load_protocol()
    payload = {
        "protocol_version": protocol.protocol_version,
        "protocol_status": protocol.status,
        "config_digest": protocol.config_digest(),
        "design_digest": design_digest(),
        "study_fingerprint": protocol.study_fingerprint(),
        "design": canonical_design_payload(),
    }
    path = Path(args.output)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({key: value for key, value in payload.items() if key != "design"}, indent=2))


if __name__ == "__main__":
    main()
