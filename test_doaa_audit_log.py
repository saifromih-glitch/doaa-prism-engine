import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).parent
AUDIT = ROOT / "doaa_audit_log.py"
request = {"goal":"test","table_schema":[{"name":"phone","type":"text"}],"dsl_version":"1.4"}
gate = {"status":"rejected","reason":"kind_invalid","execution_authority":"none"}
payload = {"audit_path": str(Path(tempfile.gettempdir()) / "doaa-audit-test.jsonl"), "request": request, "raw_model_text":"raw", "repaired_model_text":"repaired", "gate_result": gate, "repair_id": None}
completed = subprocess.run([sys.executable, str(AUDIT)], input=json.dumps(payload), text=True, encoding="utf-8", capture_output=True, check=True)
record = json.loads(completed.stdout)
assert record["schema"] == "DOAA-AUDIT-0001"
assert len(record["raw_response_sha256"]) == 64
assert len(record["repaired_response_sha256"]) == 64
assert len(record["record_sha256"]) == 64
assert record["execution_authority"] == "none"
assert record["dsl_execution"] is False
assert record["external_network_request"] is False
assert record["raw_preserved"] is True
print(json.dumps({"status":"passed","audit_schema":record["schema"],"dsl_execution":False,"external_network_request":False},separators=(",",":")))
