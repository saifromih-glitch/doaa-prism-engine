import json
import sys
from pathlib import Path
from doaa_deterministic_retrieval import retrieve


def route(payload):
    result = retrieve({"registry_path": payload.get("registry_path"), "proposal": payload.get("proposal")})
    if result.get("status") == "cache_hit":
        return {"status":"reuse_candidate","route":"reuse_candidate","model_call":False,"automatic_execution":False,"execution_authority":"none","retrieval":result}
    if result.get("status") == "cache_miss":
        return {"status":"model_stage_required","route":"governed_model_stage","model_call":True,"automatic_execution":False,"execution_authority":"none","retrieval":result}
    return {"status":"router_blocked","route":"blocked","model_call":False,"automatic_execution":False,"execution_authority":"none","retrieval":result}


def main():
    try:
        payload = json.loads(sys.stdin.read())
        print(json.dumps(route(payload), ensure_ascii=False, sort_keys=True, separators=(",", ":")))
    except Exception:
        print(json.dumps({"status":"router_blocked","route":"blocked","model_call":False,"automatic_execution":False,"execution_authority":"none"}, separators=(",", ":")))
        raise SystemExit(0)

if __name__ == "__main__": main()
