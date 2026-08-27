import json
import sys
from pathlib import Path
from doaa_algorithm_registry import lookup


def retrieve(payload):
    registry_path = payload.get("registry_path")
    proposal = payload.get("proposal")
    if not isinstance(registry_path, str) or not isinstance(proposal, dict):
        return {"status":"retrieval_blocked","reason":"registry_and_proposal_required","execution_authority":"none","automatic_execution":False,"model_call":False}
    result = lookup(Path(registry_path), proposal)
    result["model_call"] = False
    result["execution_authority"] = "none"
    result["automatic_execution"] = False
    return result


def main():
    print(json.dumps(retrieve(json.loads(sys.stdin.read())), ensure_ascii=False, sort_keys=True, separators=(",", ":")))


if __name__ == "__main__":
    main()
